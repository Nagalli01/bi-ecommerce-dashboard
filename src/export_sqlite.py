#!/usr/bin/env python3
"""Export Gold tables to SQLite for local web dashboard"""
import pandas as pd
from sqlalchemy import create_engine, text
import sqlite3
import os
import sys

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gold_dir = os.path.join(projeto_root, "data", "gold")
MYSQL_URL = "mysql+pymysql://root:root@localhost:3306/bi_ecommerce"
DB_PATH = os.path.join(projeto_root, "data", "bi_ecommerce.db")

tabelas = ["dim_clientes", "dim_produtos", "dim_calendario", "dim_vendedores", "fact_vendas"]
parquet_map = {
    "dim_clientes":   os.path.join(gold_dir, "dim_clientes", "data.parquet"),
    "dim_produtos":   os.path.join(gold_dir, "dim_produtos", "data.parquet"),
    "dim_calendario": os.path.join(gold_dir, "dim_calendario", "data.parquet"),
    "dim_vendedores": os.path.join(gold_dir, "dim_vendedores", "data.parquet"),
    "fact_vendas":    os.path.join(gold_dir, "fact_vendas", "data.parquet"),
}

print("Exportando para SQLite...")
print(f"Destino: {DB_PATH}")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn_sqlite = sqlite3.connect(DB_PATH)

try:
    mysql = create_engine(MYSQL_URL)
    with mysql.connect() as conn:
        conn.execute(text("SELECT 1"))
    mysql_ok = True
except Exception:
    print("  MySQL nao disponivel - exportando direto dos parquets")
    mysql_ok = False

if mysql_ok:
    with mysql.connect() as conn:
        for tabela in tabelas:
            df = pd.read_sql(text(f"SELECT * FROM {tabela}"), conn)
            df.to_sql(tabela, conn_sqlite, if_exists="replace", index=False)
            print(f"  {tabela}: {len(df)} linhas (via MySQL)")
    mysql.dispose()
else:
    for tabela in tabelas:
        path = parquet_map[tabela]
        if os.path.exists(path):
            df = pd.read_parquet(path)
            df.to_sql(tabela, conn_sqlite, if_exists="replace", index=False)
            print(f"  {tabela}: {len(df)} linhas (via Parquet)")

conn_sqlite.close()

tamanho = os.path.getsize(DB_PATH) / 1024
print(f"\nArquivo: {DB_PATH} ({tamanho:.0f} KB)")
print("OK!")
