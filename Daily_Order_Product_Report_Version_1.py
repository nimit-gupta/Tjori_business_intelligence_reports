#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psycopg2 as ps
import pandas as pd
import datetime
import xlsxwriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
import os

os.remove(r'C://Users//sachi//OneDrive//Desktop//Daily_Order_Product_List.xlsx')

conn = ps.connect(
                   user = 'nimit_new', 
                   password = 'nimit@tjori@123', 
                   host = '103.93.94.51', port = '5432', 
                   database = 'tjori_pd')

def daily_order_product_list(start_date, end_date):
    sql = '''
          SELECT
      so.invoice_id AS invoice_id
     ,so.created::timestamp::date AS created
     ,so.status AS status
     ,CASE WHEN so.payment_method = '1' THEN 'Paytm'
           WHEN so.payment_method = '2' THEN 'PayU'
			  WHEN so.payment_method = '3' THEN 'Cash on Delivery' 
           WHEN so.payment_method = '4' THEN 'PayPal' 
           WHEN so.payment_method = '10'THEN 'Mobiqwik' END AS payment_methods
     ,so.email AS customer_email
     ,so.first_name AS customer_first_name
     ,so.last_name AS customer_last_name
     ,so.phone AS customer_phone_number
     ,sp.id AS product_id
     ,sp.sku AS product_sku
     ,sp.name AS product_name
     ,soi.quanity AS product_quanity
     ,soi.size AS product_size
     ,so.address_line1 AS address
     ,so.postal_code
     ,so.city AS city
     ,so.country AS country
     ,so.base_amount AS base_amount
     ,so.total_amount AS total_amount
     ,so.shipping_amount AS shipping_amount
     ,so.discount_amount AS discount_amount
     ,soi.price AS sold_at
     ,sp.price AS current_product_price 
     ,sp.special_price AS current_product_special_price
     ,soi.removed AS removed
     ,so.currency AS order_currency
     ,sc.name AS category
     ,string_agg( distinct concat(os.way_bill_number),'  ,') AS way_bill_number
     ,sp.cost_price
     ,soi.in_process AS in_process
     ,hsn.tax
     ,hsn.tax_under999
     ,hsn.code
     ,soi.delivered AS delivered
     ,soi.exchanged AS exchanged
FROM
    order_order AS so
LEFT JOIN 
    order_orderproduct AS soi ON so.id = soi.order_id
LEFT JOIN
    store_product AS sp ON soi.product_id = sp.id
LEFT JOIN
    store_category AS sc ON sp.category_id = sc.id
LEFT JOIN
    order_shipment AS os ON so.id = os.order_id
LEFT JOIN 
   tms_hsncode AS hsn ON sp.hsncode_id = hsn.id
   
WHERE
    so.created >= '%s'
    AND so.created < '%s'
    AND so.status = 'confirmed'
GROUP BY
      so.invoice_id 
     ,so.created 
     ,so.status 
     ,payment_methods
     ,so.email 
     ,so.first_name 
     ,so.last_name 
     ,so.phone 
     ,sp.id 
     ,sp.sku 
     ,sp.name 
     ,soi.quanity 
     ,soi.size 
     ,so.address_line1 
     ,so.postal_code
     ,so.city 
     ,so.country 
     ,so.base_amount 
     ,so.total_amount 
     ,so.shipping_amount 
     ,so.discount_amount 
     ,soi.price 
     ,sp.price  
     ,sp.special_price 
     ,soi.removed 
     ,so.currency
     ,sc.name 
     ,sp.cost_price
     ,soi.in_process 
     ,hsn.tax
     ,hsn.tax_under999
     ,hsn.code
     ,soi.delivered 
     ,soi.exchanged 
ORDER BY
     so.created asc
    
;
''' % (
     start_date
     ,end_date
     )
    
    return pd.read_sql_query(sql, conn)

if __name__=='__main__':
    td = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    yd = (datetime.datetime.now() - datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    fd = (datetime.datetime.now() - datetime.timedelta(1)).replace(day=1,hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    ydb = (datetime.datetime.now() - datetime.timedelta(2)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')


df = daily_order_product_list(fd,td)
display(df)

def write_to_excel():
    writer = pd.ExcelWriter('C://Users//sachi//OneDrive//Desktop//Daily_Order_Product_List.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name = 'Daily_Order_Product_List')
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
                 "farhan@tjori.com",
                 "hemant@tjori.com",
                 "accounts@tjori.com",
                 "shiv@tjori.com"
                 ]
    # Create message container 
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Daily Order Product Report"
    msg['From'] = sender
    msg['To'] = ",".join(recievers)

    # instance of MIMEBase and named as part
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("C:/Users/sachi/OneDrive/Desktop/Daily_Order_Product_List.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Daily_Order_Product_List.xlsx"')
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




