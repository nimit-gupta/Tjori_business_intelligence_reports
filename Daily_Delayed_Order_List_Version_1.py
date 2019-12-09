#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psycopg2 as ps
import pygsheets
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

conn = ps.connect(user = 'nimit_new', password = 'nimit@tjori@123', host = '103.93.94.51', port = '5432', database = 'tjori_pd')
sql = '''SELECT 
      DATE(soi.created::TIMESTAMP  AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS order_date
    , soi.barcode
	 , so.invoice_id
	 , concat(so.first_name, '  ', so.last_name) AS full_name
	 , so.email
	 , so.phone
	 , so.currency
    , category.name
    , catalog.sku
    , soi.size
    , soi.quanity
    , usr.user_type
    , case when usr.user_type = 'vendor' then concat(au.first_name,' ',au.last_name) end AS vendor_name
    , EXTRACT(DAYS FROM (NOW() - soi.created)) - category.estimated_shipping_days_from AS item_delay
    , shipment.way_bill_number
    , DATE(ship.ship_date::TIMESTAMP  AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS order_ship_date
    , EXTRACT(DAYS FROM (NOW() - ship.ship_date)) AS order_delay 
    , CASE WHEN so.payment_method = '1' THEN 'Paytm'
           WHEN so.payment_method = '2' THEN 'PayU'
			  WHEN so.payment_method = '3' THEN 'Cash on Delivery' 
           WHEN so.payment_method = '4' THEN 'PayPal' 
           WHEN so.payment_method = '10' THEN 'Mobiqwik' END AS payment_methods
    , string_agg(cast(bin.bin_id AS varchar), ', ') AS item_bins
    

FROM order_orderproduct soi
    LEFT JOIN order_order so ON so.id = soi.order_id
    LEFT JOIN order_shipment_products sis ON sis.orderproduct_id = soi.id
    LEFT JOIN order_shipment shipment ON sis.shipment_id = shipment.id
    LEFT JOIN store_ribbon ribbon ON soi.ribbon = ribbon.id
    LEFT JOIN store_product catalog ON soi.product_id = catalog.id
    LEFT JOIN store_category category ON catalog.category_id = category.id
    LEFT JOIN (SELECT * FROM order_orderproductowner o WHERE o.active = TRUE) owner ON soi.id = owner.op_id
    LEFT JOIN customer_userprofile usr ON owner.user_id = usr.user_id
    LEFT JOIN auth_user AS au ON usr.user_id = au.id
    LEFT JOIN oms_shipmentbin AS bin ON bin.item_id = soi.id AND bin.active = TRUE
    LEFT JOIN (
        SELECT 
            soi.order_id,
            MAX(soi.created + category.estimated_shipping_days_from * INTERVAL '1 day') AS ship_date

        FROM 
            order_orderproduct soi
            LEFT JOIN store_product catalog ON soi.product_id = catalog.id
            LEFT JOIN store_category category ON catalog.category_id = category.id

        GROUP BY
            soi.order_id
    ) ship ON so.id = ship.order_id

WHERE 
    so.status = 'confirmed'
    AND soi.removed = FALSE
    AND soi.exchanged = FALSE
    AND soi.delivered = FALSE
    AND soi.shipped = FALSE
    AND so.email NOT LIKE '%@tjori.com'
    
    

GROUP BY
      order_date
    , soi.barcode
    , so.invoice_id
    , full_name
    , so.email
    , so.phone
    , so.currency
    , category.name
    , catalog.sku
    , soi.size
    , soi.quanity
    , usr.user_type
    , vendor_name
    , item_delay
    , shipment.way_bill_number
    , order_ship_date
    , order_delay 
    , payment_methods


ORDER BY
    order_delay ASC

;'''

sql_1 = ''' select
                  current_date;'''

df = pd.read_sql_query(sql,conn)
df_1 = pd.read_sql_query(sql_1,conn)
client = pygsheets.authorize(service_file='C:/Users/sachi/OneDrive/Desktop/Automation/delayed-order-list-09f14b13501f.json')
sh = client.open('Daily Delayed Order List')
wks = sh.sheet1
wks.clear(start = 'A1', end = None)
wks.rows = df.shape[0]
wks.set_dataframe(df, "A3")
wks.set_dataframe(df_1,"A1")

# Initiating the STMP

sender = "nimit@tjori.com"
recievers = ["nimit@tjori.com","ankit@tjori.com","hemant@tjori.com","mkindra@tjori.com"]

# Create message container - 
msg = MIMEMultipart('alternative')
msg['Subject'] = "Daily Delayed Order List"
msg['From'] = sender
msg['To'] = ",".join(recievers)

# Create the body of the message - 
html = """<html>
  <head></head>
  <body>
    <p>Hi,Daily Delayed Order List has been updated, Please click on <a href="https://docs.google.com/spreadsheets/d/1w2xpCsdA5EISaCtA247kmnzON5sH7EWEOO6xPoCE7EY/edit?ts=5d44fec6#gid=0">URL Link</a> thank you.</p>
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





# In[ ]:




