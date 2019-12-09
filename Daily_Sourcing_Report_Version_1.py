#!/usr/bin/env python
# coding: utf-8

# In[1]:


#importing Python Libaries 

import psycopg2 as ps
import pandas as pd
import xlsxwriter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email import encoders 
import datetime
import numpy as np
import os

os.remove(r'C://Users//sachi//OneDrive//Desktop//Sourcing_Report.xlsx')


#Creating a connection to database

conn = ps.connect(user = 'doadmin', password = 'xpmt05ij9uf9rknn', host = 'tjori-bi-do-user-6486966-0.db.ondigitalocean.com', port = '25060', database = 'defaultdb')


def category_percentage(x):
    sql0 = '''
        
    WITH category AS (VALUES(%s))

SELECT
    (SELECT name FROM store_category WHERE id = (TABLE category) LIMIT 1) AS selected_category,
    new_execution.week AS week,
    new_execution.new_skus,
    sku_ids,
    round(sales_breadth.in01w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent01w,
    round(sales_breadth.in02w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent02w,
    round(sales_breadth.in03w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent03w,
    round(sales_breadth.in04w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent04w,
    round(sales_breadth.in05w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent05w,
    round(sales_breadth.in06w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent06w,
    round(sales_breadth.in07w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent07w,
    round(sales_breadth.in08w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent08w,
    round(sales_breadth.in09w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent09w,
    round(sales_breadth.in10w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent10w,
    round(sales_breadth.in11w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent11w,
    round(sales_breadth.in12w::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percent12w,
    round(sales_breadth.sofar::FLOAT / new_execution.new_skus::FLOAT * 100)::INTEGER AS percentsofar
FROM
    (
        SELECT 
            (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
            count(DISTINCT catalog.sku) AS new_skus,
            string_agg(distinct catalog.sku,',') AS sku_ids
        FROM
            store_product catalog
        WHERE 
            catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01' AND
            CASE WHEN ((TABLE category) = 0) THEN TRUE
            ELSE catalog.category_id = (TABLE category) END
        GROUP BY 
            week 
    ) new_execution

    LEFT JOIN
    (
        WITH cur_week AS (
            VALUES(
                (
                    EXTRACT(YEAR FROM now() AT TIME zone 'asia/kolkata')*100 + 
                    EXTRACT(WEEK FROM now() AT TIME zone 'asia/kolkata')
                )::INTEGER
            )
        )
            

        SELECT
        week,
        CASE WHEN (week+ 0) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 1) END AS in01w,
        CASE WHEN (week+ 1) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 2) END AS in02w,
        CASE WHEN (week+ 2) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 3) END AS in03w,
        CASE WHEN (week+ 3) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 4) END AS in04w,
        CASE WHEN (week+ 4) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 5) END AS in05w,
        CASE WHEN (week+ 5) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 6) END AS in06w,
        CASE WHEN (week+ 6) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 7) END AS in07w,
        CASE WHEN (week+ 7) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 8) END AS in08w,
        CASE WHEN (week+ 8) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7* 9) END AS in09w,
        CASE WHEN (week+ 9) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7*10) END AS in10w,
        CASE WHEN (week+10) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7*11) END AS in11w,
        CASE WHEN (week+11) > (TABLE cur_week) THEN NULL ELSE count(DISTINCT catalog_id)  FILTER (WHERE sales_within_days <=  7*12) END AS in12w,
        count(DISTINCT catalog_id) AS sofar
        
        FROM
            (SELECT
                        
                (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
                catalog.created AS catalog_created,
                soi.created AS soi_created,
                soi.quanity AS soi_quantity,
                so.status AS so_status,
                catalog.id AS catalog_id,
                EXTRACT(EPOCH FROM (soi.created - catalog.created))/86400 AS days_since_live_to_sale,
                7*(CEIL(EXTRACT(EPOCH FROM (soi.created - catalog.created))/86400/7)::INTEGER) AS sales_within_days

            FROM
                order_order so
                LEFT JOIN order_orderproduct soi ON soi.order_id = so.id
                LEFT JOIN store_product catalog ON soi.product_id = catalog.id
            WHERE 
                catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01' AND
                CASE WHEN ((TABLE category) = 0) THEN TRUE
                ELSE catalog.category_id = (TABLE category) END

        ) days_since

        WHERE
            so_status = 'confirmed'

        GROUP BY
            week

    ) sales_breadth ON new_execution.week = sales_breadth.week


ORDER BY
    week DESC

;''' % (x)
 
    df0 = pd.read_sql_query(sql0, conn)
    return df0


def category_unit_sold (x):

    sql = '''
        WITH category AS (VALUES(%s))

SELECT
    (SELECT name FROM store_category WHERE id = (TABLE category) LIMIT 1) AS selected_category,
    new_execution.week AS week,
    new_execution.new_skus,
    unit_sales.w01,
    unit_sales.w02,
    unit_sales.w03,
    unit_sales.w04,
    unit_sales.w05,
    unit_sales.w06,
    unit_sales.w07,
    unit_sales.w08,
    unit_sales.w09,
    unit_sales.w10,
    unit_sales.w11,
    unit_sales.w12,
    unit_sales.sofar
FROM
    (
        SELECT 
            (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
            count(DISTINCT catalog.sku) AS new_skus
        FROM
            store_product catalog
        WHERE 
            catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01' AND
            CASE WHEN ((TABLE category) = 0) THEN TRUE
            ELSE catalog.category_id = (TABLE category) END
        GROUP BY 
            week 
    ) new_execution

    LEFT JOIN
    (
        WITH cur_week AS (
            VALUES(
                (
                    EXTRACT(YEAR FROM now() AT TIME zone 'asia/kolkata')*100 + 
                    EXTRACT(WEEK FROM now() AT TIME zone 'asia/kolkata')
                )::INTEGER
            )
        )
            

        SELECT
        week,
        CASE WHEN (week+ 0) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 1) END AS w01,
        CASE WHEN (week+ 1) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 2) END AS w02,
        CASE WHEN (week+ 2) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 3) END AS w03,
        CASE WHEN (week+ 3) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 4) END AS w04,
        CASE WHEN (week+ 4) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 5) END AS w05,
        CASE WHEN (week+ 5) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 6) END AS w06,
        CASE WHEN (week+ 6) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 7) END AS w07,
        CASE WHEN (week+ 7) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 8) END AS w08,
        CASE WHEN (week+ 8) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7* 9) END AS w09,
        CASE WHEN (week+ 9) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7*10) END AS w10,
        CASE WHEN (week+10) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7*11) END AS w11,
        CASE WHEN (week+11) > (TABLE cur_week) THEN NULL ELSE SUM(soi_quantity)  FILTER (WHERE sales_within_days =  7*12) END AS w12,
        SUM(soi_quantity) AS sofar
        
        FROM
            (SELECT
                        
                (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
                catalog.created AS catalog_created,
                soi.created AS soi_created,
                soi.quanity AS soi_quantity,
                so.status AS so_status,
                catalog.id AS catalog_id,
                EXTRACT(EPOCH FROM (soi.created - catalog.created))/86400 AS days_since_live_to_sale,
                7*(CEIL(EXTRACT(EPOCH FROM (soi.created - catalog.created))/86400/7)::INTEGER) AS sales_within_days

            FROM
                order_order so
                LEFT JOIN order_orderproduct soi ON soi.order_id = so.id
                LEFT JOIN store_product catalog ON soi.product_id = catalog.id
            WHERE 
                catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01' AND
                CASE WHEN ((TABLE category) = 0) THEN TRUE
                ELSE catalog.category_id = (TABLE category) END AND
                so.status = 'confirmed' AND
                soi.exchanged = FALSE AND
                soi.returned = FALSE AND
                soi.removed = FALSE

        ) days_since

        GROUP BY
            week

    ) unit_sales ON new_execution.week = unit_sales.week


ORDER BY
    week DESC
;

'''  % (x)
    
    df = pd.read_sql_query(sql, conn)
    return df
 
def new_execution_units_sold():

    
    sql1 = '''
            SELECT
                (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
                catalog.sku,
                category.name, 
                sum(soi.quanity) AS soi_quantity
             
            FROM
                order_order so
                LEFT JOIN order_orderproduct soi ON soi.order_id = so.id
                LEFT JOIN store_product catalog ON soi.product_id = catalog.id
                LEFT JOIN store_category category ON CATALOG.category_id = category.id
            WHERE 
                catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01' AND
                so.status = 'confirmed' AND
                soi.exchanged = FALSE AND
                soi.returned = FALSE AND
                soi.removed = FALSE

            GROUP BY
                week,
                catalog.sku,
                category.name
; '''
    df1 = pd.read_sql_query(sql1, conn)
    return df1


def category_page_views(x):
    sql3 = '''
            WITH category AS (VALUES(%s)), cur_week AS (
    VALUES(
        (
            EXTRACT(YEAR FROM now() AT TIME zone 'asia/kolkata')*100 +
            EXTRACT(WEEK FROM now() AT TIME zone 'asia/kolkata')
        )::INTEGER
    )
)


SELECT
        (SELECT name FROM store_category WHERE id = (TABLE category) LIMIT 1) AS selected_category,
        week,
        count(DISTINCT catalog_sku) AS sku_live,
        count(DISTINCT catalog_sku) AS new_skus,
        CASE WHEN (week+0) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*1) END::INTEGER AS in1w,
        CASE WHEN (week+1) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*2) END::INTEGER AS in2w,
        CASE WHEN (week+2) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*3) END::INTEGER AS in3w,
        CASE WHEN (week+3) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*4) END::INTEGER AS in4w,
        CASE WHEN (week+4) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*5) END::INTEGER AS in5w,
        CASE WHEN (week+5) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*6) END::INTEGER AS in6w,
        CASE WHEN (week+6) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*7) END::INTEGER AS in7w,
        CASE WHEN (week+7) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*8) END::INTEGER AS in8w,
        CASE WHEN (week+8) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*9) END::INTEGER AS in9w,
        CASE WHEN (week+9) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*10) END::INTEGER AS in10w,
        CASE WHEN (week+10) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*11) END::INTEGER AS in11w,
        CASE WHEN (week+11) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*12) END::INTEGER AS in12w,
        CASE WHEN (week+12) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*13) END::INTEGER AS in13w,
        CASE WHEN (week+13) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*14) END::INTEGER AS in14w,
        CASE WHEN (week+14) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*15) END::INTEGER AS in15w,
        CASE WHEN (week+15) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*16) END::INTEGER AS in16w,
        CASE WHEN (week+16) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*17) END::INTEGER AS in17w,
        CASE WHEN (week+17) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*18) END::INTEGER AS in18w,
        CASE WHEN (week+18) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*19) END::INTEGER AS in19w,
        CASE WHEN (week+19) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*20) END::INTEGER AS in20w,
        CASE WHEN (week+20) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*21) END::INTEGER AS in21w,
        CASE WHEN (week+21) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*22) END::INTEGER AS in22w,
        CASE WHEN (week+22) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*23) END::INTEGER AS in23w,
        CASE WHEN (week+23) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*24) END::INTEGER AS in24w,
        CASE WHEN (week+24) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*25) END::INTEGER AS in25w,
        CASE WHEN (week+25) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*26) END::INTEGER AS in26w,
        CASE WHEN (week+26) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*27) END::INTEGER AS in27w,
        CASE WHEN (week+27) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*28) END::INTEGER AS in28w,
        CASE WHEN (week+28) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*29) END::INTEGER AS in29w,
        CASE WHEN (week+29) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*30) END::INTEGER AS in30w,
        CASE WHEN (week+30) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*31) END::INTEGER AS in31w,
        CASE WHEN (week+31) > (TABLE cur_week) THEN NULL ELSE SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*32) END::INTEGER AS in32w,

        SUM(ga_unique_page_views)::INTEGER AS sofar
FROM
    (SELECT

        (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
        catalog.created AT TIME zone 'asia/kolkata' AS catalog_created,
        ga.date + INTERVAL '12' HOUR AS ga_date,
        ga.unique_page_views AS ga_unique_page_views,
        catalog.sku AS catalog_sku,
        EXTRACT(EPOCH FROM (ga.date + INTERVAL '12' HOUR - catalog.created AT TIME zone 'asia/kolkata'))/86400 AS days_since_live_to_view,
        7*(CEIL(EXTRACT(EPOCH FROM (ga.date + INTERVAL '12' HOUR - catalog.created AT TIME zone 'asia/kolkata'))/86400/7)::INTEGER) AS views_within_days

    FROM
        store_product catalog
        LEFT JOIN (
            SELECT * FROM ga_gatsby
            UNION SELECT * FROM ga_old
        ) ga ON ga.product_id = catalog.id
    WHERE
        catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01' AND
        CASE WHEN ((TABLE category) = 0) THEN TRUE
        ELSE catalog.category_id = (TABLE category) END
) days_since

GROUP BY
    selected_category,
    week
    
ORDER BY
    week DESC;
''' % (x)
    
    df3 = pd.read_sql_query(sql3, conn)
    return df3
    
def new_execution_page_views():
   
    sql4 =  '''
        SELECT
             (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
             catalog.created AS catalog_created,
             category.name AS category_name,
             catalog.sku AS catalog_sku,
             ssc.name AS sub_category_name,
	         sum(ga.unique_page_views) AS ga_unique_page_views
        FROM
            store_product catalog
        LEFT JOIN (
            SELECT * FROM ga_gatsby
            UNION SELECT * FROM ga_old
        ) ga ON ga.product_id = catalog.id
     LEFT JOIN
	     store_category category on catalog.category_id = category.id
	 LEFT JOIN
         store_subcategory AS ssc ON category.id = ssc.id
    WHERE
        catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01'
	GROUP BY
    catalog_sku
	,category.name
	,ssc.name 
	,catalog.created
    ,week
    
ORDER BY
    week DESC;
'''
    df4 = pd.read_sql_query(sql4, conn)
    return df4

def pips_category(x):
    
    sql5 = '''
             WITH category AS (VALUES(%s)), cur_week AS (
    VALUES(
        (
            EXTRACT(YEAR FROM now() AT TIME zone 'asia/kolkata')*100 +
            EXTRACT(WEEK FROM now() AT TIME zone 'asia/kolkata')
        )::INTEGER
    )
)

SELECT
    *,
    ROUND((units_sold.units_w01::FLOAT / page_views.pv_01w::FLOAT) * 10000) / 100 as pips_w01,
    ROUND((units_sold.units_w02::FLOAT / page_views.pv_02w::FLOAT) * 10000) / 100 as pips_w02,
    ROUND((units_sold.units_w03::FLOAT / page_views.pv_03w::FLOAT) * 10000) / 100 as pips_w03,
    ROUND((units_sold.units_w04::FLOAT / page_views.pv_04w::FLOAT) * 10000) / 100 as pips_w04,
    ROUND((units_sold.units_w05::FLOAT / page_views.pv_05w::FLOAT) * 10000) / 100 as pips_w05,
    ROUND((units_sold.units_w06::FLOAT / page_views.pv_06w::FLOAT) * 10000) / 100 as pips_w06,
    ROUND((units_sold.units_w07::FLOAT / page_views.pv_07w::FLOAT) * 10000) / 100 as pips_w07,
    ROUND((units_sold.units_w08::FLOAT / page_views.pv_08w::FLOAT) * 10000) / 100 as pips_w08,
    ROUND((units_sold.units_w09::FLOAT / page_views.pv_09w::FLOAT) * 10000) / 100 as pips_w09,
    ROUND((units_sold.units_w10::FLOAT / page_views.pv_10w::FLOAT) * 10000) / 100 as pips_w10,
    ROUND((units_sold.units_w11::FLOAT / page_views.pv_11w::FLOAT) * 10000) / 100 as pips_w11,
    ROUND((units_sold.units_w12::FLOAT / page_views.pv_12w::FLOAT) * 10000) / 100 as pips_w12,
    ROUND((units_sold.units_w13::FLOAT / page_views.pv_13w::FLOAT) * 10000) / 100 as pips_w13,
    ROUND((units_sold.units_w14::FLOAT / page_views.pv_14w::FLOAT) * 10000) / 100 as pips_w14,
    ROUND((units_sold.units_w15::FLOAT / page_views.pv_15w::FLOAT) * 10000) / 100 as pips_w15,
    ROUND((units_sold.units_w16::FLOAT / page_views.pv_16w::FLOAT) * 10000) / 100 as pips_w16,
    ROUND((units_sold.units_w17::FLOAT / page_views.pv_17w::FLOAT) * 10000) / 100 as pips_w17,
    ROUND((units_sold.units_w18::FLOAT / page_views.pv_18w::FLOAT) * 10000) / 100 as pips_w18,
    ROUND((units_sold.units_w19::FLOAT / page_views.pv_19w::FLOAT) * 10000) / 100 as pips_w19,
    ROUND((units_sold.units_w20::FLOAT / page_views.pv_20w::FLOAT) * 10000) / 100 as pips_w20,
    ROUND((units_sold.units_w21::FLOAT / page_views.pv_21w::FLOAT) * 10000) / 100 as pips_w21,
    ROUND((units_sold.units_w22::FLOAT / page_views.pv_22w::FLOAT) * 10000) / 100 as pips_w22,
    ROUND((units_sold.units_w23::FLOAT / page_views.pv_23w::FLOAT) * 10000) / 100 as pips_w23,
    ROUND((units_sold.units_w24::FLOAT / page_views.pv_24w::FLOAT) * 10000) / 100 as pips_w24,
    ROUND((units_sold.units_w25::FLOAT / page_views.pv_25w::FLOAT) * 10000) / 100 as pips_w25,
    ROUND((units_sold.units_w26::FLOAT / page_views.pv_26w::FLOAT) * 10000) / 100 as pips_w26,

    ROUND((units_sold.units_sofar::FLOAT / page_views.pv_sofar::FLOAT) * 10000) / 100 as pips_sofar    
FROM
    (
        SELECT
            catalog_sku,
            (SELECT name FROM store_category category WHERE category.id = MIN(catalog_category_id) LIMIT 1) as category,
            MIN(week) as catalog_week_created,
            MIN(catalog_created) as catalog_created,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 1) ::INTEGER AS pv_01w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 2) ::INTEGER AS pv_02w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 3) ::INTEGER AS pv_03w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 4) ::INTEGER AS pv_04w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 5) ::INTEGER AS pv_05w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 6) ::INTEGER AS pv_06w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 7) ::INTEGER AS pv_07w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 8) ::INTEGER AS pv_08w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7* 9) ::INTEGER AS pv_09w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*10) ::INTEGER AS pv_10w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*11) ::INTEGER AS pv_11w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*12) ::INTEGER AS pv_12w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*13) ::INTEGER AS pv_13w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*14) ::INTEGER AS pv_14w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*15) ::INTEGER AS pv_15w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*16) ::INTEGER AS pv_16w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*17) ::INTEGER AS pv_17w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*18) ::INTEGER AS pv_18w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*19) ::INTEGER AS pv_19w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*20) ::INTEGER AS pv_20w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*21) ::INTEGER AS pv_21w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*22) ::INTEGER AS pv_22w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*23) ::INTEGER AS pv_23w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*24) ::INTEGER AS pv_24w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*25) ::INTEGER AS pv_25w,
            SUM(ga_unique_page_views)  FILTER (WHERE views_within_days =  7*26) ::INTEGER AS pv_26w,
            SUM(ga_unique_page_views)::INTEGER AS pv_sofar
        FROM
            (SELECT

                (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
                catalog.created AS catalog_created,
                ga.date + INTERVAL '12' HOUR AS ga_date,
                ga.unique_page_views AS ga_unique_page_views,
                catalog.sku AS catalog_sku,
                catalog.category_id AS catalog_category_id,
                EXTRACT(EPOCH FROM (ga.date + INTERVAL '12' HOUR - catalog.created AT TIME zone 'asia/kolkata'))/86400 AS days_since_live_to_view,
                7*(CEIL(EXTRACT(EPOCH FROM (ga.date + INTERVAL '12' HOUR - catalog.created AT TIME zone 'asia/kolkata'))/86400/7)::INTEGER) AS views_within_days

            FROM
                store_product catalog
                LEFT JOIN (
                    SELECT * FROM ga_gatsby
                    UNION SELECT * FROM ga_old
                ) ga ON ga.product_id = catalog.id
            WHERE
                catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01' AND
                CASE WHEN ((TABLE category) = 0) THEN TRUE
                ELSE catalog.category_id = (TABLE category) END
        ) days_since

        GROUP BY
            catalog_sku

        ORDER BY
            catalog_created DESC

    ) page_views

    LEFT JOIN (
        SELECT
            catalog_sku,
            (SELECT name FROM store_category category WHERE category.id = MIN(catalog_category_id) LIMIT 1) as category,
            MIN(week) as catalog_week_created,
            MIN(catalog_created) as catalog_created,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 1) AS units_w01,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 2) AS units_w02,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 3) AS units_w03,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 4) AS units_w04,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 5) AS units_w05,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 6) AS units_w06,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 7) AS units_w07,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 8) AS units_w08,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7* 9) AS units_w09,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*10) AS units_w10,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*11) AS units_w11,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*12) AS units_w12,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*13) AS units_w13,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*14) AS units_w14,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*15) AS units_w15,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*16) AS units_w16,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*17) AS units_w17,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*18) AS units_w18,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*19) AS units_w19,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*20) AS units_w20,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*21) AS units_w21,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*22) AS units_w22,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*23) AS units_w23,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*24) AS units_w24,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*25) AS units_w25,
            SUM(soi_quantity) FILTER (WHERE sales_within_days =  7*26) AS units_w26,
            SUM(soi_quantity) AS units_sofar
                
        FROM
            (SELECT
                        
                (EXTRACT(YEAR FROM catalog.created AT TIME zone 'asia/kolkata')*100 + EXTRACT(WEEK FROM catalog.created AT TIME zone 'asia/kolkata'))::INTEGER AS week,
                catalog.sku AS catalog_sku,
                catalog.created AS catalog_created,
                soi.created AS soi_created,
                soi.quanity AS soi_quantity,
                so.status AS so_status,
                catalog.id AS catalog_id,
                catalog.category_id AS catalog_category_id,
                EXTRACT(EPOCH FROM (soi.created - catalog.created))/86400 AS days_since_live_to_sale,
                7*(CEIL(EXTRACT(EPOCH FROM (soi.created - catalog.created))/86400/7)::INTEGER) AS sales_within_days

            FROM
                order_order so
                LEFT JOIN order_orderproduct soi ON soi.order_id = so.id
                LEFT JOIN store_product catalog ON soi.product_id = catalog.id
            WHERE 
                catalog.created AT TIME zone 'asia/kolkata' > '2019-01-01' AND
                CASE WHEN ((TABLE category) = 0) THEN TRUE
                ELSE catalog.category_id = (TABLE category) END AND
                so.status = 'confirmed' AND
                soi.exchanged = FALSE AND
                soi.returned = FALSE AND
                soi.removed = FALSE

            ) days_since

        GROUP BY
            catalog_sku

        ORDER BY
            catalog_created DESC
    ) units_sold ON page_views.catalog_sku = units_sold.catalog_sku

; ''' % (x)
    
    df5 = pd.read_sql_query(sql5, conn)
    return df5



def category_percentage_1():
    list = [2,4,5,6,7,8,21,33,35,0]
    empty_list = []
    for x in list:
        df = category_percentage(x)
        empty_list.append(df)
    return empty_list


def category_unit_sold_1():
    list = [2,4,5,6,7,8,21,33,35,0]
    empty_list = []
    for x in list:
        df = category_unit_sold(x)
        empty_list.append(df)
    return empty_list

def page_views_category_1():
    list = [2,4,5,6,7,8,21,33,35,0]
    empty_list = []
    for x in list:
        df = category_page_views(x)
        empty_list.append(df)
    return empty_list

def pips_category_1():
    list = [2,4,5,6,7,8,21,33,35,0]
    empty_list = []
    for x in list:
        df = pips_category(x)
        empty_list.append(df)
    return empty_list

#Write to Excel

def write_to_excel():
    func = category_percentage_1()
    func_0 = category_unit_sold_1()
    func_1 = new_execution_units_sold()
    func_3 = page_views_category_1()
    func_5 = new_execution_page_views()
    func_7 = pips_category_1()
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    
    writer = pd.ExcelWriter('C://Users//sachi//OneDrive//Desktop//Sourcing_Report.xlsx', engine='xlsxwriter')
    
    # Convert the dataframe to an XlsxWriter Excel object.
    func[0].to_excel(writer,sheet_name='SalesThroughRate_Apparel')
    
    func[1].to_excel(writer,sheet_name='SalesThroughRate_Jewelry')
    
    func[2].to_excel(writer,sheet_name='SalesThroughRate_Footwear')
    
    func[3].to_excel(writer,sheet_name='SalesThroughRate_Accessories')
    
    func[4].to_excel(writer,sheet_name='SalesThroughRate_Home & Decor')
    
    func[5].to_excel(writer,sheet_name='SalesThroughRate_Wellness')
    
    func[6].to_excel(writer,sheet_name='SalesThroughRate_Bags')
    
    func[7].to_excel(writer,sheet_name='SalesThroughRate_MotherChild')
    
    func[8].to_excel(writer,sheet_name='SalesThroughRate_Men')
    
    func[9].to_excel(writer,sheet_name='AllCategoriesSTR')
    
    func_0[0].to_excel(writer,sheet_name='TotalUnitsSold_Apparel')
    
    func_0[1].to_excel(writer,sheet_name='TotalUnitsSold_Jewelry')
    
    func_0[2].to_excel(writer,sheet_name='TotalUnitsSold_Footwear')
    
    func_0[3].to_excel(writer,sheet_name='TotalUnitsSold_Accessories')
    
    func_0[4].to_excel(writer,sheet_name='TotalUnitsSold_Home & Decor')
    
    func_0[5].to_excel(writer,sheet_name='TotalUnitsSold_Wellness')
    
    func_0[6].to_excel(writer,sheet_name='TotalUnitsSold_Bags')
    
    func_0[7].to_excel(writer,sheet_name='TotalUnitsSold_MotherChild')
    
    func_0[8].to_excel(writer,sheet_name='TotalUnitsSold_Men')
    
    func_0[9].to_excel(writer,sheet_name='AllCategoriesTotalUnitsSold')
    
    func_1.to_excel(writer,sheet_name='NewExecutionUnitsSold')
    
    func_3[0].to_excel(writer,sheet_name='PageViews_Apparel')
    
    func_3[1].to_excel(writer,sheet_name='PageViews_Jewelry')
    
    func_3[2].to_excel(writer,sheet_name='PageViews_Footwear')
    
    func_3[3].to_excel(writer,sheet_name='PageViews_Accessories')
    
    func_3[4].to_excel(writer,sheet_name='PageViews_Home & Decor')
    
    func_3[5].to_excel(writer,sheet_name='PageViews_Wellness')
    
    func_3[6].to_excel(writer,sheet_name='PageViews_Bags')
    
    func_3[7].to_excel(writer,sheet_name='PageViews_MotherChild')
    
    func_3[8].to_excel(writer,sheet_name='PageViews_Men')
    
    func_3[9].to_excel(writer,sheet_name='AllCategoriesPV')
    
    func_5.to_excel(writer, sheet_name = 'NewExecutionsPV')
    
    func_7[0].to_excel(writer,sheet_name='PIPS_Apparel')
    
    func_7[1].to_excel(writer,sheet_name='PIPS_Jewelry')
    
    func_7[2].to_excel(writer,sheet_name='PIPS_Footwear')
    
    func_7[3].to_excel(writer,sheet_name='PIPS_Accessories')
    
    func_7[4].to_excel(writer,sheet_name='PIPS_Home & Decor')
    
    func_7[5].to_excel(writer,sheet_name='PIPS_Wellness')
    
    func_7[6].to_excel(writer,sheet_name='PIPS_Bags')
    
    func_7[7].to_excel(writer,sheet_name='PIPS_MotherChild')
    
    func_7[8].to_excel(writer,sheet_name='PIPS_Men')
    
    func_7[9].to_excel(writer,sheet_name='AllCategoriesPIPS')
    
    
    
    # Close the Pandas Excel writer and output the Excel file.
    
    writer.save()
    
#Send Excel Attachment in an Email

def send_email():
    sender = "nimit@tjori.com"
    recievers = [
                 "nimit@tjori.com",
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
                 "harshit@tjori.com",
                 "aditi@tjori.com",
                 "hanisha@tjori.com",
                 "shiv@tjori.com"
                 ]
    
    # Create message container 
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Daily Sourcing Report"
    msg['From'] = sender
    msg['To'] = ",".join(recievers)

    # instance of MIMEBase and named as part
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("C:/Users/sachi/OneDrive/Desktop/Sourcing_Report.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Sourcing_Report.xlsx"')
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





# In[ ]:




