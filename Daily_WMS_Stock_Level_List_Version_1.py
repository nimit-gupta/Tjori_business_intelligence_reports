#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Importing Python Libaries

import psycopg2 as pg
import pandas as pd 
import numpy as np
import xlsxwriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
import datetime
import os

os.remove(r'C://Users//sachi//OneDrive//Desktop/WMS_Stock_Level.xlsx')

#Connecting to the database

conn = pg.connect( user = 'doadmin', 
                   password = 'xpmt05ij9uf9rknn', 
                   host = 'tjori-bi-do-user-6486966-0.db.ondigitalocean.com', 
                   port = '25060', 
                   database = 'defaultdb')

#Defining a function, in which quering the data using SQL

def wms_stock_level():
    sql = '''SELECT 
                b.category AS category
               ,b.sku AS product_sku
               ,b.size AS product_size
			   ,CASE
			        WHEN sp.ribbon_id = 3 THEN 'Clearance' ELSE 'Non-Clearance' END AS clearance_status
			   ,COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS inward_stock
               ,COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS outward_stock
               ,COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS current_stock_level
               ,coalesce(sp.special_price,0) AS special_price
               ,((COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata')) * (coalesce(sp.special_price,0))) AS current_stock_valuation
               ,b.marketplace_reservation as market_place_reserved_stock
            FROM 
               inventory_skubin a
               LEFT JOIN inventory_skuean b ON a.sku_id = b.id
               LEFT JOIN store_product AS sp ON b.sku = sp.sku
			WHERE
			   b.sku IS NOT NULL
            GROUP BY
               b.category
              ,b.sku
              ,b.size
			  ,clearance_status
              ,sp.special_price
              ,b.marketplace_reservation
			HAVING 
			  COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') > 0 
			ORDER BY
              current_stock_level DESC
			;
'''
    return pd.read_sql_query(sql,conn)


#Calling a function, and store the query output in a temporary variable

df = wms_stock_level()

pivot = pd.pivot_table(df[df['clearance_status'] == 'Clearance'], index = ['category','product_sku'], values = ['current_stock_level', 'current_stock_valuation'], aggfunc = np.sum, margins = True, margins_name = 'Total')

pivot_1 = pd.pivot_table(df[df['clearance_status'] == 'Non-Clearance'], index = ['category','product_sku'], values = ['current_stock_level', 'current_stock_valuation'], aggfunc = np.sum, margins = True, margins_name = 'Total')

pivot_2 = pd.pivot_table(df, index = ['category','product_sku'], values = ['current_stock_level', 'current_stock_valuation'], aggfunc = np.sum, margins = True, margins_name = 'Total')

def write_to_excel():
    writer = pd.ExcelWriter('C://Users//sachi//OneDrive//Desktop//WMS_Stock_Level.xlsx', engine='xlsxwriter')
    df.to_excel(writer,sheet_name='WMS_Stock') 
    pivot.to_excel(writer, sheet_name='Clearance_WMS_Stock_Status')
    pivot_1.to_excel(writer, sheet_name='Non-Clearance_WMS_Stock_Status')
    pivot_2.to_excel(writer, sheet_name='Total_WMS_Stock_Status')
    writer.save()
    
def send_email():
    sender = "nimit@tjori.com"
    
    recievers = ["nimit@tjori.com",
                 "ankit@tjori.com",
                 "mansi@tjori.com",
                 "poonam@tjori.com",
                 "mkindra@tjori.com",
                 "pavitra@tjori.com",
                 "shubhangi@tjori.com",
                 "shruti@tjori.com",
                 "sabhyata@tjori.com",
                 "akanksha@tjori.com",
                 "geetika@tjori.com",
                 "nikita@tjori.com",
                 "harshit@tjori.com",
                 "aditi@tjori.com",
                 "hemant@tjori.com",
                 "shiv@tjori.com"
                ]

    # Create message container 
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Daily Warehouse Stock List"
    msg['From'] = sender
    msg['To'] = ",".join(recievers)

    # instance of MIMEBase and named as part
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("C:/Users/sachi/OneDrive/Desktop/WMS_Stock_Level.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="WMS_Stock_Level.xlsx"')
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




