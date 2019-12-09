#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psycopg2 as ps
import pandas as pd
import xlsxwriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
import os

os.remove(r'C://Users//sachi//OneDrive//Desktop//Daily_Active_Product_List.xlsx')

conn = ps.connect(
                   user = 'nimit_new', 
                   password = 'nimit@tjori@123', 
                   host = '103.93.94.51', port = '5432', 
                   database = 'tjori_pd')

def daily_active_product_list():
    sql = '''
            SELECT
                 sp.created::TIMESTAMP::DATE 
                ,sp.id AS product_id
                ,sp.sku
                ,coalesce(sc.name,'No Category') AS category
                ,sp.active
                ,sp.name 
                ,string_agg (distinct concat(ssc.name), ',') AS subcategory
                ,string_agg (distinct concat(spsc.subcategory_id), ',') AS subcategory_id
                ,sp.description
                ,sp.short_description
                ,sp.visibility
                ,coalesce(sp.ribbon_id, 0) AS ribbon_id
                ,sp.popularity_sequence
                ,round(sp.price,2) AS price
                ,round(sp.special_price,2) AS special_price
                ,round(sp.price_usd, 2) AS price_usd
                ,round(coalesce(sp.cost_price,0),2) AS cost_price
                ,coalesce(cast(hsn.tax as INTEGER),0) AS tax
                ,coalesce(cast(hsn.tax_under999 AS INTEGER), 0) AS tax_under999
                ,coalesce(cast(hsn.code AS INTEGER), 0) AS hsn_code
                ,coalesce(spa.value, 'No Size') AS size
                ,coalesce(spa.actual_stock, 0) AS actual_stock
	            ,coalesce(spa.virtual_stock, 0) AS virtual_stock
                ,coalesce(spa.stock, 0) AS total_stock
            FROM
                store_product AS sp
            LEFT JOIN 
                store_productattribute AS spa ON sp.id = spa.product_id
            LEFT JOIN
                store_category AS sc ON sp.category_id = sc.id
            LEFT JOIN
                store_product_subcategories AS spsc ON sp.id = spsc.product_id
            LEFT JOIN
                store_subcategory AS ssc ON sc.id = ssc.id
            LEFT JOIN
                tms_hsncode AS hsn ON sp.hsncode_id = hsn.id
            WHERE
                sp.active = TRUE 
            GROUP BY
                sp.sku
               ,sp.popularity_sequence
               ,sp.name
               ,sp.active
               ,sp.id
               ,sc.name
               ,ssc.name
               ,hsn.tax
               ,hsn.tax_under999
               ,hsn.code
               ,spa.actual_stock
               ,spa.virtual_stock
               ,spa.stock
               ,spa.value
           ORDER BY
              created asc    
          ;
          '''
    df = pd.read_sql_query(sql, conn)
    return df

df = daily_active_product_list()

def write_to_excel():
    writer = pd.ExcelWriter('C://Users//sachi//OneDrive//Desktop//Daily_Active_Product_List.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name = 'Daily_Active_Product_List')
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
                 "arvind@tjori.com",
                 "anand@tjori.com",
                 "hemant@tjori.com",
                 "shiv@tjori.com"
                ]
    # Create message container 
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Daily Active Product Report"
    msg['From'] = sender
    msg['To'] = ",".join(recievers)

    # instance of MIMEBase and named as part
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("C:/Users/sachi/OneDrive/Desktop/Daily_Active_Product_List.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Daily_Active_Product_List.xlsx"')
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




