import psycopg2 as pgSQL
import pandas as pd
import simpleGUI as simp


def db_insert(dataframe, tablename):

    sql = """INSERT INTO vendors(vendor_name)
                 VALUES(%s) RETURNING vendor_id;"""

    login = simp.prompt_user()  # Prompts user for username and password.
    conn = pgSQL.connect(host="hienmai.c5o1dbhlufm3.ca-central-1.rds.amazonaws.com",
                         database="cfia",
                         user=login[0],
                         password=login[1])

    cur = conn.cursor()
    cur.execute(sql, (value1, value2))

    conn.commit()
    cur.close()
    conn.close()