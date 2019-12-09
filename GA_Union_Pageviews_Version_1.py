#!/usr/bin/env python
# coding: utf-8

# In[1]:


import psycopg2 as pg
import pandas as pd 
import sqlalchemy
import datetime

#Connecting to the database

conn = pg.connect( user = 'doadmin', 
                   password = 'xpmt05ij9uf9rknn', 
                   host = 'tjori-bi-do-user-6486966-0.db.ondigitalocean.com', 
                   port = '25060', 
                   database = 'defaultdb')

#Writing the postgreSQL query to retrieve the data

def retrieve_the_records(yd_1, yd_2):
    sql = '''
             select 
                  *
             from
                  ga_old
             where
                  date = '%s'
                  
             union all
             
             select
                  *
             from 
                  ga_gatsby
             where
                  date = '%s'
             ;
          ''' % (
                 yd_1
                ,yd_2)
    return pd.read_sql_query(sql, conn)

if __name__ == '__main__':
    
    yd = (datetime.datetime.now() - datetime.timedelta(1)).replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')

def write_the_records():
    df = retrieve_the_records(yd,yd)
    engine = sqlalchemy.create_engine("postgresql://doadmin:xpmt05ij9uf9rknn@tjori-bi-do-user-6486966-0.db.ondigitalocean.com:25060/defaultdb", echo = True)
    con = engine.connect()
    table_name = 'ga_union_pageviews'
    df.to_sql(table_name, con, if_exists = 'append', method = 'multi', chunksize = 10000, index = False)
    
def main():
    while True:
        write_the_records()
        break
        
if __name__ == '__main__':
    main()
    
    
    
    
    
    


# In[ ]:




