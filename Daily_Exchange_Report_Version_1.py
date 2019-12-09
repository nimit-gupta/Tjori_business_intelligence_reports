#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Importing Python Libraries

import psycopg2 as ps
import pygsheets
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Connecting to the database through psycopg2

conn = ps.connect(user = 'nimit_new', password = 'nimit@tjori@123', host = '103.93.94.51', port = '5432', database = 'tjori_pd')

#Structured Query Language used to retrieve the data from PostgreSQL

sql = '''
                 SELECT 
                      date(so.created) 
                     ,so.invoice_id AS new_order_created
                     ,so.parent_order 
                     ,so.coupon
                     ,sp.sku
                     ,sc.name
                     ,sp.name
                     ,soi.size AS new_size
                     ,soi.shipped
                     ,usr.user_type
                     ,case when usr.user_type = 'vendor' then concat(au.first_name,' ',au.last_name) end AS vendor_name
                     ,CURRENT_DATE - DATE(so.created) AS delays
                  FROM
                     order_order AS so
                  LEFT JOIN 
                     order_orderproduct AS soi ON so.id = soi.order_id
                  LEFT JOIN (
                              SELECT 
			                        * 
			                  FROM 
			                        order_orderproductowner o 
			                  WHERE 
                                  o.active = TRUE
			                ) owner ON soi.id = owner.op_id
                  LEFT JOIN 
                     customer_userprofile usr ON owner.user_id = usr.user_id
                  LEFT JOIN 
                     auth_user AS au ON usr.user_id = au.id
                  LEFT JOIN
                     store_product AS sp ON soi.product_id = sp.id
                  LEFT JOIN
                     store_category AS sc ON sp.category_id = sc.id
                  WHERE
                     so.coupon LIKE '%ex\_%'
                     AND soi.shipped = False
                     AND usr.user_type <> 'packship'
                     AND so.status NOT IN ('cancelled','Cancelled','cancelled-by-cs','Cancelled by Tjori','different-order-confirmed')
                  ORDER BY
                     date(so.created) desc
;

'''

# Converting the retrieved data into dataframe

df = pd.read_sql_query(sql,conn)

# Authorizing the pygsheet to write the dataframe to the gsheet

client = pygsheets.authorize(service_file='C:/Users/sachi/OneDrive/Desktop/Automation_Exchange/daily-exchange-products-report-81154414b9c8.json')

sh = client.open('Daily Exchange List')

wks = sh.sheet1

wks.clear(start = 'A1', end = None)

wks.rows = df.shape[0]

wks.set_dataframe(df, "A2")

# Initiating the STMP

sender = "nimit@tjori.com"
recievers = ["nimit@tjori.com","neeraj@tjori.com","hemant@tjori.com","farhan@tjori.com","shiv@tjori.com"]

# Create message container - 
msg = MIMEMultipart('alternative')
msg['Subject'] = "Daily Exchange Report"
msg['From'] = sender
msg['To'] = ",".join(recievers)

# Create the body of the message - 
html = """<html>
  <head></head>
  <body>
    <p>Hi,Daily Exchange List has been updated, Please click on <a href="https://docs.google.com/spreadsheets/d/1SOqkPQzzXQrG9RTG4CfJPlXDpyy6bnbx9XkQwxa6Mvw/edit#gid=0">URL Link</a> thank you.</p>
    <p> - Nimit Gupta </p>
  </body>
</html>
"""

# Record the MIME type - 
part1 = MIMEText(html, 'html')

msg.attach(part1)


# Send the message via local SMTP server - 
mail = smtplib.SMTP('smtp.gmail.com', 587)

mail.ehlo()

mail.starttls()

mail.login('nimit@tjori.com', 's/987456321/G')
mail.sendmail(sender, recievers, msg.as_string())
mail.quit()





# In[ ]:




