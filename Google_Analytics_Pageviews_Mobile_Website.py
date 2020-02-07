#!/usr/bin/env python
# coding: utf-8

# In[1]:


import argparse
import requests
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from datetime import datetime, timedelta
import pandas as pd
import sqlalchemy 
import numpy as np

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = 'C:/Users/sachi/OneDrive/Desktop/Google_Analytics/client_secret_358050000476-cn1c98do5mg0e43jvvvh3fgpklkdqlhs.apps.googleusercontent.com.json' # Path to client_secrets.json file.
VIEW_ID = '63497244'


def initialize_analyticsreporting():
  
  
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS_PATH, scope=SCOPES,
      message=tools.message_if_missing(CLIENT_SECRETS_PATH))

  
  storage = file.Storage('analyticsreporting.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  
  analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

  return analytics

def get_report(analytics):
    
    
  
      return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'pageSize': '1000000',
          'dateRanges': [
            {'startDate' : 'yesterday' ,
             'endDate' : 'yesterday'
            }
          ],
         'metrics': [
              {'expression' : 'ga:pageviews'
              },
              {'expression' : 'ga:uniquePageViews'
              }
         ],
          'dimensions' : [
              
              {'name' : 'ga:pagePath',
              },
              {
               'name' : 'ga:date'
              }
          ],
          'dimensionFilterClauses' : [
              {'filters' : [
                  {'operator' : 'REGEXP', 
                   'dimensionName' : 'ga:pagePath', 
                   'expressions': ['/p/'
                                  ]
                  }
               ]
              }
            ]
          }
        ]
      }
  ).execute()


def convert_to_dataframe(response):
    
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = [i.get('name',{}) for i in columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])]
    finalRows = []
    

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      metrics = row.get('metrics', [])[0].get('values', {})
      rowObject = {}

      for header, dimension in zip(dimensionHeaders, dimensions):
        rowObject[header] = dimension
        
        
      for metricHeader, metric in zip(metricHeaders, metrics):
        rowObject[metricHeader] = metric

      finalRows.append(rowObject)
      
      
  dataFrameFormat = pd.DataFrame(finalRows)    
  return dataFrameFormat      


def main():

  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  df = convert_to_dataframe(response)  
  df.rename(columns = {'ga:date': 'date','ga:pagePath': 'page_path','ga:pageviews' : 'page_views', 'ga:uniquePageViews' : 'unique_page_views'}, inplace = True)
  df_1 = df['page_path'].str.split("/",n = 4, expand = True)
  df['product_id'] = df_1[3]
  df['date'] = pd.to_datetime(df['date'], dayfirst = True) 
  df['product_id'] = pd.to_numeric(df['product_id'],errors='coerce').fillna(0)
  df['product_id'] = df['product_id'].astype(np.int64)
  df['page_views'] = pd.to_numeric(df['page_views'])
  df['unique_page_views'] = pd.to_numeric(df['unique_page_views']) 
  print(df['date'].dtypes)
  print(df['product_id'].dtypes)
  print(df['page_views'].dtypes)
  print(df['unique_page_views'].dtypes)  
  return df
    
    
if __name__ == '__main__':
  df = main()

engine = sqlalchemy.create_engine("postgresql://doadmin:xpmt05ij9uf9rknn@tjori-bi-do-user-6486966-0.db.ondigitalocean.com:25060/defaultdb", echo = True)
con = engine.connect()
table_name = 'ga_old'
df.to_sql(table_name, con, if_exists = 'append', method = 'multi', chunksize = 10000, index = False)
    


# In[ ]:





# In[ ]:




