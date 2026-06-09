#!/usr/bin/env python3
"""
setup_mysql.py - Carrega camada Gold no MySQL para consumo do Power BI

Cria o banco bi_ecommerce, as tabelas Star Schema e popula com os dados
dos arquivos Parquet em data/gold/.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gold_dir = os.path.join(projeto_root, "data", "gold")

MYSQL_USER = "root"
MYSQL_PASS = "root"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
DB_NAME = "bi_ecommerce"


def main():
    print("=" * 60)
    print("  SETUP MYSQL - BI E-COMMERCE")
    print("=" * 60)

    # Conectar sem selecionar banco para criar o database
    root_engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}"
    )

    with root_engine.connect() as conn:
        conn.execute(text(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        ))
        conn.commit()
    root_engine.dispose()

    print(f"Banco '{DB_NAME}' criado/verificado.")

    # Conectar ao banco bi_ecommerce
    engine = create_engine(
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{DB_NAME}"
    )

    tables = [
        {
            "name": "dim_clientes",
            "parquet": os.path.join(gold_dir, "dim_clientes", "data.parquet"),
            "pk": "ALTER TABLE dim_clientes ADD PRIMARY KEY (id_cliente)",
            "date_cols": [],
        },
        {
            "name": "dim_produtos",
            "parquet": os.path.join(gold_dir, "dim_produtos", "data.parquet"),
            "pk": "ALTER TABLE dim_produtos ADD PRIMARY KEY (id_produto(20))",
            "date_cols": [],
        },
        {
            "name": "dim_calendario",
            "parquet": os.path.join(gold_dir, "dim_calendario", "data.parquet"),
            "pk": "ALTER TABLE dim_calendario ADD PRIMARY KEY (data)",
            "date_cols": ["data"],
        },
        {
            "name": "dim_vendedores",
            "parquet": os.path.join(gold_dir, "dim_vendedores", "data.parquet"),
            "pk": "ALTER TABLE dim_vendedores ADD PRIMARY KEY (id_vendedor)",
            "date_cols": [],
        },
        {
            "name": "fact_vendas",
            "parquet": os.path.join(gold_dir, "fact_vendas", "data.parquet"),
            "pk": None,
            "date_cols": ["data_pedido"],
            "indexes": [
                "CREATE INDEX idx_fact_cliente  ON fact_vendas (id_cliente)",
                "CREATE INDEX idx_fact_produto  ON fact_vendas (id_produto(20))",
                "CREATE INDEX idx_fact_data     ON fact_vendas (data_pedido)",
                "CREATE INDEX idx_fact_vendedor ON fact_vendas (id_vendedor)",
            ],
        },
    ]

    with engine.connect() as conn:
        for t in tables:
            name = t["name"]
            path = t["parquet"]
            print(f"\n--- {name} ---")

            df = pd.read_parquet(path)
            for col in t["date_cols"]:
                df[col] = pd.to_datetime(df[col]).dt.date

            df.to_sql(name, engine, if_exists="replace", index=False, chunksize=1000)
            print(f"  {len(df):,} linhas carregadas")

            if t["pk"]:
                conn.execute(text(t["pk"]))
                conn.commit()
                print(f"  PK criada")

            if t.get("indexes"):
                for idx_sql in t["indexes"]:
                    conn.execute(text(idx_sql))
                    conn.commit()
                print(f"  Indices criados")

    # Verificar tabelas
    print("\n" + "=" * 60)
    print("  TABELAS NO BANCO")
    print("=" * 60)

    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT TABLE_NAME, TABLE_ROWS "
            "FROM information_schema.tables "
            "WHERE table_schema = :db "
            "ORDER BY TABLE_NAME"
        ), {"db": DB_NAME})

        for row in result:
            print(f"  {row[0]:25s} {row[1]:,} linhas")

    engine.dispose()

    print("\n" + "=" * 60)
    print("  CONEXAO POWER BI")
    print("=" * 60)
    print(f"  Servidor: {MYSQL_HOST}:{MYSQL_PORT}")
    print(f"  Banco:    {DB_NAME}")
    print(f"  Usuario:  {MYSQL_USER}")
    print(f"  Senha:    {MYSQL_PASS}")
    print(f"\n  Power BI -> Obter Dados -> Banco de Dados MySQL")
    print(f"  Digite servidor: {MYSQL_HOST}:{MYSQL_PORT}")
    print(f"  Digite banco: {DB_NAME}")
    print(f"  Selecione as 5 tabelas e clique em Carregar")
    print(f"\nSCRIPT CONCLUIDO.")


if __name__ == "__main__":
    main()
