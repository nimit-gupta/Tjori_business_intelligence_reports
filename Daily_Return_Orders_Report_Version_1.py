#!/usr/bin/env python
# coding: utf-8

# In[13]:


import psycopg2 as ps
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

conn = ps.connect(
                   user = 'nimit_new', 
                   password = 'nimit@tjori@123', 
                   host = '103.93.94.51', port = '5432', 
                   database = 'tjori_pd')

def return_orders(sd, ed):
    sql = '''
               SELECT 
                     os.created::TIMESTAMP::date AS return_request_date
                    ,so.created::TIMESTAMP::date AS order_create_date
                    ,so.invoice_id
               FROM 
                     order_order AS so
               LEFT JOIN 
                     order_shipment AS os ON (so.id = os.order_id)
               WHERE 
                     os.created >= '%s' AND os.created < '%s'
                     AND os.return_shipment = True
                     
         ;'''% (
                 sd
                ,ed
               )
    return pd.read_sql_query(sql,conn)

def exchange_orders(sd, ed):
    sql = '''
              SELECT 
                 so.created::TIMESTAMP::DATE AS exchange_request_date
                ,so.invoice_id AS exchange_order_invoice_id
                ,a.socreated AS parent_order_date
                ,a.so_invoice_id AS parent_order_invoice_id
              FROM 
                order_order AS so
             LEFT JOIN 
                   (
                     SELECT 
                        so.created::TIMESTAMP::DATE AS socreated
                       ,so.invoice_id AS so_invoice_id
                       ,so.phone AS sophone
                     FROM 
                        order_order AS so
                   ) AS a ON (a.so_invoice_id = so.parent_order) 
            WHERE 
                so.created >= '%s' AND so.created < TIMESTAMP '%s'
                AND so.coupon LIKE '%%ex\_%%'
                AND so.status NOT IN ('cancelled','Cancelled','cancelled-by-cs','Cancelled by Tjori','different-order-confirmed')

        ;'''% (
                sd,
                ed
              )
    return pd.read_sql_query(sql, conn)

def order_shipped(sd, ed):
    sql = '''
             SELECT 
                   order_id as os_order_id
             FROM 
                 order_shipment
             WHERE 
                 created >= '%s' AND created < '%s'
                 and email not like '%%@tjori.com%%'
                 and return_shipment = FALSE
;
            
          ;'''%(
                 sd
                ,ed
               )
    return pd.read_sql_query(sql,conn)

if __name__ == '__main__':
     td = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
     yd = (datetime.datetime.now() - datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')

df = return_orders(yd,td)

df_1 = exchange_orders(yd,td)

df_2 = order_shipped(yd, td)

df = df[~df.invoice_id.isin(df_1.parent_order_invoice_id.values)]

dfcal = ((df['invoice_id'].count() + df_1['exchange_order_invoice_id'].count())/df_2['os_order_id'].count())*100

dfcal = pd.DataFrame([dfcal])

dfes = pd.DataFrame({'Total': [df['invoice_id'].count(), df_1['exchange_order_invoice_id'].count(), df_2['os_order_id'].count(), dfcal.to_string(index = False, header = False)]}, index = ['Total returned', 'Total exchanged', 'Total Orders Shipped', 'Return percentage'])

def write_to_excel():
    writer = pd.ExcelWriter('C://Users//sachi//OneDrive//Desktop//Daily_Return_Report.xlsx', engine='xlsxwriter')
    dfes.to_excel(writer, float_format = '%.2f', sheet_name = 'Executive Summary')
    df.to_excel(writer, sheet_name  = 'Return_Orders')
    df_1.to_excel(writer, sheet_name = 'Exchange_Orders')
    writer.save()
    
def send_email():
    sender = "nimit@tjori.com"
    recievers = [
                   "nimit@tjori.com"
                  ,"farhan@tjori.com"
                  ,"neeraj@tjori.com"
                ]
    # Create message container 
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Daily Return Report"
    msg['From'] = sender
    msg['To'] = ",".join(recievers)

    # instance of MIMEBase and named as part
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("C:/Users/sachi/OneDrive/Desktop/Daily_Return_Report.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Daily_Return_Report.xlsx"')
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




