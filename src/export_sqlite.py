#!/usr/bin/env python3
"""Export MySQL to SQLite for web deployment"""
import pandas as pd
from sqlalchemy import create_engine, text
import sqlite3
import os

MYSQL_URL = "mysql+pymysql://root:root@localhost:3306/bi_ecommerce"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bi_ecommerce.db")

print("Exporting MySQL -> SQLite...")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

mysql = create_engine(MYSQL_URL)
conn_sqlite = sqlite3.connect(DB_PATH)

tabelas = ["dim_clientes", "dim_produtos", "dim_calendario", "dim_vendedores", "fact_vendas"]

with mysql.connect() as conn:
    for tabela in tabelas:
        df = pd.read_sql(text(f"SELECT * FROM {tabela}"), conn)
        df.to_sql(tabela, conn_sqlite, if_exists="replace", index=False)
        print(f"  {tabela}: {len(df)} linhas")

conn_sqlite.close()
mysql.dispose()

tamanho = os.path.getsize(DB_PATH) / 1024
print(f"\nArquivo: {DB_PATH} ({tamanho:.0f} KB)")
print("OK!")
