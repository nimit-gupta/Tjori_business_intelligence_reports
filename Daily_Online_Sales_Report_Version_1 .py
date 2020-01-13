#!/usr/bin/env python
# coding: utf-8

# In[7]:


# Importing libraries

import psycopg2 as ps
import pygsheets
import pandas as pd
import numpy as np
import xlsxwriter 
import datetime
import warnings
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import warnings
warnings.filterwarnings('ignore')

pd.options.display.float_format = '{0:,.0f}'.format

conn = ps.connect(user = 'nimit_new', password = 'nimit@tjori@123', host = '103.93.94.51', port = '5432', database = 'tjori_pd')

def clearance_sales(startdate, enddate):
    
    sql = '''
           SELECT
             DATE(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS order_date
            ,soi.order_id	 
            ,catalog.sku
            ,category.name
            ,CASE
                WHEN so.currency = 'USD' THEN 
			       CASE 
				      WHEN (((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) <= 999 THEN ROUND(((((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) - (((((soi.quanity * soi.price)*70) - (coalesce(soi.discount, 0) *70))*hsn.tax_under999::integer)/100)),2)
                      WHEN (((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) > 999 THEN ROUND(((((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) - (((((soi.quanity * soi.price)*70) - (coalesce(soi.discount, 0) *70))*hsn.tax::integer)/100)),2)
                   END 
                WHEN so.currency = 'INR' THEN 
			       CASE 
				      WHEN ((soi.quanity * soi.price) - coalesce(soi.discount,0)) <= 999 THEN ROUND((((soi.quanity * soi.price) - coalesce(soi.discount,0)) - ((((soi.quanity * soi.price) - coalesce(soi.discount,0))*hsn.tax_under999::integer)/100)),2)
                      WHEN ((soi.quanity * soi.price) - coalesce(soi.discount,0)) > 999 THEN ROUND((((soi.quanity * soi.price) - coalesce(soi.discount,0)) - ((((soi.quanity * soi.price) - coalesce(soi.discount,0))*hsn.tax::integer)/100)),2)
	               END
		      END AS revenue
             ,soi.quanity AS quantity
             ,ribbon.id
             ,ribbon.creative_text
            FROM 
                order_orderproduct soi
            LEFT JOIN 
                order_order so ON so.id = soi.order_id
            LEFT JOIN 
                store_product catalog ON soi.product_id = catalog.id   
            LEFT JOIN 
                store_ribbon ribbon ON catalog.ribbon_id = ribbon.id
            LEFT JOIN 
                store_category category ON catalog.category_id = category.id
            LEFT JOIN 
                tms_hsncode AS hsn ON catalog.hsncode_id = hsn.id
            WHERE 
              so.status = 'confirmed' AND
              ribbon.id = 3 AND 
              date(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') >= '%s' AND
              date(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') < '%s' AND
              soi.removed = False AND
              soi.returned = False AND
              soi.exchanged = False 
            GROUP BY
              order_date
             ,hsn.tax
             ,soi.price
             ,soi.quanity
             ,soi.discount
             ,catalog.sku
             ,category.name
             ,ribbon.id
             ,ribbon.creative_text
             ,soi.order_id
             ,so.currency
             ,hsn.tax_under999
;

''' % (
       startdate,
       enddate  
      )
    
    df1 = pd.read_sql_query(sql, conn)
    return df1

def non_clearance_sales(startdate, enddate):
    
    sql1 = '''
            SELECT
                DATE(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS order_date
                ,soi.order_id	 
                ,catalog.sku
                ,category.name
                ,CASE
                     WHEN so.currency = 'USD' THEN 
			             CASE 
				            WHEN (((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) <= 999 THEN ROUND(((((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) - (((((soi.quanity * soi.price)*70) - (coalesce(soi.discount, 0) *70))*hsn.tax_under999::integer)/100)),2)
                            WHEN (((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) > 999 THEN ROUND(((((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) - (((((soi.quanity * soi.price)*70) - (coalesce(soi.discount, 0) *70))*hsn.tax::integer)/100)),2)
                         END 
                     WHEN so.currency = 'INR' THEN 
			             CASE 
				            WHEN ((soi.quanity * soi.price) - coalesce(soi.discount,0)) <= 999 THEN ROUND((((soi.quanity * soi.price) - coalesce(soi.discount,0)) - ((((soi.quanity * soi.price) - coalesce(soi.discount,0))*hsn.tax_under999::integer)/100)),2)
                            WHEN ((soi.quanity * soi.price) - coalesce(soi.discount,0)) > 999 THEN ROUND((((soi.quanity * soi.price) - coalesce(soi.discount,0)) - ((((soi.quanity * soi.price) - coalesce(soi.discount,0))*hsn.tax::integer)/100)),2)
	                  END
		          END AS revenue
                 ,soi.quanity AS quantity
                 ,ribbon.id
                 ,ribbon.creative_text
             FROM 
                order_orderproduct soi
             LEFT JOIN 
                order_order so ON so.id = soi.order_id
             LEFT JOIN 
                store_product catalog ON soi.product_id = catalog.id   
             LEFT JOIN 
                store_ribbon ribbon ON catalog.ribbon_id = ribbon.id
             LEFT JOIN 
                store_category category ON catalog.category_id = category.id
             LEFT JOIN 
                tms_hsncode AS hsn ON catalog.hsncode_id = hsn.id
            WHERE 
              so.status = 'confirmed' AND
              ribbon.id IS DISTINCT FROM 3 AND 
              date(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') >= '%s' AND
              date(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') < '%s' AND
              soi.removed = False AND
              soi.returned = False AND
              soi.exchanged = False 
            GROUP BY
              order_date
             ,hsn.tax
             ,soi.price
             ,soi.quanity
             ,soi.discount
             ,catalog.sku
             ,category.name
             ,ribbon.id
             ,ribbon.creative_text
             ,soi.order_id
             ,so.currency
             ,hsn.tax_under999
          ;

          ''' % (
                 startdate,
                 enddate  
                )
    
    df2 = pd.read_sql_query(sql1, conn)
    return df2

def total_sales(startdate, enddate):
    
    sql2 = '''
            SELECT
                  DATE(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') AS order_date
                 ,soi.order_id	 
                 ,catalog.sku
                 ,category.name
                 ,CASE
                     WHEN so.currency = 'USD' THEN 
			            CASE 
				           WHEN (((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) <= 999 THEN ROUND(((((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) - (((((soi.quanity * soi.price)*70) - (coalesce(soi.discount, 0) *70))*hsn.tax_under999::integer)/100)),2)
                           WHEN (((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) > 999 THEN ROUND(((((soi.quanity * soi.price)*70) - (COALESCE(soi.discount, 0)*70)) - (((((soi.quanity * soi.price)*70) - (coalesce(soi.discount, 0) *70))*hsn.tax::integer)/100)),2)
                        END 
                      WHEN so.currency = 'INR' THEN 
			             CASE 
				            WHEN ((soi.quanity * soi.price) - coalesce(soi.discount,0)) <= 999 THEN ROUND((((soi.quanity * soi.price) - coalesce(soi.discount,0)) - ((((soi.quanity * soi.price) - coalesce(soi.discount,0))*hsn.tax_under999::integer)/100)),2)
                            WHEN ((soi.quanity * soi.price) - coalesce(soi.discount,0)) > 999 THEN ROUND((((soi.quanity * soi.price) - coalesce(soi.discount,0)) - ((((soi.quanity * soi.price) - coalesce(soi.discount,0))*hsn.tax::integer)/100)),2)
	                  END
		          END AS revenue
                 ,soi.quanity AS quantity
                 ,ribbon.id
                 ,ribbon.creative_text
             FROM 
                order_orderproduct soi
             LEFT JOIN 
                order_order so ON so.id = soi.order_id
             LEFT JOIN 
                store_product catalog ON soi.product_id = catalog.id   
             LEFT JOIN 
                store_ribbon ribbon ON catalog.ribbon_id = ribbon.id
             LEFT JOIN 
                store_category category ON catalog.category_id = category.id
             LEFT JOIN 
                tms_hsncode AS hsn ON catalog.hsncode_id = hsn.id
            WHERE 
              so.status = 'confirmed' AND
              date(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') >= '%s' AND
              date(soi.created::TIMESTAMP AT TIME ZONE 'utc' AT TIME ZONE 'asia/kolkata') < '%s' AND
              soi.removed = False AND
              soi.returned = False AND
              soi.exchanged = False 
            GROUP BY
              order_date
             ,hsn.tax
             ,soi.price
             ,soi.quanity
             ,soi.discount
             ,catalog.sku
             ,category.name
             ,ribbon.id
             ,ribbon.creative_text
             ,soi.order_id
             ,so.currency
             ,hsn.tax_under999
          ;

          ''' % (
                 startdate,
                 enddate  
                 )
    
    df3 = pd.read_sql_query(sql2, conn)
    return df3

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

if __name__ == '__main__':
    td = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    yd = (datetime.datetime.now() - datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    fd = (datetime.datetime.now() - datetime.timedelta(1)).replace(day=1,hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
    ydb = (datetime.datetime.now() - datetime.timedelta(2)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')


#Clearance Sales

#Yesterday

dfy = clearance_sales(yd,td) 

                                                 # Yesterday Quantity

dfa1 = dfy[dfy['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfa1.empty is True:
    dfa1a1 = '0'
else:
    dfa1a1 = dfa1.to_string(header = None, index = None)

dfa2 = dfy[dfy['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfa2.empty is True:
    dfa2a2 = '0'
else:
    dfa2a2 = dfa2.to_string(header = None, index = None)
    
dfa3 = dfy[dfy['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfa3.empty is True:
    dfa3a3 = '0'
else:
    dfa3a3 = dfa3.to_string(header = None, index = None)

dfa4 = dfy[dfy['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfa4.empty is True:
    dfa4a4 = '0'
else:
    dfa4a4 = dfa4.to_string(header = None, index = None)
    
dfa5 = dfy[dfy['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfa5.empty is True:
    dfa5a5 = '0'
else:
    dfa5a5 = dfa5.to_string(header = None, index = None)
    
dfa6 = dfy[dfy['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfa6.empty is True:
    dfa6a6 = '0'
else:
    dfa6a6 = dfa6.to_string(header = None, index = None)

dfa7 = dfy[dfy['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfa7.empty is True:
    dfa7a7 = '0'
else:
    dfa7a7 = dfa7.to_string(header = None, index = None)
    
dfa8 = dfy[dfy['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfa8.empty is True:
    dfa8a8 = '0'
else:
    dfa8a8 = dfa8.to_string(header = None, index = None)

dfa9 = dfy[dfy['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfa9.empty is True:
    dfa9a9 = '0'
else:
    dfa9a9 = dfa9.to_string(header = None, index = None)

                                         # Yesterday Revenue

dfa11 = dfy[dfy['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfa11.empty is True:
    dfa11a11 = '0'
else:
    dfa11a11 = dfa11.to_string(header = None, index = None)

dfa22 = dfy[dfy['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfa22.empty is True:
    dfa22a22 = '0'
else:
    dfa22a22 = dfa22.to_string(header = None, index = None)
    
dfa33 = dfy[dfy['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfa33.empty is True:
    dfa33a33 = '0'
else:
    dfa33a33 = dfa33.to_string(header = None, index = None)

dfa44 = dfy[dfy['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfa44.empty is True:
    dfa44a44 = '0'
else:
    dfa44a44 = dfa44.to_string(header = None, index = None)
    
dfa55 = dfy[dfy['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfa55.empty is True:
    dfa55a55 = '0'
else:
    dfa55a55 = dfa55.to_string(header = None, index = None)
    
dfa66 = dfy[dfy['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfa66.empty is True:
    dfa66a66 = '0'
else:
    dfa66a66 = dfa66.to_string(header = None, index = None)

dfa77 = dfy[dfy['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfa77.empty is True:
    dfa77a77 = '0'
else:
    dfa77a77 = dfa77.to_string(header = None, index = None)
    
dfa88 = dfy[dfy['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfa88.empty is True:
    dfa88a88 = '0'
else:
    dfa88a88 = dfa88.to_string(header = None, index = None)

dfa99 = dfy[dfy['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfa99.empty is True:
    dfa99a99 = '0'
else:
    dfa99a99 = dfa99.to_string(header = None, index = None)

    

                                               #Day before yesterday

dfyb = clearance_sales(ydb, yd)

                                           # Day before yesterday Quantity

dfb1 = dfyb[dfyb['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfb1.empty is True:
    dfb1b1 = '0'
else:
    dfb1b1 = dfb1.to_string(header = None, index = None)

dfb2 = dfyb[dfyb['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfb2.empty is True:
    dfb2b2 = '0'
else:
    dfb2b2 = dfb2.to_string(header = None, index = None)
    
dfb3 = dfyb[dfyb['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfb3.empty is True:
    dfb3b3 = '0'
else:
    dfb3b3 = dfb3.to_string(header = None, index = None)
    
dfb4 = dfyb[dfyb['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfb4.empty is True:
    dfb4b4 = '0'
else:
    dfb4b4 = dfb4.to_string(header = None, index = None)
    
dfb5 = dfyb[dfyb['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfb5.empty is True:
    dfb5b5 = '0'
else:
    dfb5b5 = dfb5.to_string(header = None, index = None)

dfb6 = dfyb[dfyb['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfb6.empty is True:
    dfb6b6 = '0'
else:
    dfb6b6 = dfb6.to_string(header = None, index = None)
    
dfb7 = dfyb[dfyb['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfb7.empty is True:
    dfb7b7 = '0'
else:
    dfb7b7 = dfb7.to_string(header = None, index = None)
    
dfb8 = dfyb[dfyb['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfb8.empty is True:
    dfb8b8 = '0'
else:
    dfb8b8 = dfb8.to_string(header = None, index = None)

dfb9 = dfyb[dfyb['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfb9.empty is True:
    dfb9b9 = '0'
else:
    dfb9b9 = dfb9.to_string(header = None, index = None)

    
                                     # Day before yesterday Revenue

dfb11 = dfyb[dfyb['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfb11.empty is True:
    dfb11b11 = '0'
else:
    dfb11b11 = dfb11.to_string(header = None, index = None)

dfb22 = dfyb[dfyb['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfb22.empty is True:
    dfb22b22 = '0'
else:
    dfb22b22 = dfb22.to_string(header = None, index = None)
    
dfb33 = dfyb[dfyb['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfb33.empty is True:
    dfb33b33 = '0'
else:
    dfb33b33 = dfb33.to_string(header = None, index = None)
    
dfb44 = dfyb[dfyb['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfb44.empty is True:
    dfb44b44 = '0'
else:
    dfb44b44 = dfb44.to_string(header = None, index = None)
    
dfb55 = dfyb[dfyb['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfb55.empty is True:
    dfb55b55 = '0'
else:
    dfb55b55 = dfb55.to_string(header = None, index = None)
    
dfb66 = dfyb[dfyb['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfb66.empty is True:
    dfb66b66 = '0'
else:
    dfb66b66 = dfb66.to_string(header = None, index = None)
    
dfb77 = dfyb[dfyb['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfb77.empty is True:
    dfb77b77 = '0'
else:
    dfb77b77 = dfb77.to_string(header = None, index = None)
    
dfb88 = dfyb[dfyb['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfb88.empty is True:
    dfb88b88 = '0'
else:
    dfb88b88 = dfb88.to_string(header = None, index = None)

dfb99 = dfyb[dfyb['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfb99.empty is True:
    dfb99b99 = '0'
else:
    dfb99b99 = dfb99.to_string(header = None, index = None)
    
                                                #Month Till Date

dfmtd = clearance_sales(fd, td)

                                             #Month till Date Quantity

dfc1 = dfmtd[dfmtd['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfc1.empty is True:
    dfc1c1 = '0'
else:
    dfc1c1 = dfc1.to_string(header = None, index = None)

dfc2 = dfmtd[dfmtd['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfc2.empty is True:
    dfc2c2 = '0'
else:
    dfc2c2 = dfc2.to_string(header = None, index = None)
    
dfc3 = dfmtd[dfmtd['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfc3.empty is True:
    dfc3c3 = '0'
else:
    dfc3c3 = dfc3.to_string(header = None, index = None)
    
dfc4 = dfmtd[dfmtd['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfc4.empty is True:
    dfc4c4 = '0'
else:
    dfc4c4 = dfc4.to_string(header = None, index = None)
    
dfc5 = dfmtd[dfmtd['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfc5.empty is True:
    dfc5c5 = '0'
else:
    dfc5c5 = dfc5.to_string(header = None, index = None)
    
dfc6 = dfmtd[dfmtd['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfc6.empty is True:
    dfc6c6 = '0'
else:
    dfc6c6 = dfc6.to_string(header = None, index = None)
    
dfc7 = dfmtd[dfmtd['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfc7.empty is True:
    dfc7c7 = '0'
else:
    dfc7c7 = dfc7.to_string(header = None, index = None)
    
dfc8 = dfmtd[dfmtd['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfc8.empty is True:
    dfc8c8 = '0'
else:
    dfc8c8 = dfc8.to_string(header = None, index = None)
    
dfc9 = dfmtd[dfmtd['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfc9.empty is True:
    dfc9c9 = '0'
else:
    dfc9c9 = dfc9.to_string(header = None, index = None)
    
    
                                          # Month Till Date Revenue

dfc11 = dfmtd[dfmtd['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfc11.empty is True:
    dfc11c11 = '0'
else:
    dfc11c11 = dfc11.to_string(header = None, index = None)

dfc22 = dfmtd[dfmtd['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfc22.empty is True:
    dfc22c22 = '0'
else:
    dfc22c22 = dfc22.to_string(header = None, index = None)
    
dfc33 = dfmtd[dfmtd['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfc33.empty is True:
    dfc33c33 = '0'
else:
    dfc33c33 = dfc33.to_string(header = None, index = None)
    
dfc44 = dfmtd[dfmtd['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfc44.empty is True:
    dfc44c44 = '0'
else:
    dfc44c44 = dfc44.to_string(header = None, index = None)
    
dfc55 = dfmtd[dfmtd['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfc55.empty is True:
    dfc55c55 = '0'
else:
    dfc55c55 = dfc55.to_string(header = None, index = None)
    
dfc66 = dfmtd[dfmtd['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfc66.empty is True:
    dfc66c66 = '0'
else:
    dfc66c66 = dfc66.to_string(header = None, index = None)
    
dfc77 = dfmtd[dfmtd['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfc77.empty is True:
    dfc77c77 = '0'
else:
    dfc77c77 = dfc77.to_string(header = None, index = None)
    
dfc88 = dfmtd[dfmtd['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfc88.empty is True:
    dfc88c88 = '0'
else:
    dfc88c88 = dfc88.to_string(header = None, index = None)
    
dfc99 = dfmtd[dfmtd['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfc99.empty is True:
    dfc99c99 = '0'
else:
    dfc99c99 = dfc99.to_string(header = None, index = None)
    
                                                    #Non Clearance Sale

                                                        #Yesterday

dfy1 = non_clearance_sales(yd,td) 

                                                     # Yesterday Quantity

dfa1x1 = dfy1[dfy1['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfa1x1.empty is True:
    dfa1a1x1 = '0'
else:
    dfa1a1x1 = dfa1x1.to_string(header = None, index = None)

dfa2x2 = dfy1[dfy1['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfa2x2.empty is True:
    dfa2a2x2 = '0'
else:
    dfa2a2x2 = dfa2x2.to_string(header = None, index = None)
    
dfa3x3 = dfy1[dfy1['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfa3x3.empty is True:
    dfa3a3x3 = '0'
else:
    dfa3a3x3 = dfa3x3.to_string(header = None, index = None)

dfa4x4 = dfy1[dfy1['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfa4x4.empty is True:
    dfa4a4x4 = '0'
else:
    dfa4a4x4 = dfa4x4.to_string(header = None, index = None)
    
dfa5x5 = dfy1[dfy1['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfa5x5.empty is True:
    dfa5a5x5 = '0'
else:
    dfa5a5x5 = dfa5x5.to_string(header = None, index = None)
    
dfa6x6 = dfy1[dfy1['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfa6x6.empty is True:
    dfa6a6x6 = '0'
else:
    dfa6a6x6 = dfa6x6.to_string(header = None, index = None)

dfa7x7 = dfy1[dfy1['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfa7x7.empty is True:
    dfa7a7x7 = '0'
else:
    dfa7a7x7 = dfa7x7.to_string(header = None, index = None)
    
dfa8x8 = dfy1[dfy1['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfa8x8.empty is True:
    dfa8a8x8 = '0'
else:
    dfa8a8x8 = dfa8x8.to_string(header = None, index = None)

dfa9x9 = dfy1[dfy1['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfa9x9.empty is True:
    dfa9a9x9 = '0'
else:
    dfa9a9x9 = dfa9x9.to_string(header = None, index = None)
    
                                               # Yesterday Revenue

dfa11x11 = dfy1[dfy1['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfa11x11.empty is True:
    dfa11a11x11 = '0'
else:
    dfa11a11x11 = dfa11x11.to_string(header = None, index = None)

dfa22x22 = dfy1[dfy1['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfa22x22.empty is True:
    dfa22a22x22 = '0'
else:
    dfa22a22x22 = dfa22x22.to_string(header = None, index = None)
    
dfa33x33 = dfy1[dfy1['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfa33x33.empty is True:
    dfa33a33x33 = '0'
else:
    dfa33a33x33 = dfa33x33.to_string(header = None, index = None)

dfa44x44 = dfy1[dfy1['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfa44x44.empty is True:
    dfa44a44x44 = '0'
else:
    dfa44a44x44 = dfa44x44.to_string(header = None, index = None)
    
dfa55x55 = dfy1[dfy1['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfa55x55.empty is True:
    dfa55a55x55 = '0'
else:
    dfa55a55x55 = dfa55x55.to_string(header = None, index = None)
    
dfa66x66 = dfy1[dfy1['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfa66x66.empty is True:
    dfa66a66x66 = '0'
else:
    dfa66a66x66 = dfa66x66.to_string(header = None, index = None)

dfa77x77 = dfy1[dfy1['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfa77x77.empty is True:
    dfa77a77x77 = '0'
else:
    dfa77a77x77 = dfa77x77.to_string(header = None, index = None)
    
dfa88x88 = dfy1[dfy1['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfa88x88.empty is True:
    dfa88a88x88 = '0'
else:
    dfa88a88x88 = dfa88x88.to_string(header = None, index = None)

dfa99x99 = dfy1[dfy1['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfa99x99.empty is True:
    dfa99a99x99 = '0'
else:
    dfa99a99x99 = dfa99x99.to_string(header = None, index = None)
    
    
                                              #Day before yesterday

dfyb1 = non_clearance_sales(ydb, yd)

                                        # Day before yesterday Quantity

dfb1x1 = dfyb1[dfyb1['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfb1x1.empty is True:
    dfb1b1x1 = '0'
else:
    dfb1b1x1 = dfb1x1.to_string(header = None, index = None)

dfb2x2 = dfyb1[dfyb1['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfb2x2.empty is True:
    dfb2b2x2 = '0'
else:
    dfb2b2x2 = dfb2x2.to_string(header = None, index = None)
    
dfb3x3 = dfyb1[dfyb1['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfb3x3.empty is True:
    dfb3b3x3 = '0'
else:
    dfb3b3x3 = dfb3x3.to_string(header = None, index = None)
    
dfb4x4 = dfyb1[dfyb1['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfb4x4.empty is True:
    dfb4b4x4 = '0'
else:
    dfb4b4x4 = dfb4x4.to_string(header = None, index = None)
    
dfb5x5 = dfyb1[dfyb1['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfb5x5.empty is True:
    dfb5b5x5 = '0'
else:
    dfb5b5x5 = dfb5x5.to_string(header = None, index = None)

dfb6x6 = dfyb1[dfyb1['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfb6x6.empty is True:
    dfb6b6x6 = '0'
else:
    dfb6b6x6 = dfb6x6.to_string(header = None, index = None)
    
dfb7x7 = dfyb1[dfyb1['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfb7x7.empty is True:
    dfb7b7x7 = '0'
else:
    dfb7b7x7 = dfb7x7.to_string(header = None, index = None)
    
dfb8x8 = dfyb1[dfyb1['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfb8x8.empty is True:
    dfb8b8x8 = '0'
else:
    dfb8b8x8 = dfb8x8.to_string(header = None, index = None)

dfb9x9 = dfyb1[dfyb1['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfb9x9.empty is True:
    dfb9b9x9 = '0'
else:
    dfb9b9x9 = dfb9x9.to_string(header = None, index = None)

        
                                        # Day before yesterday Quantity

dfb11x11 = dfyb1[dfyb1['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfb11x11.empty is True:
    dfb11b11x11 = '0'
else:
    dfb11b11x11 = dfb11x11.to_string(header = None, index = None)

dfb22x22 = dfyb1[dfyb1['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfb22x22.empty is True:
    dfb22b22x22 = '0'
else:
    dfb22b22x22 = dfb22x22.to_string(header = None, index = None)
    
dfb33x33 = dfyb1[dfyb1['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfb33x33.empty is True:
    dfb33b33x33 = '0'
else:
    dfb33b33x33 = dfb33x33.to_string(header = None, index = None)
    
dfb44x44 = dfyb1[dfyb1['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfb44x44.empty is True:
    dfb44b44x44 = '0'
else:
    dfb44b44x44 = dfb44x44.to_string(header = None, index = None)
    
dfb55x55 = dfyb1[dfyb1['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfb55x55.empty is True:
    dfb55b55x55 = '0'
else:
    dfb55b55x55 = dfb55x55.to_string(header = None, index = None)
    
dfb66x66 = dfyb1[dfyb1['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfb66x66.empty is True:
    dfb66b66x66 = '0'
else:
    dfb66b66x66 = dfb66x66.to_string(header = None, index = None)
    
dfb77x77 = dfyb1[dfyb1['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfb77x77.empty is True:
    dfb77b77x77 = '0'
else:
    dfb77b77x77 = dfb77x77.to_string(header = None, index = None)
    
dfb88x88 = dfyb1[dfyb1['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfb88x88.empty is True:
    dfb88b88x88 = '0'
else:
    dfb88b88x88 = dfb88x88.to_string(header = None, index = None)

dfb99x99 = dfyb1[dfyb1['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfb99x99.empty is True:
    dfb99b99x99 = '0'
else:
    dfb99b99x99 = dfb99x99.to_string(header = None, index = None)
    
    
                                                #Month Till Date

dfmtd1 = non_clearance_sales(fd, td)

                                             #Month till Date Quantity

dfc1x1 = dfmtd1[dfmtd1['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfc1x1.empty is True:
    dfc1c1x1 = '0'
else:
    dfc1c1x1 = dfc1x1.to_string(header = None, index = None)

dfc2x2 = dfmtd1[dfmtd1['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfc2x2.empty is True:
    dfc2c2x2 = '0'
else:
    dfc2c2x2 = dfc2x2.to_string(header = None, index = None)
    
dfc3x3 = dfmtd1[dfmtd1['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfc3x3.empty is True:
    dfc3c3x3 = '0'
else:
    dfc3c3x3 = dfc3x3.to_string(header = None, index = None)
    
dfc4x4 = dfmtd1[dfmtd1['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfc4x4.empty is True:
    dfc4c4x4 = '0'
else:
    dfc4c4x4 = dfc4x4.to_string(header = None, index = None)
    
dfc5x5 = dfmtd1[dfmtd1['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfc5x5.empty is True:
    dfc5c5x5 = '0'
else:
    dfc5c5x5 = dfc5x5.to_string(header = None, index = None)
    
dfc6x6 = dfmtd1[dfmtd1['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfc6x6.empty is True:
    dfc6c6x6 = '0'
else:
    dfc6c6x6 = dfc6x6.to_string(header = None, index = None)
    
dfc7x7 = dfmtd1[dfmtd1['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfc7x7.empty is True:
    dfc7c7x7 = '0'
else:
    dfc7c7x7 = dfc7x7.to_string(header = None, index = None)
    
dfc8x8 = dfmtd1[dfmtd1['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfc8x8.empty is True:
    dfc8c8x8 = '0'
else:
    dfc8c8x8 = dfc8x8.to_string(header = None, index = None)
    
dfc9x9 = dfmtd1[dfmtd1['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfc9x9.empty is True:
    dfc9c9x9 = '0'
else:
    dfc9c9x9 = dfc9x9.to_string(header = None, index = None)
    
    
                                         # Month Till Date Revenue

dfc11x11 = dfmtd1[dfmtd1['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfc11x11.empty is True:
    dfc11c11x11 = '0'
else:
    dfc11c11x11 = dfc11x11.to_string(header = None, index = None)

dfc22x22 = dfmtd1[dfmtd1['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfc22x22.empty is True:
    dfc22c22x22 = '0'
else:
    dfc22c22x22 = dfc22x22.to_string(header = None, index = None)
    
dfc33x33 = dfmtd1[dfmtd1['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfc33x33.empty is True:
    dfc33c33x33 = '0'
else:
    dfc33c33x33 = dfc33x33.to_string(header = None, index = None)
    
dfc44x44 = dfmtd1[dfmtd1['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfc44x44.empty is True:
    dfc44c44x44 = '0'
else:
    dfc44c44x44 = dfc44x44.to_string(header = None, index = None)
    
dfc55x55 = dfmtd1[dfmtd1['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfc55x55.empty is True:
    dfc55c55x55 = '0'
else:
    dfc55c55x55 = dfc55x55.to_string(header = None, index = None)
    
dfc66x66 = dfmtd1[dfmtd1['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfc66x66.empty is True:
    dfc66c66x66 = '0'
else:
    dfc66c66x66 = dfc66x66.to_string(header = None, index = None)
    
dfc77x77 = dfmtd1[dfmtd1['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfc77x77.empty is True:
    dfc77c77x77 = '0'
else:
    dfc77c77x77 = dfc77x77.to_string(header = None, index = None)
    
dfc88x88 = dfmtd1[dfmtd1['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfc88x88.empty is True:
    dfc88c88x88 = '0'
else:
    dfc88c88x88 = dfc88x88.to_string(header = None, index = None)
    
dfc99x99 = dfmtd1[dfmtd1['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfc99x99.empty is True:
    dfc99c99x99 = '0'
else:
    dfc99c99x99 = dfc99x99.to_string(header = None, index = None)
    
                                                #Total Sales

                                                 #Yesterday

dfy2 = total_sales(yd,td) 

# Yesterday Quantity

dfa1y1 = dfy2[dfy2['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfa1y1.empty is True:
    dfa1a1y1 = '0'
else:
    dfa1a1y1 = dfa1y1.to_string(header = None, index = None)

dfa2y2 = dfy2[dfy2['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfa2y2.empty is True:
    dfa2a2y2 = '0'
else:
    dfa2a2y2 = dfa2y2.to_string(header = None, index = None)
    
dfa3y3 = dfy2[dfy2['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfa3y3.empty is True:
    dfa3a3y3 = '0'
else:
    dfa3a3y3 = dfa3y3.to_string(header = None, index = None)

dfa4y4 = dfy2[dfy2['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfa4y4.empty is True:
    dfa4a4y4 = '0'
else:
    dfa4a4y4 = dfa4y4.to_string(header = None, index = None)
    
dfa5y5 = dfy2[dfy2['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfa5y5.empty is True:
    dfa5a5y5 = '0'
else:
    dfa5a5y5 = dfa5y5.to_string(header = None, index = None)
    
dfa6y6 = dfy2[dfy2['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfa6y6.empty is True:
    dfa6a6y6= '0'
else:
    dfa6a6y6 = dfa6y6.to_string(header = None, index = None)

dfa7y7 = dfy2[dfy2['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfa7y7.empty is True:
    dfa7a7y7 = '0'
else:
    dfa7a7y7 = dfa7y7.to_string(header = None, index = None)
    
dfa8y8 = dfy2[dfy2['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfa8y8.empty is True:
    dfa8a8y8 = '0'
else:
    dfa8a8y8 = dfa8y8.to_string(header = None, index = None)

dfa9y9 = dfy2[dfy2['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfa9y9.empty is True:
    dfa9a9y9 = '0'
else:
    dfa9a9y9 = dfa9y9.to_string(header = None, index = None)


                                           # Yesterday Revenue

dfa11y11 = dfy2[dfy2['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfa11y11.empty is True:
    dfa11a11y11 = '0'
else:
    dfa11a11y11 = dfa11y11.to_string(header = None, index = None)

dfa22y22 = dfy2[dfy2['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfa22y22.empty is True:
    dfa22a22y22 = '0'
else:
    dfa22a22y22 = dfa22y22.to_string(header = None, index = None)
    
dfa33y33 = dfy2[dfy2['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfa33y33.empty is True:
    dfa33a33y33 = '0'
else:
    dfa33a33y33 = dfa33y33.to_string(header = None, index = None)

dfa44y44 = dfy2[dfy2['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfa44y44.empty is True:
    dfa44a44y44 = '0'
else:
    dfa44a44y44 = dfa44y44.to_string(header = None, index = None)
    
dfa55y55 = dfy2[dfy2['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfa55y55.empty is True:
    dfa55a55y55 = '0'
else:
    dfa55a55y55 = dfa55y55.to_string(header = None, index = None)
    
dfa66y66 = dfy2[dfy2['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfa66y66.empty is True:
    dfa66a66y66 = '0'
else:
    dfa66a66y66 = dfa66y66.to_string(header = None, index = None)

dfa77y77 = dfy2[dfy2['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfa77y77.empty is True:
    dfa77a77y77 = '0'
else:
    dfa77a77y77 = dfa77y77.to_string(header = None, index = None)
    
dfa88y88 = dfy2[dfy2['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfa88y88.empty is True:
    dfa88a88y88 = '0'
else:
    dfa88a88y88 = dfa88y88.to_string(header = None, index = None)

dfa99y99 = dfy2[dfy2['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfa99y99.empty is True:
    dfa99a99y99 = '0'
else:
    dfa99a99y99 = dfa99y99.to_string(header = None, index = None)
    
    
                                                   #Day before yesterday

dfyb2 = total_sales(ydb, yd)

                                                # Day before yesterday Quantity

dfb1y1 = dfyb2[dfyb2['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfb1y1.empty is True:
    dfb1b1y1 = '0'
else:
    dfb1b1y1 = dfb1y1.to_string(header = None, index = None)

dfb2y2 = dfyb2[dfyb2['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfb2y2.empty is True:
    dfb2b2y2 = '0'
else:
    dfb2b2y2 = dfb2y2.to_string(header = None, index = None)
    
dfb3y3 = dfyb2[dfyb2['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfb3y3.empty is True:
    dfb3b3y3 = '0'
else:
    dfb3b3y3 = dfb3y3.to_string(header = None, index = None)
    
dfb4y4 = dfyb2[dfyb2['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfb4y4.empty is True:
    dfb4b4y4 = '0'
else:
    dfb4b4y4 = dfb4y4.to_string(header = None, index = None)
    
dfb5y5 = dfyb2[dfyb2['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfb5y5.empty is True:
    dfb5b5y5 = '0'
else:
    dfb5b5y5 = dfb5y5.to_string(header = None, index = None)

dfb6y6 = dfyb2[dfyb2['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfb6y6.empty is True:
    dfb6b6y6 = '0'
else:
    dfb6b6y6 = dfb6y6.to_string(header = None, index = None)
    
dfb7y7 = dfyb2[dfyb2['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfb7y7.empty is True:
    dfb7b7y7 = '0'
else:
    dfb7b7y7 = dfb7y7.to_string(header = None, index = None)
    
dfb8y8 = dfyb2[dfyb2['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfb8y8.empty is True:
    dfb8b8y8 = '0'
else:
    dfb8b8y8 = dfb8y8.to_string(header = None, index = None)

dfb9y9 = dfyb2[dfyb2['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfb9y9.empty is True:
    dfb9b9y9 = '0'
else:
    dfb9b9y9 = dfb9y9.to_string(header = None, index = None)

                                              # Day before yesterday Quantity

dfb11y11 = dfyb2[dfyb2['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfb11y11.empty is True:
    dfb11b11y11 = '0'
else:
    dfb11b11y11 = dfb11y11.to_string(header = None, index = None)

dfb22y22 = dfyb2[dfyb2['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfb22y22.empty is True:
    dfb22b22y22 = '0'
else:
    dfb22b22y22 = dfb22y22.to_string(header = None, index = None)
    
dfb33y33 = dfyb2[dfyb2['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfb33y33.empty is True:
    dfb33b33y33 = '0'
else:
    dfb33b33y33 = dfb33y33.to_string(header = None, index = None)
    
dfb44y44 = dfyb2[dfyb2['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfb44y44.empty is True:
    dfb44b44y44 = '0'
else:
    dfb44b44y44 = dfb44y44.to_string(header = None, index = None)
    
dfb55y55 = dfyb2[dfyb2['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfb55y55.empty is True:
    dfb55b55y55 = '0'
else:
    dfb55b55y55 = dfb55y55.to_string(header = None, index = None)
    
dfb66y66 = dfyb2[dfyb2['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfb66y66.empty is True:
    dfb66b66y66 = '0'
else:
    dfb66b66y66 = dfb66y66.to_string(header = None, index = None)
    
dfb77y77 = dfyb2[dfyb2['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfb77y77.empty is True:
    dfb77b77y77 = '0'
else:
    dfb77b77y77 = dfb77y77.to_string(header = None, index = None)
    
dfb88y88 = dfyb2[dfyb2['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfb88y88.empty is True:
    dfb88b88y88 = '0'
else:
    dfb88b88y88 = dfb88y88.to_string(header = None, index = None)

dfb99y99 = dfyb2[dfyb2['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfb99y99.empty is True:
    dfb99b99y99 = '0'
else:
    dfb99b99y99 = dfb99y99.to_string(header = None, index = None)


                                                   #Month Till Date

dfmtd2 = total_sales(fd, td)

#Month till Date Quantity

dfc1y1 = dfmtd2[dfmtd2['name'] == 'Apparel'].groupby('name').aggregate({'quantity': np.sum})
if dfc1y1.empty is True:
    dfc1c1y1 = '0'
else:
    dfc1c1y1 = dfc1y1.to_string(header = None, index = None)

dfc2y2 = dfmtd2[dfmtd2['name'] == 'Bags'].groupby('name').aggregate({'quantity': np.sum})
if dfc2y2.empty is True:
    dfc2c2y2 = '0'
else:
    dfc2c2y2 = dfc2y2.to_string(header = None, index = None)
    
dfc3y3 = dfmtd2[dfmtd2['name'] == 'Footwear'].groupby('name').aggregate({'quantity': np.sum})
if dfc3y3.empty is True:
    dfc3c3y3 = '0'
else:
    dfc3c3y3 = dfc3y3.to_string(header = None, index = None)
    
dfc4y4 = dfmtd2[dfmtd2['name'] == 'Home & Decor'].groupby('name').aggregate({'quantity': np.sum})
if dfc4y4.empty is True:
    dfc4c4y4 = '0'
else:
    dfc4c4y4 = dfc4y4.to_string(header = None, index = None)
    
dfc5y5 = dfmtd2[dfmtd2['name'] == 'Jewelry'].groupby('name').aggregate({'quantity': np.sum})
if dfc5y5.empty is True:
    dfc5c5y5 = '0'
else:
    dfc5c5y5 = dfc5y5.to_string(header = None, index = None)
    
dfc6y6 = dfmtd2[dfmtd2['name'] == 'Wellness'].groupby('name').aggregate({'quantity': np.sum})
if dfc6y6.empty is True:
    dfc6c6y6 = '0'
else:
    dfc6c6y6 = dfc6y6.to_string(header = None, index = None)
    
dfc7y7 = dfmtd2[dfmtd2['name'] == 'Accessories'].groupby('name').aggregate({'quantity': np.sum})
if dfc7y7.empty is True:
    dfc7c7y7 = '0'
else:
    dfc7c7y7 = dfc7y7.to_string(header = None, index = None)
    
dfc8y8 = dfmtd2[dfmtd2['name'] == 'Mother & Child'].groupby('name').aggregate({'quantity': np.sum})
if dfc8y8.empty is True:
    dfc8c8y8 = '0'
else:
    dfc8c8y8 = dfc8y8.to_string(header = None, index = None)
    
dfc9y9 = dfmtd2[dfmtd2['name'] == 'Men'].groupby('name').aggregate({'quantity': np.sum})
if dfc9y9.empty is True:
    dfc9c9y9 = '0'
else:
    dfc9c9y9 = dfc9y9.to_string(header = None, index = None)
    
    
    
                                            # Month Till Date Revenue

dfc11y11 = dfmtd2[dfmtd2['name'] == 'Apparel'].groupby('name').aggregate({'revenue': np.sum})
if dfc11y11.empty is True:
    dfc11c11y11 = '0'
else:
    dfc11c11y11 = dfc11y11.to_string(header = None, index = None)

dfc22y22 = dfmtd2[dfmtd2['name'] == 'Bags'].groupby('name').aggregate({'revenue': np.sum})
if dfc22y22.empty is True:
    dfc22c22y22 = '0'
else:
    dfc22c22y22 = dfc22y22.to_string(header = None, index = None)
    
dfc33y33 = dfmtd2[dfmtd2['name'] == 'Footwear'].groupby('name').aggregate({'revenue': np.sum})
if dfc33y33.empty is True:
    dfc33c33y33 = '0'
else:
    dfc33c33y33 = dfc33y33.to_string(header = None, index = None)
    
dfc44y44 = dfmtd2[dfmtd2['name'] == 'Home & Decor'].groupby('name').aggregate({'revenue': np.sum})
if dfc44y44.empty is True:
    dfc44c44y44 = '0'
else:
    dfc44c44y44 = dfc44y44.to_string(header = None, index = None)
    
dfc55y55 = dfmtd2[dfmtd2['name'] == 'Jewelry'].groupby('name').aggregate({'revenue': np.sum})
if dfc55y55.empty is True:
    dfc55c55y55 = '0'
else:
    dfc55c55y55 = dfc55y55.to_string(header = None, index = None)
    
dfc66y66 = dfmtd2[dfmtd2['name'] == 'Wellness'].groupby('name').aggregate({'revenue': np.sum})
if dfc66y66.empty is True:
    dfc66c66y66 = '0'
else:
    dfc66c66y66 = dfc66y66.to_string(header = None, index = None)
    
dfc77y77 = dfmtd2[dfmtd2['name'] == 'Accessories'].groupby('name').aggregate({'revenue': np.sum})
if dfc77y77.empty is True:
    dfc77c77y77 = '0'
else:
    dfc77c77y77 = dfc77y77.to_string(header = None, index = None)
    
dfc88y88 = dfmtd2[dfmtd2['name'] == 'Mother & Child'].groupby('name').aggregate({'revenue': np.sum})
if dfc88y88.empty is True:
    dfc88c88y88 = '0'
else:
    dfc88c88y88 = dfc88y88.to_string(header = None, index = None)
    
dfc99y99 = dfmtd2[dfmtd2['name'] == 'Men'].groupby('name').aggregate({'revenue': np.sum})
if dfc99y99.empty is True:
    dfc99c99y99 = '0'
else:
    dfc99c99y99 = dfc99y99.to_string(header = None, index = None)
    
    
                                                #Clearance Sale Sum Totals

                                                   #Sum Total Quantity

x1x1 =  dfy['quantity'].sum()
x11x11 = int(x1x1)

x2x2 = dfyb['quantity'].sum()
x22x22 = int(x2x2)

x3x3 = dfmtd['quantity'].sum()
x33x33 = int(x3x3)

                                                     # Sum Total Revenue

y1y1 =   dfy['revenue'].sum()
y11y11 = format(int(y1y1),",d")
    
y2y2 = dfyb['revenue'].sum()
y22y22 = format(int(y2y2),",d")

y3y3 = dfmtd['revenue'].sum()
y33y33 = format(int(y3y3),",d")

                                                  #Non Clearance Sales Sum total

                                                     #Sum Total Quantity

x1x1x1 =  dfy1['quantity'].sum()
x11x11x11 = int(x1x1x1)

x2x2x2 = dfyb1['quantity'].sum()
x22x22x22 = int(x2x2x2)

x3x3x3 = dfmtd1['quantity'].sum()
x33x33x33 = int(x3x3x3)

                                                      #Sum Total Revenue

y1y1y1 =   dfy1['revenue'].sum()
y11y11y11 = format(int(y1y1y1),",d")
    
y2y2y2 = dfyb1['revenue'].sum()
y22y22y22 = format(int(y2y2y2),",d")

y3y3y3 = dfmtd1['revenue'].sum()
y33y33y33 = format(int(y3y3y3),",d")

                                                     #Total Sales Sum total

                                                       #Sum Total Quantity

x1x1x1x1 =  dfy2['quantity'].sum()
x11x11x11x11 = int(x1x1x1x1)

x2x2x2x2 = dfyb2['quantity'].sum()
x22x22x22x22 = int(x2x2x2x2)

x3x3x3x3 = dfmtd2['quantity'].sum()
x33x33x33x33 = int(x3x3x3x3)

                                                        #Sum Total Revenue

y1y1y1y1 =   dfy2['revenue'].sum()
y11y11y11y11 = format(int(y1y1y1y1),",d")
    
y2y2y2y2 = dfyb2['revenue'].sum()
y22y22y22y22 = format(int(y2y2y2y2),",d")

y3y3y3y3 = dfmtd2['revenue'].sum()
y33y33y33y33 = format(int(y3y3y3y3),",d")

# Initiating the STMP

sender = "nimit@tjori.com"
recievers = [
               "nimit@tjori.com"
              ,"ankit@tjori.com"
              ,"mansi@tjori.com"
              ,"poonam@tjori.com"
              ,"shiv@tjori.com"
              ,"anand@tjori.com"
            ]

# Create message container - 
msg = MIMEMultipart('alternative')
msg['Subject'] = "Daily Online Sales Report"
msg['From'] = sender
msg['To'] = ",".join(recievers)

# Create the body of the message - 
html = """<html>
  <head>
  <p><b>Clearance Sales</b></p> 
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
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Date </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;">""" + str(df_1_1) + """</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;">""" + str(df_2_2) + """</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> MTD </th>
  </tr>
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Category Name </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
  </tr>
  <tr>
    <td><b>Apparel</b></td>
    <td>""" + str(dfa1a1) + """</td>
    <td>""" + str(dfa11a11) + """</td>
    <td>""" + str(dfb1b1) + """</td>
    <td>""" + str(dfb11b11) + """</td>
    <td>""" + str(dfc1c1) + """</td>
    <td>""" + str(dfc11c11) + """</td>
  </tr>
  <tr>
    <td><b>Bags</b></td>
    <td>""" + str(dfa2a2) + """</td>
    <td>""" + str(dfa22a22) + """</td>
    <td>""" + str(dfb2b2) + """</td>
    <td>""" + str(dfb22b22) + """</td>
    <td>""" + str(dfc2c2) + """</td>
    <td>""" + str(dfc22c22) + """</td>
  </tr>
  <tr>
    <td><b>Footwear</b></td>
    <td>""" + str(dfa3a3) + """</td>
    <td>""" + str(dfa33a33) + """</td>
    <td>""" + str(dfb3b3) + """</td>
    <td>""" + str(dfb33b33) + """</td>
    <td>""" + str(dfc3c3) + """</td>
    <td>""" + str(dfc33c33) + """</td>
  </tr>
  <tr>
    <td><b>Home & Decor</b></td>
    <td>""" + str(dfa4a4) + """</td>
    <td>""" + str(dfa44a44) + """</td>
    <td>""" + str(dfb4b4) + """</td>
    <td>""" + str(dfb44b44) + """</td>
    <td>""" + str(dfc4c4) + """</td>
    <td>""" + str(dfc44c44) + """</td>
  </tr>
  <tr>
    <td><b>Jewelry</b></td>
    <td>""" + str(dfa5a5) + """</td>
    <td>""" + str(dfa55a55) + """</td>
    <td>""" + str(dfb5b5) + """</td>
    <td>""" + str(dfb55b55) + """</td>
    <td>""" + str(dfc5c5) + """</td>
    <td>""" + str(dfc55c55) + """</td>
  </tr>
  <tr>
    <td><b>Wellness</b></td>
    <td>""" + str(dfa6a6) + """</td>
    <td>""" + str(dfa66a66) + """</td>
    <td>""" + str(dfb6b6) + """</td>
    <td>""" + str(dfb66b66) + """</td>
    <td>""" + str(dfc6c6) + """</td>
    <td>""" + str(dfc66c66) + """</td>
  </tr>
   <tr>
    <td><b>Accessories</b></td>
    <td>""" + str(dfa7a7) + """</td>
    <td>""" + str(dfa77a77) + """</td>
    <td>""" + str(dfb7b7) + """</td>
    <td>""" + str(dfb77b77) + """</td>
    <td>""" + str(dfc7c7) + """</td>
    <td>""" + str(dfc77c77) + """</td>
  </tr>
  <tr>
    <td><b>Mother & Child</b></td>
    <td>""" + str(dfa8a8) + """</td>
    <td>""" + str(dfa88a88) + """</td>
    <td>""" + str(dfb8b8) + """</td>
    <td>""" + str(dfb88b88) + """</td>
    <td>""" + str(dfc8c8) + """</td>
    <td>""" + str(dfc88c88) + """</td>
  </tr>
  <tr>
    <td><b>Men</b></td>
    <td>""" + str(dfa9a9) + """</td>
    <td>""" + str(dfa99a99) + """</td>
    <td>""" + str(dfb9b9) + """</td>
    <td>""" + str(dfb99b99) + """</td>
    <td>""" + str(dfc9c9) + """</td>
    <td>""" + str(dfc99c99) + """</td>
  </tr>
  <tr>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b>Sum total</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x11x11)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y11y11)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x22x22)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y22y22)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x33x33)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y33y33)+"""</b></td>
  </tr>
  </table>
  <br>
  </br>
  <p><b>Non Clearance Sales</b></p> 
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
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Date </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;">""" + str(df_1_1) + """</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;">""" + str(df_2_2) + """</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> MTD </th>
  </tr>
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Category Name </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
  </tr>
  <tr>
    <td><b>Apparel</b></td>
    <td>""" + str(dfa1a1x1) + """</td>
    <td>""" + str(dfa11a11x11) + """</td>
    <td>""" + str(dfb1b1x1) + """</td>
    <td>""" + str(dfb11b11x11) + """</td>
    <td>""" + str(dfc1c1x1) + """</td>
    <td>""" + str(dfc11c11x11) + """</td>
  </tr>
  <tr>
    <td><b>Bags</b></td>
    <td>""" + str(dfa2a2x2) + """</td>
    <td>""" + str(dfa22a22x22) + """</td>
    <td>""" + str(dfb2b2x2) + """</td>
    <td>""" + str(dfb22b22x22) + """</td>
    <td>""" + str(dfc2c2x2) + """</td>
    <td>""" + str(dfc22c22x22) + """</td>
  </tr>
  <tr>
    <td><b>Footwear</b></td>
    <td>""" + str(dfa3a3x3) + """</td>
    <td>""" + str(dfa33a33x33) + """</td>
    <td>""" + str(dfb3b3x3) + """</td>
    <td>""" + str(dfb33b33x33) + """</td>
    <td>""" + str(dfc3c3x3) + """</td>
    <td>""" + str(dfc33c33x33) + """</td>
  </tr>
  <tr>
    <td><b>Home & Decor</b></td>
    <td>""" + str(dfa4a4x4) + """</td>
    <td>""" + str(dfa44a44x44) + """</td>
    <td>""" + str(dfb4b4x4) + """</td>
    <td>""" + str(dfb44b44x44) + """</td>
    <td>""" + str(dfc4c4x4) + """</td>
    <td>""" + str(dfc44c44x44) + """</td>
  </tr>
  <tr>
    <td><b>Jewelry</b></td>
    <td>""" + str(dfa5a5x5) + """</td>
    <td>""" + str(dfa55a55x55) + """</td>
    <td>""" + str(dfb5b5x5) + """</td>
    <td>""" + str(dfb55b55x55) + """</td>
    <td>""" + str(dfc5c5x5) + """</td>
    <td>""" + str(dfc55c55x55) + """</td>
  </tr>
  <tr>
    <td><b>Wellness</b></td>
    <td>""" + str(dfa6a6x6) + """</td>
    <td>""" + str(dfa66a66x66) + """</td>
    <td>""" + str(dfb6b6x6) + """</td>
    <td>""" + str(dfb66b66x66) + """</td>
    <td>""" + str(dfc6c6x6) + """</td>
    <td>""" + str(dfc66c66x66) + """</td>
  </tr>
   <tr>
    <td><b>Accessories</b></td>
    <td>""" + str(dfa7a7x7) + """</td>
    <td>""" + str(dfa77a77x77) + """</td>
    <td>""" + str(dfb7b7x7) + """</td>
    <td>""" + str(dfb77b77x77) + """</td>
    <td>""" + str(dfc7c7x7) + """</td>
    <td>""" + str(dfc77c77x77) + """</td>
  </tr>
   <tr>
    <td><b>Mother & Child</b></td>
    <td>""" + str(dfa8a8x8) + """</td>
    <td>""" + str(dfa88a88x88) + """</td>
    <td>""" + str(dfb8b8x8) + """</td>
    <td>""" + str(dfb88b88x88) + """</td>
    <td>""" + str(dfc8c8x8) + """</td>
    <td>""" + str(dfc88c88x88) + """</td>
  </tr>
   <tr>
    <td><b>Men</b></td>
    <td>""" + str(dfa9a9x9) + """</td>
    <td>""" + str(dfa99a99x99) + """</td>
    <td>""" + str(dfb9b9x9) + """</td>
    <td>""" + str(dfb99b99x99) + """</td>
    <td>""" + str(dfc9c9x9) + """</td>
    <td>""" + str(dfc99c99x99) + """</td>
  </tr>
  <tr>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b>Sum total</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x11x11x11)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y11y11y11)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x22x22x22)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y22y22y22)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x33x33x33)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y33y33y33)+"""</b></td>
  </tr>
  </table>
  <br>
  </br>
  <p><b>Total Sales</b></p> 
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
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Date </th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;">""" + str(df_1_1) + """</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;">""" + str(df_2_2) + """</th>
    <th style="background-color:#000; color:#fff; padding: 10px;"></th>
    <th style="background-color:#000; color:#fff; padding: 10px;"> MTD </th>
  </tr>
  <tr>
    <th style="background-color:#000; color:#fff; padding: 10px;"> Category Name </th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Quantity</th>
    <th style="background-color:#000; color:#fff; padding: 10px;">Revenue</th>
  </tr>
  <tr>
    <td><b>Apparel</b></td>
    <td>""" + str(dfa1a1y1) + """</td>
    <td>""" + str(dfa11a11y11) + """</td>
    <td>""" + str(dfb1b1y1) + """</td>
    <td>""" + str(dfb11b11y11) + """</td>
    <td>""" + str(dfc1c1y1) + """</td>
    <td>""" + str(dfc11c11y11) + """</td>
  </tr>
  <tr>
    <td><b>Bags</b></td>
    <td>""" + str(dfa2a2y2) + """</td>
    <td>""" + str(dfa22a22y22) + """</td>
    <td>""" + str(dfb2b2y2) + """</td>
    <td>""" + str(dfb22b22y22) + """</td>
    <td>""" + str(dfc2c2y2) + """</td>
    <td>""" + str(dfc22c22y22) + """</td>
  </tr>
  <tr>
    <td><b>Footwear</b></td>
    <td>""" + str(dfa3a3y3) + """</td>
    <td>""" + str(dfa33a33y33) + """</td>
    <td>""" + str(dfb3b3y3) + """</td>
    <td>""" + str(dfb33b33y33) + """</td>
    <td>""" + str(dfc3c3y3) + """</td>
    <td>""" + str(dfc33c33y33) + """</td>
  </tr>
  <tr>
    <td><b>Home & Decor</b></td>
    <td>""" + str(dfa4a4y4) + """</td>
    <td>""" + str(dfa44a44y44) + """</td>
    <td>""" + str(dfb4b4y4) + """</td>
    <td>""" + str(dfb44b44y44) + """</td>
    <td>""" + str(dfc4c4y4) + """</td>
    <td>""" + str(dfc44c44y44) + """</td>
  </tr>
  <tr>
    <td><b>Jewelry</b></td>
    <td>""" + str(dfa5a5y5) + """</td>
    <td>""" + str(dfa55a55y55) + """</td>
    <td>""" + str(dfb5b5y5) + """</td>
    <td>""" + str(dfb55b55y55) + """</td>
    <td>""" + str(dfc5c5y5) + """</td>
    <td>""" + str(dfc55c55y55) + """</td>
  </tr>
  <tr>
    <td><b>Wellness</b></td>
    <td>""" + str(dfa6a6y6) + """</td>
    <td>""" + str(dfa66a66y66) + """</td>
    <td>""" + str(dfb6b6y6) + """</td>
    <td>""" + str(dfb66b66y66) + """</td>
    <td>""" + str(dfc6c6y6) + """</td>
    <td>""" + str(dfc66c66y66) + """</td>
  </tr>
   <tr>
    <td><b>Accessories</b></td>
    <td>""" + str(dfa7a7y7) + """</td>
    <td>""" + str(dfa77a77y77) + """</td>
    <td>""" + str(dfb7b7y7) + """</td>
    <td>""" + str(dfb77b77y77) + """</td>
    <td>""" + str(dfc7c7y7) + """</td>
    <td>""" + str(dfc77c77y77) + """</td>
  </tr>
  <tr>
    <td><b>Mother & Child</b></td>
    <td>""" + str(dfa8a8y8) + """</td>
    <td>""" + str(dfa88a88y88) + """</td>
    <td>""" + str(dfb8b8y8) + """</td>
    <td>""" + str(dfb88b88y88) + """</td>
    <td>""" + str(dfc8c8y8) + """</td>
    <td>""" + str(dfc88c88y88) + """</td>
  </tr>
  <tr>
    <td><b>Men</b></td>
    <td>""" + str(dfa9a9y9) + """</td>
    <td>""" + str(dfa99a99y99) + """</td>
    <td>""" + str(dfb9b9y9) + """</td>
    <td>""" + str(dfb99b99y99) + """</td>
    <td>""" + str(dfc9c9y9) + """</td>
    <td>""" + str(dfc99c99y99) + """</td>
  </tr>
  <tr>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b>Sum total</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x11x11x11x11)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y11y11y11y11)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x22x22x22x22)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y22y22y22y22)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(x33x33x33x33)+"""</b></td>
    <td style="background-color:#000; color:#fff; padding: 10px;"><b> """+str(y33y33y33y33)+"""</b></td>
  </tr>
  </table>
  <br>
  </br>  
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




