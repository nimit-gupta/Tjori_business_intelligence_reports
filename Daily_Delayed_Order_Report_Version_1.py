#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psycopg2 as ps
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import warnings
warnings.filterwarnings('ignore')


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
                Current_date;'''

df = pd.read_sql_query(sql,conn)
df_1 =pd.read_sql_query(sql_1,conn)

dfA1 = df[(df['name'] == 'Apparel') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfA1.empty is True:
    dfA11 = '0'
else:
    dfA11 = dfA1.to_string(header = None, index = None)
dfA2 = df[(df['name'] == 'Apparel') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfA2.empty is True:
    dfA22 = '0'
else:
    dfA22 = dfA2.to_string(header = None, index = None)
dfA3 = df[(df['name'] == 'Apparel') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfA3.empty is True:
    dfA33 = '0'
else:
    dfA33 = dfA3.to_string(header = None, index = None)
dfA4 = df[(df['name'] == 'Apparel') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfA4.empty is True:
    dfA44 = '0'
else:
    dfA44 = dfA4.to_string(header = None, index = None)
    
#**************************************************************************************************************************

dfB1 = df[(df['name'] == 'Bags') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfB1.empty is True:
    dfB11 = '0'
else:
    dfB11 = dfB1.to_string(header = None, index = None)
dfB2 = df[(df['name'] == 'Bags') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfB2.empty is True:
    dfB22 = '0'
else:
    dfB22 = dfB2.to_string(header = None, index = None)
dfB3 = df[(df['name'] == 'Bags') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfB3.empty is True:
    dfB33 = '0'
else:
    dfB33 = dfB3.to_string(header = None, index = None)
dfB4 = df[(df['name'] == 'Bags') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfB4.empty is True:
    dfB44 = '0'
else:
    dfB44 = dfB4.to_string(header = None, index = None)
    
#***************************************************************************************************************************

dfF1 = df[(df['name'] == 'Footwear') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfF1.empty is True:
    dfF11 = '0'
else:
    dfF11 = dfF1.to_string(header = None, index = None)
dfF2 = df[(df['name'] == 'Footwear') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfF2.empty is True:
    dfF22 = '0'
else:
    dfF22 = dfF2.to_string(header = None, index = None)
dfF3 = df[(df['name'] == 'Footwear') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfF3.empty is True:
    dfF33 = '0'
else:
    dfF33 = dfF3.to_string(header = None, index = None)
dfF4 = df[(df['name'] == 'Footwear') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfF4.empty is True:
    dfF44 = '0'
else:
    dfF44 = dfF4.to_string(header = None, index = None)
    
#***************************************************************************************************************************


dfH1 = df[(df['name'] == 'Home & Decor') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfH1.empty is True:
    dfH11 = '0'
else:
    dfH11 = dfH1.to_string(header = None, index = None)
dfH2 = df[(df['name'] == 'Home & Decor') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfH2.empty is True:
    dfH22 = '0'
else:
    dfH22 = dfH2.to_string(header = None, index = None)
dfH3 = df[(df['name'] == 'Home & Decor') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfH3.empty is True:
    dfH33 = '0'
else:
    dfH33 = dfH3.to_string(header = None, index = None)
dfH4 = df[(df['name'] == 'Home & Decor') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfH4.empty is True:
    dfH44 = '0'
else:
    dfH44 = dfH4.to_string(header = None, index = None)

#***************************************************************************************************************************

dfJ1 = df[(df['name'] == 'Jewelry') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfJ1.empty is True:
    dfJ11 = '0'
else:
    dfJ11 = dfJ1.to_string(header = None, index = None)
dfJ2 = df[(df['name'] == 'Jewelry') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfJ2.empty is True:
    dfJ22 = '0'
else:
    dfJ22 = dfJ2.to_string(header = None, index = None)
dfJ3 = df[(df['name'] == 'Jewelry') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfJ3.empty is True:
    dfJ33 = '0'
else:
    dfJ33 = dfJ3.to_string(header = None, index = None)
dfJ4 = df[(df['name'] == 'Jewelry') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfJ4.empty is True:
    dfJ44 = '0'
else:
    dfJ44 = dfJ4.to_string(header = None, index = None)
    
#***************************************************************************************************************************

dfM1 = df[(df['name'] == 'Mother & Child') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfM1.empty is True:
    dfM11 = '0'
else:
    dfM11 = dfM1.to_string(header = None, index = None)
dfM2 = df[(df['name'] == 'Mother & Child') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfM2.empty is True:
    dfM22 = '0'
else:
    dfM22 = dfM2.to_string(header = None, index = None)
dfM3 = df[(df['name'] == 'Mother & Child') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfM3.empty is True:
    dfM33 = '0'
else:
    dfM33 = dfM3.to_string(header = None, index = None)
dfM4 = df[(df['name'] == 'Mother & Child') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfM4.empty is True:
    dfM44 = '0'
else:
    dfM44 = dfM4.to_string(header = None, index = None)
    
#***************************************************************************************************************************
          
dfW1 = df[(df['name'] == 'Wellness') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfW1.empty is True:
    dfW11 = '0'
else:
    dfW11 = dfW1.to_string(header = None, index = None)
dfW2 = df[(df['name'] == 'Wellness') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfW2.empty is True:
    dfW22 = '0'
else:
    dfW22 = dfW2.to_string(header = None, index = None)
dfW3 = df[(df['name'] == 'Wellness') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfW3.empty is True:
    dfW33 = '0'
else:
    dfW33 = dfW3.to_string(header = None, index = None)
dfW4 = df[(df['name'] == 'Wellness') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfW4.empty is True:
    dfW44 = '0'
else:
    dfW44 = dfW4.to_string(header = None, index = None)
    
#***************************************************************************************************************************

          
dfAA1 = df[(df['name'] == 'Accessories') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfAA1.empty is True:
    dfAA11 = '0'
else:
    dfAA11 = dfAA1.to_string(header = None, index = None)
dfAA2 = df[(df['name'] == 'Accessories') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfAA2.empty is True:
    dfAA22 = '0'
else:
    dfAA22 = dfAA2.to_string(header = None, index = None)
dfAA3 = df[(df['name'] == 'Accessories') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfAA3.empty is True:
    dfAA33 = '0'
else:
    dfAA33 = dfAA3.to_string(header = None, index = None)
dfAA4 = df[(df['name'] == 'Accessories') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfAA4.empty is True:
    dfAA44 = '0'
else:
    dfAA44 = dfAA4.to_string(header = None, index = None)
    
#***************************************************************************************************************************

dfMM1 = df[(df['name'] == 'Men') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0) & (df['order_delay'] <= 3)].groupby('name')['order_delay'].count()
if dfMM1.empty is True:
    dfMM11 = '0'
else:
    dfMM11 = dfMM1.to_string(header = None, index = None)
dfMM2 = df[(df['name'] == 'Men') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 3) & (df['order_delay'] <= 5)].groupby('name')['order_delay'].count()
if dfMM2.empty is True:
    dfMM22 = '0'
else:
    dfMM22 = dfMM2.to_string(header = None, index = None)
dfMM3 = df[(df['name'] == 'Men') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 5) & (df['order_delay'] <= 7)].groupby('name')['order_delay'].count()
if dfMM3.empty is True:
    dfMM33 = '0'
else:
    dfMM33 = dfMM3.to_string(header = None, index = None)
dfMM4 = df[(df['name'] == 'Men') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 7)].groupby('name')['order_delay'].count()
if dfMM4.empty is True:
    dfMM44 = '0'
else:
    dfMM44 = dfMM4.to_string(header = None, index = None)


#Removing Date header and Index

df_2 = df_1.to_string(header = None, index = None)

#***************************************************************************************************************************

dfST1 = df[(df['name'] == 'Accessories') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST1.empty is True:
    dfST11 = '0'
else:
    dfST11 = dfST1.to_string(index = None, header = None)
dfST2 = df[(df['name'] == 'Apparel') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST2.empty is True:
    dfST22 = '0'
else:
    dfST22 = dfST2.to_string(index = None, header = None)
dfST3 = df[(df['name'] == 'Bags') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST3.empty is True:
    dfST33 = '0'
else:
    dfST33 = dfST3.to_string(index = None, header = None)
dfST4 = df[(df['name'] == 'Footwear') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST4.empty is True:
    dfST44 = '0'
else:
    dfST44 = dfST4.to_string(index = None, header = None)
dfST5 = df[(df['name'] == 'Home & Decor') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST5.empty is True:
    dfST55 = '0'
else:
    dfST55 = dfST5.to_string(index = None, header = None)
dfST6 = df[(df['name'] == 'Jewelry') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST6.empty is True:
    dfST66 = '0'
else:
    dfST66 = dfST6.to_string(index = None, header = None)
dfST7 = df[(df['name'] == 'Mother & Child') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST7.empty is True:
    dfST77 = '0'
else:
    dfST77 = dfST7.to_string(index = None, header = None)
dfST8 = df[(df['name'] == 'Wellness') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST8.empty is True:
    dfST88 = '0'
else:
    dfST88 = dfST8.to_string(index = None, header = None)
dfST9 = df[(df['name'] == 'Men') & (df['user_type'] != 'packship') & (df['user_type'] != 'qc') & (df['order_delay'] > 0)].groupby('name')['order_delay'].count()
if dfST9.empty is True:
    dfST99 = '0'
else:
    dfST99 = dfST9.to_string(index = None, header = None)

#*************************************************************************************************************************

#Sum total

dfSTT1 = df[(df.user_type != 'packship') & (df.user_type != 'qc') & (df.order_delay > 0)].count()['order_delay']

#Total

dfTT11 = df[(df.user_type != 'packship') & (df.user_type != 'qc') & (df.order_delay > 0) & (df.order_delay <=3)].count()['order_delay']

dfTT22 = df[(df.user_type != 'packship') & (df.user_type != 'qc') & (df.order_delay > 3) & (df.order_delay <=5)].count()['order_delay']

dfTT33 = df[(df.user_type != 'packship') & (df.user_type != 'qc') & (df.order_delay > 5) & (df.order_delay <=7)].count()['order_delay']

dfTT44 = df[(df.user_type != 'packship') & (df.user_type != 'qc') & (df.order_delay > 7)].count()['order_delay']


#**************************************************************************************************************************

#Packship

dfpk11 = df[(df.user_type == 'packship')  & (df.order_delay > 0) & (df.order_delay <=3)].count()['order_delay']
dfpk22 = df[(df.user_type == 'packship')  & (df.order_delay > 3) & (df.order_delay <=5)].count()['order_delay']
dfpk33 = df[(df.user_type == 'packship')  & (df.order_delay > 5) & (df.order_delay <=7)].count()['order_delay'] 
dfpk44 = df[(df.user_type == 'packship')  & (df.order_delay > 7)].count()['order_delay']

#Sum Total

dfpk55 = df[(df.user_type == 'packship')  & (df.order_delay > 0)].count()['order_delay']

#**************************************************************************************************************************

#QC

dfqc11 = df[(df.user_type == 'qc')  & (df.order_delay > 0) & (df.order_delay <=3)].count()['order_delay']
dfqc22 = df[(df.user_type == 'qc')  & (df.order_delay > 3) & (df.order_delay <=5)].count()['order_delay']
dfqc33 = df[(df.user_type == 'qc')  & (df.order_delay > 5) & (df.order_delay <=7)].count()['order_delay'] 
dfqc44 = df[(df.user_type == 'qc')  & (df.order_delay > 7)].count()['order_delay']

#Sum Total

dfqc55 = df[(df.user_type == 'qc')  & (df.order_delay > 0)].count()['order_delay']

#Grand Sum Total

dfGSTT = df.apply(lambda x : True if x['order_delay'] > 0 else False, axis = 1)
dfGSTT1 = len(dfGSTT[dfGSTT == True].index)



#*************************************************************************************************************************

# Initiating the STMP

sender = "nimit@tjori.com"
recievers = ["nimit@tjori.com","hemant@tjori.com","ankit@tjori.com","mansi@tjori.com","shiv@tjori.com"]


# Create message container - 
msg = MIMEMultipart('alternative')
msg['Subject'] = "Daily Delayed Order Report"
msg['From'] = sender
msg['To'] = ",".join(recievers)


# Create the body of the message - 
html = """<html>
  <head>
  <style> 
    table, th, td { 
    border: 2px solid black; 
    border-collapse: collapse; 
    } 
    th, td { 
        padding: 4px;
        background-color: #dff5f4;
        text-align: center;
    }
</style> 
  </head>
  <body>
    <table style="width:100%" border = 0; padding = 0;>
    <col width = "150">
    <col width = "150">
    <col width = "150">
    <col width = "150">
    <col width = "150">
    <col width = "150">
     <tr>
     <td style="background-color:#000; color:#fff; padding: 10px;"><b>Daily Delayed Order Report</b></td>
     <td style="background-color:#000; color:#fff; padding: 10px;"></td>
     <td style="background-color:#000; color:#fff; padding: 10px;"></td>
     <td style="background-color:#000; color:#fff; padding: 10px;"></td>
     <td style="background-color:#000; color:#fff; padding: 10px;"></td>
     <td style="background-color:#000; color:#fff; padding: 10px;"><b>""" + str(df_2) + """</b></td>
     </tr>
     </table>
     <br>
    </br>
    <table style="width:100%" border = 0; padding = 0;>
    <col width = "150">
    <col width = "150">
    <col width = "150">
    <col width = "150">
    <col width = "150">
    <col width = "150">
    <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;">Delay at Packship</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >0-<=3 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >3-<=5 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >5-<=7 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">     >7 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Total </th>
  </tr>
  <tr>
    <td><b>Packship</b></td>
    <td>""" + str(dfpk11) + """</td>
    <td>""" + str(dfpk22) + """</td>
    <td>""" + str(dfpk33) + """</td>
    <td>""" + str(dfpk44) + """</td>
    <td style="font-size: 20px;"><b>""" + str(dfpk55) + """</b></td>
  </tr>
  </table>
  <br>
  </br>
  <table style="width:100%" border = 0; padding = 0;>
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
    <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;">Delay at QC</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >0-<=3 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >3-<=5 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >5-<=7 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">     >7 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Total </th>
  </tr>
  <tr>
    <td><b>QC</b></td>
    <td>""" + str(dfqc11) + """</td>
    <td>""" + str(dfqc22) + """</td>
    <td>""" + str(dfqc33) + """</td>
    <td>""" + str(dfqc44) + """</td>
    <td style="font-size: 20px;"><b>""" + str(dfqc55) + """</b></td>
  </tr>
  </table>
  <br>
  </br>
  <table style="width:100%" border = 0; padding = 0;>
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;">Delay at Vendor</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >0-<=3 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >3-<=5 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> >5-<=7 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">     >7 days </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Total </th>
  </tr>
  <tr>
    <td><b>Accessories</b></td>
    <td>""" + str(dfAA11) + """</td>
    <td>""" + str(dfAA22) + """</td>
    <td>""" + str(dfAA33) + """</td>
    <td>""" + str(dfAA44) + """</td>
    <td><b>""" + str(dfST11) + """</b></td>
  </tr>
  <tr>
    <td><b>Apparel</b></td>
    <td>""" + str(dfA11) + """</td>
    <td>""" + str(dfA22) + """</td>
    <td>""" + str(dfA33) + """</td>
    <td>""" + str(dfA44) + """</td>
    <td><b>""" + str(dfST22) + """</b></td>
  </tr>
  <tr>
    <td><b>Bags</b></td>
    <td>""" + str(dfB11) + """</td>
    <td>""" + str(dfB22) + """</td>
    <td>""" + str(dfB33) + """</td>
    <td>""" + str(dfB44) + """</td>
    <td><b>""" + str(dfST33) + """</b></td>
  </tr>
  <tr>
    <td><b>Footwear</b></td>
    <td>""" + str(dfF11) + """</td>
    <td>""" + str(dfF22) + """</td>
    <td>""" + str(dfF33) + """</td>
    <td>""" + str(dfF44) + """</td>
    <td><b>""" + str(dfST44) + """</b></td>
  </tr>
  <tr>
    <td><b>Home & Decor</b></td>
    <td>""" + str(dfH11) + """</td>
    <td>""" + str(dfH22) + """</td>
    <td>""" + str(dfH33) + """</td>
    <td>""" + str(dfH44) + """</td>
    <td><b>""" + str(dfST55) + """</b></td>
  </tr>
  <tr>
    <td><b>Jewelry</b></td>
    <td>""" + str(dfJ11) + """</td>
    <td>""" + str(dfJ22) + """</td>
    <td>""" + str(dfJ33) + """</td>
    <td>""" + str(dfJ44) + """</td>
    <td><b>""" + str(dfST66) + """</b></td>
  </tr>
  <tr>
    <td><b>Mother & Child</b></td>
    <td>""" + str(dfM11) + """</td>
    <td>""" + str(dfM22) + """</td>
    <td>""" + str(dfM33) + """</td>
    <td>""" + str(dfM44) + """</td>
    <td><b>""" + str(dfST77) + """</b></td>
  </tr>
  <tr>
    <td><b>Wellness</b></td>
    <td>""" + str(dfW11) + """</td>
    <td>""" + str(dfW22) + """</td>
    <td>""" + str(dfW33) + """</td>
    <td>""" + str(dfW44) + """</td>
    <td><b>""" + str(dfST88) + """</b></td>
  </tr>
   <tr>
    <td><b>Men</b></td>
    <td>""" + str(dfMM11) + """</td>
    <td>""" + str(dfMM22) + """</td>
    <td>""" + str(dfMM33) + """</td>
    <td>""" + str(dfMM44) + """</td>
    <td><b>""" + str(dfST99) + """</b></td>
  </tr>
  <tr>
    <td><b>Total</b></td>
    <td><b>""" + str(dfTT11) + """</b></td>
    <td><b>""" + str(dfTT22) + """</b></td>
    <td><b>""" + str(dfTT33) + """</b></td>
    <td><b>""" + str(dfTT44) + """</b></td>
    <td style="font-size: 20px;"><b>""" + str(dfSTT1) + """</b></td>
  </tr>
  </table>
  <br>
  </br>
  <table style="width:100%" border = 0; padding = 0;>
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <col width = "150">
  <tr>
  <td style="background-color:#000; color:#fff; padding: 10px;"></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b>Sum Total Delayed Orders</b></td>
  <td style="background-color:#000; font-size:20px; color:#fff; padding: 10px;"><b>"""+ str(dfGSTT1) +"""</b></td>
  </tr>
  </table>
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




