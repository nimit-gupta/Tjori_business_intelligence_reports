#!/usr/bin/env python
# coding: utf-8

# In[1]:


#************************************************************************************************************************
# Importing libraries

import psycopg2 as ps
import pygsheets
import pandas as pd
import numpy as np
import datetime
import warnings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
warnings.filterwarnings('ignore')
import re

#*************************************************************************************************************************


pd.options.display.float_format = '{0:,.0f}'.format


#**************************************************************************************************************************

def date_time (startdate,enddate):
    
    # Connect to Database
    conn = ps.connect(user = 'nimit_new', password = 'nimit@tjori@123', host = '103.93.94.51', port = '5432', database = 'tjori_pd')
    sql = '''
            SELECT
       date(so.created)
      ,so.email
      ,so.id
      ,soi.product_id
      ,sc.name AS category
      ,soi.price
      ,soi.quanity
      ,soi.discount
      ,hsn.tax
      ,((soi.price*soi.quanity) - soi.discount) AS Revenue_Before_Tax
      ,case
          WHEN sc.name = 'Apparel' THEN round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Wellness' THEN round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Footwear' THEN round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Bags' THEN round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Jewelry' THEN round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100)
          WHEN sc.name = 'Home & Decor' THEN round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Mother & Child' THEN round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          END AS Taxable_amount
      ,case
          WHEN sc.name = 'Apparel' THEN ((soi.price*soi.quanity) - soi.discount) - round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Wellness' THEN ((soi.price*soi.quanity) - soi.discount) - round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Footwear' THEN ((soi.price*soi.quanity) - soi.discount) - round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Bags' THEN ((soi.price*soi.quanity) - soi.discount) - round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Jewelry' THEN ((soi.price*soi.quanity) - soi.discount) - round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Home & Decor' THEN ((soi.price*soi.quanity) - soi.discount) - round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
          WHEN sc.name = 'Mother & Child' THEN ((soi.price*soi.quanity) - soi.discount) - round((((soi.price*soi.quanity) - soi.discount)*hsn.tax::integer)/100) 
			 END AS revenue_after_tax
          
FROM
     order_order AS so
LEFT JOIN
     order_orderproduct AS soi ON so.id = soi.order_id
LEFT JOIN
     store_product AS sp ON soi.product_id = sp.id
LEFT JOIN
     store_category AS sc ON sp.category_id = sc.id
LEFT JOIN
     tms_hsncode AS hsn ON sp.hsncode_id = hsn.id
WHERE
     so.created >= '%s' AND so.created < '%s'
     AND so.email LIKE '%%@tjori.com%%'
     AND so.status = 'confirmed'

      
      ;
    ''' % (
             startdate,
             enddate 
          )
    
    dff = pd.read_sql_query(sql, conn)
    return dff

if __name__ == '__main__':
    td = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    yd = (datetime.datetime.now() - datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    fd = (datetime.datetime.now() - datetime.timedelta(1)).replace(day=1,hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    ydb = (datetime.datetime.now() - datetime.timedelta(2)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')

#*************************************************************************************************************************

# Yesterday

dfy = date_time(yd,td) 

a1 = dfy[dfy['email'] == 'nykaa@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a1.empty is True:
    a11 = '0'
else:
    a11 = a1.to_string(header = None, index = None)
a2 = dfy[dfy['email'] == 'amazon@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a2.empty is True:
    a22 = '0'
else:
    a22 = a2.to_string(header = None, index = None)
a3 = dfy[dfy['email'] == 'flipkart@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a3.empty is True:
    a33 = '0'
else:
    a33 = a3.to_string(header = None, index = None)
a4 = dfy[dfy['email'] == 'jabong@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a4.empty is True:
    a44 = '0'
else:
    a44 = a4.to_string(header = None, index = None)
a5 = dfy[dfy['email'] == 'myntra@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a5.empty is True:
    a55 = '0'
else:
    a55 = a5.to_string(header = None, index = None)
a6 = dfy[dfy['email'] == 'limeroad@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a6.empty is True:
    a66 = '0'
else:
    a66 = a6.to_string(header = None, index = None)
a7 = dfy[dfy['email'] == 'tatacliq@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a7.empty is True:
    a77 = '0'
else:
    a77 = a7.to_string(header = None, index = None)
a8 = dfy[dfy['email'] == 'paytm@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
a88 = a8.to_string(header = None, index = None)
if a8.empty is True:
    a88 = '0'
else:
    a88 = a8.to_string(header = None, index = None)
a9 = dfy[dfy['email'] == 'cloudtail@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a9.empty is True:
    a99 = '0'
else:
    a99 = a9.to_string(header = None, index = None)
a10 = dfy[dfy['email'] == '1mg@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a10.empty is True:
    a1010 = '0'
else:
    a1010 = a10.to_string(header = None, index = None)
a111 = dfy[dfy['email'] == 'bigbasket@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a111.empty is True:
    a1111 = '0'
else:
    a1111 = a111.to_string(header = None, index = None)
a12 = dfy[dfy['email'] == 'pepperfry@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a12.empty is True:
    a1212 = '0'
else:
    a1212 = a12.to_string(header = None, index = None)
a13 = dfy[dfy['email'] == 'firstcry@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a13.empty is True:
    a1313 = '0'
else:
    a1313 = a13.to_string(header = None, index = None)
a14 = dfy[dfy['email'] == 'mirraw@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())   
if a14.empty is True:
    a1414 = '0'
else:
    a1414 = a14.to_string(header = None, index = None)
a15 = dfy[dfy['email'] == 'mirraw@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())   
if a14.empty is True:
    a1414 = '0'
else:
    a1414 = a14.to_string(header = None, index = None)
a15 = dfy[dfy['email'] == 'nykaafashion@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a15.empty is True:
    a1515 = '0'
else:
    a1515 = a15.to_string(header = None, index = None)
a16 = dfy[dfy['email'] == 'lbb@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a16.empty is True:
    a1616 = '0'
else:
    a1616 = a16.to_string(header = None, index = None)
a17 = dfy[dfy['email'] == 'amazon.fba@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if a17.empty is True:
    a1717 = '0'
else:
    a1717 = a17.to_string(header = None, index = None)

#***************************************************************************************************************************

# Day Before Yesterday

dfyb = date_time(ydb, yd)

b1 = dfyb[dfyb['email'] == 'nykaa@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b1.empty is True:
    b11 = '0'
else:
    b11 = b1.to_string(header = None, index = None)
b2 = dfyb[dfyb['email'] == 'amazon@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b2.empty is True:
    b22 = '0'
else:
    b22 = b2.to_string(header = None, index = None)
b3 = dfyb[dfyb['email'] == 'flipkart@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b3.empty is True:
    b33 = '0'
else:
    b33 = b3.to_string(header = None, index = None)
b4 = dfyb[dfyb['email'] == 'jabong@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b4.empty is True:
    b44 = '0'
else:
    b44 = b4.to_string(header = None, index = None)
b5 = dfyb[dfyb['email'] == 'myntra@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b5.empty is True:
    b55 = '0'
else:
    b55 = b5.to_string(header = None, index = None)
b6 = dfyb[dfyb['email'] == 'limeroad@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b6.empty is True:
    b66 = '0'
else:
    b66 = b6.to_string(header = None, index = None)
b7 = dfyb[dfyb['email'] == 'tatacliq@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b7.empty is True:
    b77 = '0'
else:
    b77 = b7.to_string(header = None, index = None)
b8 = dfyb[dfyb['email'] == 'paytm@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b8.empty is True:
    b88 = '0'
else:
    b88 = b8.to_string(header = None, index = None)
b9 = dfyb[dfyb['email'] == 'cloudtail@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b9.empty is True:
    b99 = '0'
else:
    b99 = b9.to_string(header = None, index = None)
b10 = dfyb[dfyb['email'] == '1mg@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b10.empty is True:
    b1010 = '0'
else:
    b1010 = b10.to_string(header = None, index = None)
b111 = dfyb[dfyb['email'] == 'bigbasket@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b111.empty is True:
    b1111 = '0'
else:
    b1111 = b111.to_string(header = None, index = None)
b12 = dfyb[dfyb['email'] == 'pepperfry@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b12.empty is True:
    b1212 = '0'
else:
    b1212 = b12.to_string(header = None, index = None)
b13 = dfyb[dfyb['email'] == 'firstcry@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b13.empty is True:
    b1313 = '0'
else:
    b1313 = b13.to_string(header = None, index = None)
b14 = dfyb[dfyb['email'] == 'mirraw@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b14.empty is True:
    b1414 = '0'
else:
    b1414 = b14.to_string(header = None, index = None)
b15 = dfyb[dfyb['email'] == 'nykaafashion@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b15.empty is True:
    b1515 = '0'
else:
    b1515 = b15.to_string(header = None, index = None)
b16 = dfyb[dfyb['email'] == 'lbb@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b16.empty is True:
    b1616 = '0'
else:
    b1616 = b16.to_string(header = None, index = None)
b17 = dfyb[dfyb['email'] == 'amazon.fba@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if b17.empty is True:
    b1717 = '0'
else:
    b1717 = b17.to_string(header = None, index = None)


#***************************************************************************************************************************

# Month Till Date

dfmtd = date_time(fd, td)

c1 = dfmtd[dfmtd['email'] == 'nykaa@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c1.empty is True:
    c11 = '0'
else:
    c11 = c1.to_string(header = None, index = None)
c2 = dfmtd[dfmtd['email'] == 'amazon@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c2.empty is True:
    c22 = '0'
else:
    c22 = c2.to_string(header = None, index = None)
c3 = dfmtd[dfmtd['email'] == 'flipkart@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c3.empty is True:
    c33 = '0'
else:
    c33 = c3.to_string(header = None, index = None)
c4 = dfmtd[dfmtd['email'] == 'jabong@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c4.empty is True:
    c44 = '0'
else:
    c44 = c4.to_string(header = None, index = None)
c5 = dfmtd[dfmtd['email'] == 'myntra@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c5.empty is True:
    c55 = '0'
else:
    c55 = c5.to_string(header = None, index = None)
c6 = dfmtd[dfmtd['email'] == 'limeroad@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c6.empty is True:
    c66 = '0'
else:
    c66 = c6.to_string(header = None, index = None)
c7 = dfmtd[dfmtd['email'] == 'tatacliq@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c7.empty is True:
    c77 = '0'
else:
    c77 = c7.to_string(header = None, index = None)
c8 = dfmtd[dfmtd['email'] == 'paytm@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c8.empty is True:
    c88 = '0'
else:
    c88 = c8.to_string(header = None, index = None)
c9 = dfmtd[dfmtd['email'] == 'cloudtail@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c9.empty is True:
    c99 = '0'
else:
    c99 = c9.to_string(header = None, index = None)
c10 = dfmtd[dfmtd['email'] == '1mg@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c10.empty is True:
    c1010 = '0'
else:
    c1010 = c10.to_string(header = None, index = None) 
c111 = dfmtd[dfmtd['email'] == 'bigbasket@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c111.empty is True:
    c1111 = '0'
else:
    c1111 = c111.to_string(header = None, index = None)
c12 = dfmtd[dfmtd['email'] == 'pepperfry@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c12.empty is True:
    c1212 = '0'
else:
    c1212 = c12.to_string(header = None, index = None) 
c13 = dfmtd[dfmtd['email'] == 'firstcry@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c13.empty is True:
    c1313 = '0'
else:
    c1313 = c13.to_string(header = None, index = None) 
c14 = dfmtd[dfmtd['email'] == 'mirraw@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c14.empty is True:
    c1414 = '0'
else:
    c1414 = c14.to_string(header = None, index = None)
c15 = dfmtd[dfmtd['email'] == 'nykaafashion@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c15.empty is True:
    c1515 = '0'
else:
    c1515 = c15.to_string(header = None, index = None)
c16 = dfmtd[dfmtd['email'] == 'lbb@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c16.empty is True:
    c1616 = '0'
else:
    c1616 = c16.to_string(header = None, index = None)
c17 = dfmtd[dfmtd['email'] == 'amazon.fba@tjori.com'].groupby('email').apply(lambda x : x['revenue_after_tax'].sum())
if c17.empty is True:
    c1717 = '0'
else:
    c1717 = c17.to_string(header = None, index = None)
    

#************************************************************************************************************************

#Sum Total
tjori_email = ['nykaa@tjori.com','amazon@tjori.com','flipkart@tjori.com','jabong@tjori.com','myntra@tjori.com','limeroad@tjori.com','tatacliq@tjori.com',
              'paytm@tjori.com','cloudtail@tjori.com','1mg@tjori.com','bigbasket@tjori.com','pepperfry@tjori.com','firstcry@tjori.com','mirraw@tjori.com',
              'nykaafashion@tjori.com','lbb@tjori.com','amazon.fba@tjori.com']                                                                    

a999 = (dfy[dfy['email'].isin(tjori_email)].aggregate({'revenue_after_tax' : 'sum'}))
a9999 = a999.to_string(header = None, index = None)

b999 = (dfyb[dfyb['email'].isin(tjori_email)].aggregate({'revenue_after_tax' : 'sum'}))
b9999 = b999.to_string(header = None, index = None)

c999 = (dfmtd[dfmtd['email'].isin(tjori_email)].aggregate({'revenue_after_tax' : 'sum'}))
c9999 = c999.to_string(header = None, index = None)



#************************************************************************************************************************

def date_time_1():
    conn = ps.connect(user = 'nimit_new', password = 'nimit@tjori@123', host = '103.93.94.51', port = '5432', database = 'tjori_pd')
    sql_1 = '''
           SELECT
                 CURRENT_DATE - 1;
        '''
    sql_2 = '''
          SELECT CURRENT_DATE - 2;
        '''

    df_1 = pd.read_sql_query(sql_1, conn)
    df_2 = pd.read_sql_query(sql_2,conn)
    return df_1,df_2

df_1,df_2 = date_time_1()
df_1_1 = df_1.to_string(header = None, index = None)
df_2_2 = df_2.to_string(header = None, index = None)


#*************************************************************************************************************************

client = pygsheets.authorize(service_file='C:/Users/sachi/OneDrive/Desktop/Automation_V2/daily-market-place-report-3734e9e4d9ca.json')
sh = client.open('Daily Market Place Report')
wks = sh.sheet1
h11 = wks.get_value("B1")
h22 = wks.get_value("B2")
h33 = wks.get_value("B3")
h44 = wks.get_value("B4")
h55 = wks.get_value("B5")
h66 = wks.get_value("B6")
h77 = wks.get_value("B7")
h88 = wks.get_value("B8")
h99 = wks.get_value("B9")
h1010 = wks.get_value("B10")
h1111 = wks.get_value("B11")
h1212 = wks.get_value("B12")
h1313 = wks.get_value("B13")
h1414 = wks.get_value("B14")
h1515 = wks.get_value("B15")
h1616 = wks.get_value("B16")
h1717 = wks.get_value("B17")
h1818 = wks.get_value("B18")


#*************************************************************************************************************************

# Initiating the STMP

sender = "nimit@tjori.com"
recievers = ["nimit@tjori.com","ankit@tjori.com","ritika.chhokra@tjori.com", "mansi@tjori.com", "poonam@tjori.com","shiv@tjori.com"]

# Create message container - 
msg = MIMEMultipart('alternative')
msg['Subject'] = "Daily Market Place Report"
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
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;">Market Place</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">""" + str(df_1_1) + """</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">""" + str(df_2_2) + """</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> MTD </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Targets</th>
  </tr>
  <tr>
    <td><b>nykaa</b></td>
    <td>""" + str(a11) + """</td>
    <td>""" + str(b11) + """</td>
    <td>""" + str(c11) + """</td>
    <td>""" + str(h11) + """</td>
  </tr>
  <tr>
    <td><b>amazon</b></td>
    <td> """+str(a22)+"""</td>
    <td> """+str(b22)+"""</td>
    <td> """+str(c22)+"""</td>
    <td> """+str(h22)+"""</td>
  </tr>
  <tr>
    <td><b>flipkart</b></td>
    <td> """+str(a33)+"""</td>
    <td> """+str(b33)+"""</td>
    <td> """+str(c33)+"""</td>
    <td> """+str(h33)+"""</td>
  </tr>
  <tr>
    <td><b>jabong</b></td>
    <td> """+str(a44)+"""</td>
    <td> """+str(b44)+"""</td>
    <td> """+str(c44)+"""</td>
    <td> """+str(h44)+"""</td>
  </tr>
  <tr>
    <td><b>myntra</b></td>
    <td> """+str(a55)+"""</td>
    <td> """+str(b55)+"""</td>
    <td> """+str(c55)+"""</td>
    <td> """+str(h55)+"""</td>
  </tr>
  <tr>
    <td><b>limerod</b></td>
    <td> """+str(a66)+"""</td>
    <td> """+str(b66)+"""</td>
    <td> """+str(c66)+"""</td>
    <td> """+str(h66)+"""</td>
  </tr>
  <tr>
    <td><b>tatacliq</b></td>
    <td> """+str(a77)+"""</td>
    <td> """+str(b77)+"""</td>
    <td> """+str(c77)+"""</td>
    <td> """+str(h77)+"""</td>
  </tr>
  <tr>
    <td><b>paytm</b></td>
    <td> """+str(a88)+"""</td>
    <td> """+str(b88)+"""</td>
    <td> """+str(c88)+"""</td>
    <td> """+str(h88)+"""</td>
  </tr>
  <tr>
    <td><b>cloudtail</b></td>
    <td> """+str(a99)+"""</td>
    <td> """+str(b99)+"""</td>
    <td> """+str(c99)+"""</td>
    <td> """+str(h99)+"""</td>
  </tr>
   <tr>
    <td><b>1mg</b></td>
    <td> """+str(a1010)+"""</td>
    <td> """+str(b1010)+"""</td>
    <td> """+str(c1010)+"""</td>
    <td> """+str(h1010)+"""</td>
  </tr>
   <tr>
    <td><b>bigbasket</b></td>
    <td> """+str(a1111)+"""</td>
    <td> """+str(b1111)+"""</td>
    <td> """+str(c1111)+"""</td>
    <td> """+str(h1111)+"""</td>
  </tr> 
  <tr>
    <td><b>pepperfry</b></td>
    <td> """+str(a1212)+"""</td>
    <td> """+str(b1212)+"""</td>
    <td> """+str(c1212)+"""</td>
    <td> """+str(h1212)+"""</td>
  </tr> 
  <tr>
    <td><b>firstcry</b></td>
    <td> """+str(a1313)+"""</td>
    <td> """+str(b1313)+"""</td>
    <td> """+str(c1313)+"""</td>
    <td> """+str(h1313)+"""</td>
  </tr>
  <tr>
    <td><b>mirraw</b></td>
    <td> """+str(a1414)+"""</td>
    <td> """+str(b1414)+"""</td>
    <td> """+str(c1414)+"""</td>
    <td> """+str(h1414)+"""</td>
  </tr>
  <tr>
    <td><b>nykaa fashion</b></td>
    <td> """+str(a1515)+"""</td>
    <td> """+str(b1515)+"""</td>
    <td> """+str(c1515)+"""</td>
    <td> """+str(h1515)+"""</td>
  </tr>
  <tr>
    <td><b>lbb</b></td>
    <td> """+str(a1616)+"""</td>
    <td> """+str(b1616)+"""</td>
    <td> """+str(c1616)+"""</td>
    <td> """+str(h1616)+"""</td>
  </tr>
  <tr>
    <td><b>amazon fba</b></td>
    <td> """+str(a1717)+"""</td>
    <td> """+str(b1717)+"""</td>
    <td> """+str(c1717)+"""</td>
    <td> """+str(h1717)+"""</td>
  </tr>
  <tr>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b>Sum total</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(a9999)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(b9999)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(c9999)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(h1818)+"""</b></td>
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

#***************************************************************************************************************************


# In[ ]:




