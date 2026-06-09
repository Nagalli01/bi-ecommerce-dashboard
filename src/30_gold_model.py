#!/usr/bin/env python3
"""
30_gold_model.py - Modelagem Gold (Star Schema)

Le dados da camada Silver e constroi o modelo dimensional:
- dim_clientes
- dim_produtos
- dim_calendario
- dim_vendedores
- fact_vendas

Medallion Architecture: Gold Layer (Star Schema).
"""

import os
import sys

import pandas as pd
import numpy as np

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
silver_dir = os.path.join(projeto_root, "data", "silver")
gold_dir = os.path.join(projeto_root, "data", "gold")

for sub in ["dim_clientes", "dim_produtos", "dim_calendario", "dim_vendedores", "fact_vendas"]:
    os.makedirs(os.path.join(gold_dir, sub), exist_ok=True)

MESES_PT = [
    "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

VENDEDORES = [
    (1,  "Carlos Mendes",    "Sudeste"),
    (2,  "Ana Beatriz",      "Sudeste"),
    (3,  "Roberto Nunes",    "Sudeste"),
    (4,  "Fernanda Lima",    "Sul"),
    (5,  "Paulo Cesar",      "Sul"),
    (6,  "Juliana Alves",    "Sul"),
    (7,  "Ricardo Souza",    "Nordeste"),
    (8,  "Mariana Costa",    "Nordeste"),
    (9,  "Lucas Pereira",    "Nordeste"),
    (10, "Camila Rocha",     "Norte"),
    (11, "Eduardo Santos",   "Norte"),
    (12, "Patricia Gomes",   "Norte"),
    (13, "Felipe Oliveira",  "Centro-Oeste"),
    (14, "Tatiane Martins",  "Centro-Oeste"),
    (15, "Gustavo Barbosa",  "Centro-Oeste"),
]


def main():
    print("=" * 60)
    print("  MODELAGEM GOLD - STAR SCHEMA")
    print("=" * 60)

    # ---------------------------------------------------------------
    # dim_clientes
    # ---------------------------------------------------------------
    print("\n--- dim_clientes ---")
    df_cli = pd.read_parquet(os.path.join(silver_dir, "clientes", "data.parquet"))
    df_dim_cli = df_cli[["cliente_id", "nome", "cidade", "estado", "regiao"]].copy()
    df_dim_cli = df_dim_cli.rename(columns={"cliente_id": "id_cliente"})
    df_dim_cli = df_dim_cli.drop_duplicates(subset=["id_cliente"])
    path = os.path.join(gold_dir, "dim_clientes", "data.parquet")
    df_dim_cli.to_parquet(path, index=False)
    print(f"  Linhas: {len(df_dim_cli)}")
    print(f"  Colunas: {list(df_dim_cli.columns)}")

    # ---------------------------------------------------------------
    # dim_produtos
    # ---------------------------------------------------------------
    print("\n--- dim_produtos ---")
    df_prod = pd.read_parquet(os.path.join(silver_dir, "produtos", "data.parquet"))
    df_dim_prod = df_prod[["sku", "nome_produto", "categoria", "preco_venda"]].copy()
    df_dim_prod = df_dim_prod.rename(columns={"sku": "id_produto"})
    df_dim_prod = df_dim_prod.drop_duplicates(subset=["id_produto"])
    path = os.path.join(gold_dir, "dim_produtos", "data.parquet")
    df_dim_prod.to_parquet(path, index=False)
    print(f"  Linhas: {len(df_dim_prod)}")
    print(f"  Colunas: {list(df_dim_prod.columns)}")

    # ---------------------------------------------------------------
    # dim_calendario
    # ---------------------------------------------------------------
    print("\n--- dim_calendario ---")
    df_ped = pd.read_parquet(os.path.join(silver_dir, "pedidos", "data.parquet"))
    min_date = pd.to_datetime(df_ped["data_pedido"]).min()
    max_date = pd.to_datetime(df_ped["data_pedido"]).max()
    print(f"  Range de datas: {min_date.date()} ate {max_date.date()}")

    date_range = pd.date_range(start=min_date, end=max_date, freq="D")
    df_cal = pd.DataFrame({"data": date_range})
    df_cal["data"] = df_cal["data"].dt.date
    df_cal["dia"] = df_cal["data"].apply(lambda x: x.day)
    df_cal["mes"] = df_cal["data"].apply(lambda x: x.month)
    df_cal["nome_mes"] = df_cal["mes"].apply(lambda m: MESES_PT[m - 1])
    df_cal["mes_num"] = df_cal["mes"]
    df_cal["trimestre"] = df_cal["mes"].apply(lambda m: (m - 1) // 3 + 1)
    df_cal["ano"] = df_cal["data"].apply(lambda x: x.year)

    path = os.path.join(gold_dir, "dim_calendario", "data.parquet")
    df_cal.to_parquet(path, index=False)
    print(f"  Linhas: {len(df_cal)}")
    print(f"  Colunas: {list(df_cal.columns)}")

    # ---------------------------------------------------------------
    # dim_vendedores
    # ---------------------------------------------------------------
    print("\n--- dim_vendedores ---")
    df_vend = pd.DataFrame(VENDEDORES, columns=["id_vendedor", "nome", "regiao"])
    path = os.path.join(gold_dir, "dim_vendedores", "data.parquet")
    df_vend.to_parquet(path, index=False)
    print(f"  Linhas: {len(df_vend)}")
    print(f"  Colunas: {list(df_vend.columns)}")
    print(f"  Vendedores: {', '.join(df_vend['nome'].tolist())}")

    # ---------------------------------------------------------------
    # fact_vendas
    # ---------------------------------------------------------------
    print("\n--- fact_vendas ---")
    df_fact = df_ped.copy()
    df_fact = df_fact.rename(columns={
        "cliente_id": "id_cliente",
        "sku": "id_produto",
    })
    df_fact = df_fact[[
        "pedido_id", "id_cliente", "id_produto", "data_pedido",
        "id_vendedor", "quantidade", "valor_frete", "total_pedido",
        "municipio", "estado", "regiao",
    ]]

    path = os.path.join(gold_dir, "fact_vendas", "data.parquet")
    df_fact.to_parquet(path, index=False)
    print(f"  Linhas: {len(df_fact)}")
    print(f"  Colunas: {list(df_fact.columns)}")

    # ---------------------------------------------------------------
    # Resumo
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  RESUMO STAR SCHEMA (GOLD)")
    print("=" * 60)
    print(f"  dim_clientes    : {len(df_dim_cli):6d} linhas  PK: id_cliente")
    print(f"  dim_produtos    : {len(df_dim_prod):6d} linhas  PK: id_produto")
    print(f"  dim_calendario  : {len(df_cal):6d} linhas  PK: data")
    print(f"  dim_vendedores  : {len(df_vend):6d} linhas  PK: id_vendedor")
    print(f"  fact_vendas     : {len(df_fact):6d} linhas")
    print(f"\nMODELAGEM GOLD CONCLUIDA.")


if __name__ == "__main__":
    main()
