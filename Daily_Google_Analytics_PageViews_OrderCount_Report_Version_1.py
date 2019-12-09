#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psycopg2 as pg
import pandas as pd 
import numpy as np
import datetime
import xlsxwriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
import os

pd.options.display.float_format = '{0:,.0f}'.format

os.remove(r'C://Users//sachi//OneDrive//Desktop//Google_Analytics_Pageviews_List.xlsx')

#Connecting to the database

conn = pg.connect( user = 'doadmin', 
                   password = 'xpmt05ij9uf9rknn', 
                   host = 'tjori-bi-do-user-6486966-0.db.ondigitalocean.com', 
                   port = '25060', 
                   database = 'defaultdb')

#Writing the postgreSQL query to retrieve the data

def google_analytics_page_views(start_date, end_date):
    
    sql_1 = '''
             select 
                  date::timestamp::date
	             ,page_path
	             ,product_id
                 ,sp.sku
	             ,sc.name
	             ,sum(page_views) as page_views
	             ,sum(unique_page_views) as unique_page_views
             from 
                 ga_union_pageviews as ga
             left join
                 store_product as sp on ga.product_id = sp.id
             left join
                 store_category as sc on sp.category_id = sc.id
             where
                 date >= '%s' and date < '%s'
             group by
                 date
	            ,page_path
	            ,product_id
                ,sp.sku
	            ,sc.name
             order by
                date asc
         ;''' % (
                  start_date,
                  end_date
                )
    df_1 = pd.read_sql_query(sql_1, conn)
    return df_1

def order_order(start_date, end_date):
    
    sql_2 = '''
              select 
                   soi.created::timestamp::date
	              ,sp.sku
	              ,sum(soi.quanity) as quanity
              from 
                  order_order as so
              left join
                  order_orderproduct as soi on so.id = soi.order_id
              left join 
                  store_product as sp on soi.product_id = sp.id
              where 
                  soi.created >= '%s' and soi.created < '%s'
	              and so.status = 'confirmed'
	              and so.email not like '%%@tjori.com%%'
              group by 
                  soi.created
	             ,sp.sku
              order by
                  soi.created asc

	 
         ;''' % (
                  start_date,
                  end_date
                )
    df_2 = pd.read_sql_query(sql_2, conn)
    return df_2



def google_analytics_page_views_clearance(start_date, end_date):
    
    sql_3 = '''
             select 
                  date::timestamp::date
	             ,page_path
	             ,product_id
                 ,sp.sku
	             ,sc.name
	             ,sum(page_views) as page_views
	             ,sum(unique_page_views) as unique_page_views
             from 
                 ga_union_pageviews as ga
             left join
                 store_product as sp on ga.product_id = sp.id
             left join
                 store_category as sc on sp.category_id = sc.id
             where
                 date >= '%s' and date < '%s'
                 and sp.ribbon_id = 3
             group by
                 date
	            ,page_path
	            ,product_id
                ,sp.sku
	            ,sc.name
             order by
                date asc
         ;''' % (
                  start_date,
                  end_date
                )
    df_3 = pd.read_sql_query(sql_3, conn)
    return df_3

def order_order_clearance(start_date, end_date):
    
    sql_4 = '''
              select 
                   soi.created::timestamp::date
	              ,sp.sku
	              ,sum(soi.quanity) as quanity
              from 
                  order_order as so
              left join
                  order_orderproduct as soi on so.id = soi.order_id
              left join 
                  store_product as sp on soi.product_id = sp.id
              where 
                  soi.created >= '%s' and soi.created < '%s'
	              and so.status = 'confirmed'
	              and so.email not like '%%@tjori.com%%'
                  and sp.ribbon_id = 3
              group by 
                  soi.created
	             ,sp.sku
              order by
                  soi.created asc

	 
         ;''' % (
                  start_date,
                  end_date
                )
    df_4 = pd.read_sql_query(sql_4, conn)
    return df_4


if __name__ == '__main__':
        td = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
        yd = (datetime.datetime.now() - datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
        fd = (datetime.datetime.now() - datetime.timedelta(1)).replace(day=1,hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
        ydb = (datetime.datetime.now() - datetime.timedelta(2)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')

df_1 = google_analytics_page_views(fd, td)
df_2 = order_order(fd, td)
df_3 = google_analytics_page_views_clearance(fd, td)
df_4 = order_order_clearance(fd, td)


pivot_1 = pd.pivot_table(df_1, values = 'unique_page_views', index = 'sku', columns = 'date', aggfunc = np.sum, margins = True, margins_name = 'Total')
pivot_2 = pd.pivot_table(df_2, values = 'quanity', index = 'sku', columns = 'created', aggfunc = np.sum, margins = True, margins_name = 'Total')
pivot_3 = pd.pivot_table(df_3, values = 'unique_page_views', index = 'sku', columns = 'date', aggfunc = np.sum, margins = True, margins_name = 'Total')
pivot_4 = pd.pivot_table(df_4, values = 'quanity', index = 'sku', columns = 'created', aggfunc = np.sum, margins = True, margins_name = 'Total')

all_data_1 = pd.merge(pivot_1, pivot_2, on = 'sku', how = 'left', suffixes = ('_pageviews','_quanity'))
all_data_2 = pd.merge(pivot_3, pivot_4, on = 'sku', how = 'left', suffixes = ('_pageviews','_quanity'))


def write_to_excel():
    writer = pd.ExcelWriter('C://Users//sachi//OneDrive//Desktop//Google_Analytics_Pageviews_List.xlsx', engine='xlsxwriter')
    all_data_1.to_excel(writer, sheet_name = 'PageviewsOrderReport')
    all_data_2.to_excel(writer, sheet_name = 'PageviewsClearanceOrderReport')
    writer.save()
    
   
def send_email():
    sender = "nimit@tjori.com"
    recievers = ["nimit@tjori.com",
                 "ankit@tjori.com",
                 "mansi@tjori.com",
                 "mkindra@tjori.com",
                 "poonam@tjori.com",
                 "pavitra@tjori.com",
                 "shubhangi@tjori.com",
                 "shruti@tjori.com",
                 "sabhyata@tjori.com",
                 "akanksha@tjori.com",
                 "geetika@tjori.com",
                 "nikita@tjori.com",
                 "hanisha@tjori.com",
                 "samira@tjori.com",
                 "harshit@tjori.com",
                 "aditi@tjori.com",
                 "shiv@tjori.com"
                ]
    # Create message container 
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Daily Google Analytics Pageviews Report"
    msg['From'] = sender
    msg['To'] = ",".join(recievers)

    # instance of MIMEBase and named as part
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("C:/Users/sachi/OneDrive/Desktop/Google_Analytics_Pageviews_List.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Google_Analytics_Pageviews_List.xlsx"')
    msg.attach(part)

    # creates SMTP session 
    
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login('nimit@tjori.com', 's/987456321/G')
    mail.sendmail(sender, recievers, msg.as_string())
    mail.quit()
    
 
def main():
    while True:
        write_to_excel()
        send_email()
        break

if __name__ == '__main__':
    main()
       


# In[ ]:





# In[ ]:




