#python programming language: script

'''importing the python libraries'''

import psycopg2 as pg
import pandas as pd
import xlsxwriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
import os

os.remove(r'C://Users//sachi//OneDrive//Desktop//Best_Sellers.xlsx')


class Best_sellers:
    
    def __init__ (self, sql, conn):
        self.sql = sql
        self.conn = conn
        
    def read_query(self):
        df = pd.read_sql_query(self.sql, self.conn)
        return df
          
    def write_to_excel(self, df):
        writer = pd.ExcelWriter('C://Users//sachi//OneDrive//Desktop//Best_Sellers.xlsx', engine='xlsxwriter')
        df.to_excel(writer, sheet_name = 'Best_Sellers')
        writer.save()
        
    def send_report(self):
        sender = "nimit@tjori.com"
        recievers = [
                     "nimit@tjori.com"
                    ]
        # Create message container 
    
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Best Sellers Report"
        msg['From'] = sender
        msg['To'] = ",".join(recievers)

        # instance of MIMEBase and named as part
    
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open("C://Users//sachi//OneDrive//Desktop//Best_Sellers.xlsx", "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="Best_Sellers.xlsx"')
        msg.attach(part)

        # creates SMTP session 
    
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login('nimit@tjori.com', 's/987456321/G')
        mail.sendmail(sender, recievers, msg.as_string())
        mail.quit()
        
def main():
    
    conn = pg.connect(user = 'doadmin', 
                      password = 'xpmt05ij9uf9rknn', 
                      host = 'tjori-bi-do-user-6486966-0.db.ondigitalocean.com', 
                      port = '25060', 
                      database = 'defaultdb')
    sql = '''
            --strucutred query language; query

            SELECT 
                 sp.sku
                ,sum(lsq.sum_quanity)
                ,lsq.month
                ,lsq.category
            FROM
                store_product AS sp
            LEFT JOIN
                    (
	                  SELECT 
		                   TO_CHAR(soi.created, 'MON') AS month
		                   ,sp.sku AS product_sku
				           ,SUM(soi.quanity) AS sum_quanity
				           ,sc.name AS category 
		              FROM 
		                   order_order AS so
		              LEFT JOIN 
		                   order_orderproduct AS soi ON (so.id = soi.order_id)
		              LEFT JOIN 
		                   store_product AS sp ON (soi.product_id = sp.id)
		              LEFT JOIN 
		                   store_category AS sc ON (sp.category_id = sc.id)
		              WHERE 
		                   soi.created BETWEEN '2019-10-01' AND '2020-01-01'
		                   AND so.status = 'confirmed'
		              GROUP BY 
		                   1
		                  ,2
		                  ,4
                        ) AS lsq ON (lsq.product_sku = sp.sku)
                      WHERE 
                         sp.active = TRUE 
                      GROUP BY 
                          1
                         ,3
                         ,4
                      HAVING 
                         CASE 
                            WHEN lsq.category = 'Apparel' THEN SUM(lsq.sum_quanity) > 100
                            WHEN lsq.category = 'Footwear' THEN SUM(lsq.sum_quanity) > 100
                            WHEN lsq.category = 'Wellness' THEN SUM(lsq.sum_quanity) > 100
                            WHEN lsq.category = 'Jewelry' THEN SUM(lsq.sum_quanity) > 50
                            WHEN lsq.category = 'Home & Decor' THEN SUM(lsq.sum_quanity) > 10
                            WHEN lsq.category = 'Mother & Child' THEN SUM(lsq.sum_quanity) > 50
                         END 
                        ;
		  
                 
                         '''
    inst = Best_sellers(sql, conn)
    df = inst.read_query()
    inst.write_to_excel(df)
    inst.send_report

if __name__ == '__main__':
    main()
    
        