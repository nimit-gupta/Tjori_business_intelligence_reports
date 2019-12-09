#!/usr/bin/env python
# coding: utf-8

# In[1]:


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

os.remove(r'C://Users//sachi//OneDrive//Desktop//Daily_Pending_Payment_List.xlsx')


conn = ps.connect(
                   user = 'nimit_new', 
                   password = 'nimit@tjori@123', 
                   host = '103.93.94.51', port = '5432', 
                   database = 'tjori_pd')

def pending_payment_list(st,et):
    sql = '''
             SELECT
                  created::TIMESTAMP::date  AS order_created 
		         ,CASE 
		             WHEN payment_method = '1' THEN 'Paytm'
			         WHEN payment_method = '2' THEN 'PayU'
			         WHEN payment_method = '4' THEN 'PayPal'
			         WHEN payment_method = '10' THEN 'Mobiqwik'
		          END AS payment_method 
                 ,invoice_id AS order_invoice_id 
                 ,status AS order_status
            FROM
                 order_order
            WHERE
                 created >= '%s' AND created < '%s'
                 AND email NOT LIKE '%%@tjori.com%%'
                 AND status SIMILAR TO 'pending-payment'
                 AND payment_method IN ('1','2','4','10')
            ORDER BY
                 order_created asc
             ;
             ''' %  ( 
                      st,
                      et
                    )
    df = pd.read_sql_query(sql, conn)
    return df
    
if __name__ == '__main__':
     td = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
     yd = (datetime.datetime.now() - datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')

df = pending_payment_list(yd,td)

pivot = pd.pivot_table(df, values = 'order_invoice_id', index = 'payment_method', columns = 'order_status', aggfunc = 'count',margins = True, margins_name = 'Total')

def write_to_excel():
    writer = pd.ExcelWriter('C://Users//sachi//OneDrive//Desktop//Daily_Pending_Payment_List.xlsx', engine='xlsxwriter')
    pivot.to_excel(writer, sheet_name  = 'Daily_Pending_Payment_Report')
    df.to_excel(writer, sheet_name = 'Daily_Pending_Payment_List')
    writer.save()
    
def send_email():
    sender = "nimit@tjori.com"
    recievers = ["nimit@tjori.com",
                 "farhan@tjori.com",
                 "shiv@tjori.com",
                 "farhan18khan.1995@gmail.com"
                 
                ]
    # Create message container 
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Daily Pending Payment Report"
    msg['From'] = sender
    msg['To'] = ",".join(recievers)

    # instance of MIMEBase and named as part
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("C:/Users/sachi/OneDrive/Desktop/Daily_Pending_Payment_List.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Daily_Pending_Payment_List.xlsx"')
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




