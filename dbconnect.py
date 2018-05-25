# import mysql.connector
# import psycopg2

import pymysql

def getconnect():
    __cnx = pymysql.connect(user='', password='',
                             host='127.0.0.1',
                             port=3306,
                             database='',
                             charset='utf8')
    
    return __cnx
