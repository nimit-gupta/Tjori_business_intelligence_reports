#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Importing libraries

import psycopg2 as ps
import pandas as pd
import warnings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import warnings
warnings.filterwarnings('ignore')

pd.options.display.float_format = '{0:,.0f}'.format

def wms_valuation_clearance():
    conn = ps.connect(user = 'doadmin', password = 'xpmt05ij9uf9rknn', host = 'tjori-bi-do-user-6486966-0.db.ondigitalocean.com', port = '25060', database = 'defaultdb')
    sql = '''SELECT
      sq.category as category
	  ,sq.quantity as quantity
	  ,sq.stock_valuation
	  ,sq.clearance_status
FROM
     (

       SELECT 
                b.category AS category
               ,b.sku AS product_sku
               ,b.size AS product_size
			   ,CASE
			        WHEN sp.ribbon_id = 3 THEN 'Clearance' ELSE 'Non-Clearance' END AS clearance_status
			   ,COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS inward_stock
               ,COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS outward_stock
               ,COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS quantity
               ,coalesce(sp.special_price,0) AS special_price
               ,((COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata')) * (coalesce(sp.special_price,0))) AS stock_valuation
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
              stock_valuation DESC
		  ) AS sq
WHERE 
     sq.clearance_status SIMILAR TO 'Clearance'
;
'''

    df = pd.read_sql_query(sql,conn)
    return df

def wms_valuation_non_clearance():
    conn = ps.connect(user = 'doadmin', password = 'xpmt05ij9uf9rknn', host = 'tjori-bi-do-user-6486966-0.db.ondigitalocean.com', port = '25060', database = 'defaultdb')
    sql = '''SELECT
      sq.category as category
	  ,sq.quantity as quantity
	  ,sq.stock_valuation
	  ,sq.clearance_status
FROM
     (

       SELECT 
                b.category AS category
               ,b.sku AS product_sku
               ,b.size AS product_size
			   ,CASE
			        WHEN sp.ribbon_id = 3 THEN 'Clearance' ELSE 'Non-Clearance' END AS clearance_status
			   ,COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS inward_stock
               ,COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS outward_stock
               ,COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS quantity
               ,coalesce(sp.special_price,0) AS special_price
               ,((COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata')) * (coalesce(sp.special_price,0))) AS stock_valuation
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
              stock_valuation DESC
		  ) AS sq
WHERE 
     sq.clearance_status SIMILAR TO 'Non-Clearance'
;
'''

    dff = pd.read_sql_query(sql,conn)
    return dff

def wms_valuation_total():
    conn = ps.connect(user = 'doadmin', password = 'xpmt05ij9uf9rknn', host = 'tjori-bi-do-user-6486966-0.db.ondigitalocean.com', port = '25060', database = 'defaultdb')
    sql = '''SELECT
      sq.category as category
	  ,sq.quantity as quantity
	  ,sq.stock_valuation
	  ,sq.clearance_status
FROM
     (

       SELECT 
                b.category AS category
               ,b.sku AS product_sku
               ,b.size AS product_size
			   ,CASE
			        WHEN sp.ribbon_id = 3 THEN 'Clearance' ELSE 'Non-Clearance' END AS clearance_status
			   ,COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS inward_stock
               ,COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS outward_stock
               ,COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS quantity
               ,coalesce(sp.special_price,0) AS special_price
               ,((COUNT(a.in_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') - COUNT(a.out_timestamp::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata')) * (coalesce(sp.special_price,0))) AS stock_valuation
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
              stock_valuation DESC
		  ) AS sq

;
'''

    ddf = pd.read_sql_query(sql,conn)
    return ddf

#WMS Clearance Stock Valuation

dfw = wms_valuation_clearance()

#WMS Quantity

dfw1w1 = dfw[(dfw['category'] == 'apparel')].groupby('category')['quantity'].sum()
dfw11w11 = dfw1w1.to_string(index = None, header = None)

dfw2w2 = dfw[(dfw['category'] == 'bags')].groupby('category')['quantity'].sum()
dfw22w22 = dfw2w2.to_string(index = None, header = None)

dfw3w3 = dfw[(dfw['category'] == 'footwear')].groupby('category')['quantity'].sum()
dfw33w33 = dfw3w3.to_string(index = None, header = None)

dfw4w4 = dfw[(dfw['category'] == 'home')].groupby('category')['quantity'].sum()
dfw44w44 = dfw4w4.to_string(index = None, header = None)

dfw5w5 = dfw[(dfw['category'] == 'jewelry')].groupby('category')['quantity'].sum()
dfw55w55 = dfw5w5.to_string(index = None, header = None)

dfw6w6 = dfw[(dfw['category'] == 'living')].groupby('category')['quantity'].sum()
if dfw6w6.empty is True:
    dfw66w66 = '0'
else:
    dfw66w66 = dfw6w6.to_string(index = None, header = None)

dfw7w7 = dfw[(dfw['category'] == 'accessories')].groupby('category')['quantity'].sum()
dfw77w77 = dfw7w7.to_string(index = None, header = None)

dfw8w8 = dfw[(dfw['category'] == 'motherchild')].groupby('category')['quantity'].sum()
if dfw8w8.empty is True:
    dfw88w88 = '0'
else:
    dfw88w88 = dfw8w8.to_string(index = None, header = None)

#WMS Stock_valuation

dfm1m1 = dfw[(dfw['category'] == 'apparel')].groupby('category')['stock_valuation'].sum()
dfm11m11 = dfm1m1.to_string(index = None, header = None)

dfm2m2 = dfw[(dfw['category'] == 'bags')].groupby('category')['stock_valuation'].sum()
dfm22m22 = dfm2m2.to_string(index = None, header = None)

dfm3m3 = dfw[(dfw['category'] == 'footwear')].groupby('category')['stock_valuation'].sum()
dfm33m33 = dfm3m3.to_string(index = None, header = None)

dfm4m4 = dfw[(dfw['category'] == 'home')].groupby('category')['stock_valuation'].sum()
dfm44m44 = dfm4m4.to_string(index = None, header = None)

dfm5m5 = dfw[(dfw['category'] == 'jewelry')].groupby('category')['stock_valuation'].sum()
dfm55m55 = dfm5m5.to_string(index = None, header = None)

dfm6m6 = dfw[(dfw['category'] == 'living')].groupby('category')['stock_valuation'].sum()
if dfm6m6.empty is True:
    dfm66m66 = '0'
else:
    dfm66m66 = dfm6m6.to_string(index = None, header = None)

dfm7m7 = dfw[(dfw['category'] == 'accessories')].groupby('category')['stock_valuation'].sum()
dfm77m77 = dfm7m7.to_string(index = None, header = None)

dfm8m8 = dfw[(dfw['category'] == 'motherchild')].groupby('category')['stock_valuation'].sum()
if dfm8m8.empty is True:
    dfm88m88 = '0'
else: 
    dfm88m88 = dfm8m8.to_string(index = None, header = None)

#WMS Non-Clearance Stock Valuation

dffw = wms_valuation_non_clearance()

#WMS Quantity

dffw1w1 = dffw[(dffw['category'] == 'apparel')].groupby('category')['quantity'].sum()
dffw11w11 = dffw1w1.to_string(index = None, header = None)

dffw2w2 = dffw[(dffw['category'] == 'bags')].groupby('category')['quantity'].sum()
dffw22w22 = dffw2w2.to_string(index = None, header = None)

dffw3w3 = dffw[(dffw['category'] == 'footwear')].groupby('category')['quantity'].sum()
dffw33w33 = dffw3w3.to_string(index = None, header = None)

dffw4w4 = dffw[(dffw['category'] == 'home')].groupby('category')['quantity'].sum()
dffw44w44 = dffw4w4.to_string(index = None, header = None)

dffw5w5 = dffw[(dffw['category'] == 'jewelry')].groupby('category')['quantity'].sum()
dffw55w55 = dffw5w5.to_string(index = None, header = None)

dffw6w6 = dffw[(dffw['category'] == 'living')].groupby('category')['quantity'].sum()
if dffw6w6.empty is True:
    dffw66w66 = '0'
else:
    dffw66w66 = dffw6w6.to_string(index = None, header = None)

dffw7w7 = dffw[(dffw['category'] == 'accessories')].groupby('category')['quantity'].sum()
dffw77w77 = dffw7w7.to_string(index = None, header = None)

dffw8w8 = dffw[(dffw['category'] == 'motherchild')].groupby('category')['quantity'].sum()
if dffw8w8.empty is True:
    dffw88w88 = '0'
else:
    dffw88w88 = dffw8w8.to_string(index = None, header = None)

#WMS Stock_valuation

dffm1m1 = dffw[(dffw['category'] == 'apparel')].groupby('category')['stock_valuation'].sum()
dffm11m11 = dffm1m1.to_string(index = None, header = None)

dffm2m2 = dffw[(dffw['category'] == 'bags')].groupby('category')['stock_valuation'].sum()
dffm22m22 = dffm2m2.to_string(index = None, header = None)

dffm3m3 = dffw[(dffw['category'] == 'footwear')].groupby('category')['stock_valuation'].sum()
dffm33m33 = dffm3m3.to_string(index = None, header = None)

dffm4m4 = dffw[(dffw['category'] == 'home')].groupby('category')['stock_valuation'].sum()
dffm44m44 = dffm4m4.to_string(index = None, header = None)

dffm5m5 = dffw[(dffw['category'] == 'jewelry')].groupby('category')['stock_valuation'].sum()
dffm55m55 = dffm5m5.to_string(index = None, header = None)

dffm6m6 = dffw[(dffw['category'] == 'living')].groupby('category')['stock_valuation'].sum()
if dffm6m6.empty is True:
    dffm66m66 = '0'
else:
    dffm66m66 = dffm6m6.to_string(index = None, header = None)

dffm7m7 = dffw[(dffw['category'] == 'accessories')].groupby('category')['stock_valuation'].sum()
dffm77m77 = dffm7m7.to_string(index = None, header = None)

dffm8m8 = dffw[(dffw['category'] == 'motherchild')].groupby('category')['stock_valuation'].sum()
if dffm8m8.empty is True:
    dffm88m88 = '0'
else: 
    dffm88m88 = dffm8m8.to_string(index = None, header = None)

#WMS Total Stock Valuation

ddfw = wms_valuation_total()

#WMS Quantity

ddfw1w1 = ddfw[(ddfw['category'] == 'apparel')].groupby('category')['quantity'].sum()
ddfw11w11 = ddfw1w1.to_string(index = None, header = None)

ddfw2w2 = ddfw[(ddfw['category'] == 'bags')].groupby('category')['quantity'].sum()
ddfw22w22 = ddfw2w2.to_string(index = None, header = None)

ddfw3w3 = ddfw[(ddfw['category'] == 'footwear')].groupby('category')['quantity'].sum()
ddfw33w33 = ddfw3w3.to_string(index = None, header = None)

ddfw4w4 = ddfw[(ddfw['category'] == 'home')].groupby('category')['quantity'].sum()
ddfw44w44 = ddfw4w4.to_string(index = None, header = None)

ddfw5w5 = ddfw[(ddfw['category'] == 'jewelry')].groupby('category')['quantity'].sum()
ddfw55w55 = ddfw5w5.to_string(index = None, header = None)

ddfw6w6 = ddfw[(ddfw['category'] == 'living')].groupby('category')['quantity'].sum()
if ddfw6w6.empty is True:
    ddfw66w66 = '0'
else:
    ddfw66w66 = ddfw6w6.to_string(index = None, header = None)

ddfw7w7 = ddfw[(ddfw['category'] == 'accessories')].groupby('category')['quantity'].sum()
ddfw77w77 = ddfw7w7.to_string(index = None, header = None)

ddfw8w8 = ddfw[(ddfw['category'] == 'motherchild')].groupby('category')['quantity'].sum()
if ddfw8w8.empty is True:
    ddfw88w88 = '0'
else:
    ddfw88w88 = ddfw8w8.to_string(index = None, header = None)

#WMS Stock_valuation

ddfm1m1 = ddfw[(ddfw['category'] == 'apparel')].groupby('category')['stock_valuation'].sum()
ddfm11m11 = ddfm1m1.to_string(index = None, header = None)

ddfm2m2 = ddfw[(ddfw['category'] == 'bags')].groupby('category')['stock_valuation'].sum()
ddfm22m22 = ddfm2m2.to_string(index = None, header = None)

ddfm3m3 = ddfw[(ddfw['category'] == 'footwear')].groupby('category')['stock_valuation'].sum()
ddfm33m33 = ddfm3m3.to_string(index = None, header = None)

ddfm4m4 = ddfw[(ddfw['category'] == 'home')].groupby('category')['stock_valuation'].sum()
ddfm44m44 = ddfm4m4.to_string(index = None, header = None)

ddfm5m5 = ddfw[(ddfw['category'] == 'jewelry')].groupby('category')['stock_valuation'].sum()
ddfm55m55 = ddfm5m5.to_string(index = None, header = None)

ddfm6m6 = ddfw[(ddfw['category'] == 'living')].groupby('category')['stock_valuation'].sum()
ddfm66m66 = ddfm6m6.to_string(index = None, header = None)

ddfm7m7 = ddfw[(ddfw['category'] == 'accessories')].groupby('category')['stock_valuation'].sum()
ddfm77m77 = ddfm7m7.to_string(index = None, header = None)

ddfm8m8 = ddfw[(ddfw['category'] == 'motherchild')].groupby('category')['stock_valuation'].sum()
ddfm88m88 = ddfm8m8.to_string(index = None, header = None)


#WMS_Sum_Total_Clearance

dfs1s1 = format(sum(dfw['quantity']),",d")

dfs2s2 = format(int(sum(dfw['stock_valuation'])),",d")

#WMS Sum Total_Non_Clearance

dfs1s1s1 = format(sum(dffw['quantity']),",d")

dfs2s2s2 = format(int(sum(dffw['stock_valuation'])),",d")

#WMS Sum Total

dfs1s1s1s1 = format(sum(ddfw['quantity']),",d")

dfs2s2s2s2 = format(int(sum(ddfw['stock_valuation'])),",d")

# Initiating the STMP

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


# Create message container - 
msg = MIMEMultipart('alternative')
msg['Subject'] = "Daily Warehouse Stock Report"
msg['From'] = sender
msg['To'] = ",".join(recievers)

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
  <p><b>WMS Clearance Stock Valuation</b></p>
  <table style="width:100%" border = 0; padding = 0;>
    <col width = "200">
    <col width = "200">
    <col width = "200">
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Category Name </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Stock Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Stock Valuation</th>
  </tr>
  <tr>
  <td><b>Apparel</b></td>
  <td>""" + str(dfw11w11) + """</td>
  <td>""" + str(dfm11m11) + """</td>
  </tr>
  <tr>
  <td><b>Bags</b></td>
  <td>""" + str(dfw22w22) + """</td>
  <td>""" + str(dfm22m22) + """</td>
  </tr>
  <tr>
  <td><b>Footwear</b></td>
  <td>""" + str(dfw33w33) + """</td>
  <td>""" + str(dfm33m33) + """</td>
  </tr>
  <tr>
  <td><b>Home & Decor</b></td>
  <td>""" + str(dfw44w44) + """</td>
  <td>""" + str(dfm44m44) + """</td>
  </tr>
  <tr>
  <td><b>Jewelry</b></td>
  <td>""" + str(dfw55w55) + """</td>
  <td>""" + str(dfm55m55) + """</td>
  </tr>
  <tr>
  <td><b>Wellness</b></td>
  <td>""" + str(dfw66w66) + """</td>
  <td>""" + str(dfm66m66) + """</td>
  </tr>
  <tr>
  <td><b>Accessories</b></td>
  <td>""" + str(dfw77w77) + """</td>
  <td>""" + str(dfm77m77) + """</td>
  </tr>
  <tr>
  <td><b>Mother & Child</b></td>
  <td>""" + str(dfw88w88) + """</td>
  <td>""" + str(dfm88m88) + """</td>
  </tr>
  <tr>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b>Sum total</b></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(dfs1s1)+"""</b></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(dfs2s2)+"""</b></td>
  </tr>
  </table>
  <br>
  </br>
  <p><b>WMS Non-Clearance Stock Valuation</b></p>
  <table style="width:100%" border = 0; padding = 0;>
    <col width = "200">
    <col width = "200">
    <col width = "200">
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Category Name </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Stock Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Stock Valuation</th>
  </tr>
  <tr>
  <td><b>Apparel</b></td>
  <td>""" + str(dffw11w11) + """</td>
  <td>""" + str(dffm11m11) + """</td>
  </tr>
  <tr>
  <td><b>Bags</b></td>
  <td>""" + str(dffw22w22) + """</td>
  <td>""" + str(dffm22m22) + """</td>
  </tr>
  <tr>
  <td><b>Footwear</b></td>
  <td>""" + str(dffw33w33) + """</td>
  <td>""" + str(dffm33m33) + """</td>
  </tr>
  <tr>
  <td><b>Home & Decor</b></td>
  <td>""" + str(dffw44w44) + """</td>
  <td>""" + str(dffm44m44) + """</td>
  </tr>
  <tr>
  <td><b>Jewelry</b></td>
  <td>""" + str(dffw55w55) + """</td>
  <td>""" + str(dffm55m55) + """</td>
  </tr>
  <tr>
  <td><b>Wellness</b></td>
  <td>""" + str(dffw66w66) + """</td>
  <td>""" + str(dffm66m66) + """</td>
  </tr>
  <tr>
  <td><b>Accessories</b></td>
  <td>""" + str(dffw77w77) + """</td>
  <td>""" + str(dffm77m77) + """</td>
  </tr>
  <tr>
  <td><b>Mother & Child</b></td>
  <td>""" + str(dffw88w88) + """</td>
  <td>""" + str(dffm88m88) + """</td>
  </tr>
  <tr>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b>Sum total</b></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(dfs1s1s1)+"""</b></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(dfs2s2s2)+"""</b></td>
  </tr>
  </table>
  <br>
  </br>
  <p><b>WMS Total Stock Valuation</b></p>
  <table style="width:100%" border = 0; padding = 0;>
    <col width = "200">
    <col width = "200">
    <col width = "200">
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Category Name </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Stock Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Stock Valuation</th>
  </tr>
  <tr>
  <td><b>Apparel</b></td>
  <td>""" + str(ddfw11w11) + """</td>
  <td>""" + str(ddfm11m11) + """</td>
  </tr>
  <tr>
  <td><b>Bags</b></td>
  <td>""" + str(ddfw22w22) + """</td>
  <td>""" + str(ddfm22m22) + """</td>
  </tr>
  <tr>
  <td><b>Footwear</b></td>
  <td>""" + str(ddfw33w33) + """</td>
  <td>""" + str(ddfm33m33) + """</td>
  </tr>
  <tr>
  <td><b>Home & Decor</b></td>
  <td>""" + str(ddfw44w44) + """</td>
  <td>""" + str(ddfm44m44) + """</td>
  </tr>
  <tr>
  <td><b>Jewelry</b></td>
  <td>""" + str(ddfw55w55) + """</td>
  <td>""" + str(ddfm55m55) + """</td>
  </tr>
  <tr>
  <td><b>Wellness</b></td>
  <td>""" + str(ddfw66w66) + """</td>
  <td>""" + str(ddfm66m66) + """</td>
  </tr>
  <tr>
  <td><b>Accessories</b></td>
  <td>""" + str(ddfw77w77) + """</td>
  <td>""" + str(ddfm77m77) + """</td>
  </tr>
  <tr>
  <td><b>Mother & Child</b></td>
  <td>""" + str(ddfw88w88) + """</td>
  <td>""" + str(ddfm88m88) + """</td>
  </tr>
  <tr>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b>Sum total</b></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(dfs1s1s1s1)+"""</b></td>
  <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(dfs2s2s2s2)+"""</b></td>
  </tr>
  </table>
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




