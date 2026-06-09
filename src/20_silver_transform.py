#!/usr/bin/env python3
"""
20_silver_transform.py - Transformacao Silver

Le dados da camada Bronze, aplica limpeza, padronizacao e
enriquecimento. Gera arquivos parquet curados em data/silver/.
Medallion Architecture: Silver Layer.
"""

import os
import sys

import pandas as pd
import numpy as np

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bronze_dir = os.path.join(projeto_root, "data", "bronze")
silver_dir = os.path.join(projeto_root, "data", "silver")

os.makedirs(os.path.join(silver_dir, "clientes"), exist_ok=True)
os.makedirs(os.path.join(silver_dir, "produtos"), exist_ok=True)
os.makedirs(os.path.join(silver_dir, "pedidos"), exist_ok=True)


def title_case_pt(s):
    if not isinstance(s, str):
        return s
    excecoes = {"da", "de", "do", "das", "dos", "e"}
    palavras = s.strip().split()
    resultado = []
    for i, p in enumerate(palavras):
        if p.lower() in excecoes and i > 0:
            resultado.append(p.lower())
        else:
            resultado.append(p.capitalize())
    return " ".join(resultado)


def main():
    print("=" * 60)
    print("  TRANSFORMACAO SILVER - LIMPEZA E ENRIQUECIMENTO")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Silver Clientes
    # ---------------------------------------------------------------
    print("\n--- Silver Clientes ---")
    df_cli = pd.read_parquet(os.path.join(bronze_dir, "clientes.parquet"))
    count_orig = len(df_cli)
    print(f"  Linhas bronze: {count_orig}")

    df_cli["nome"] = df_cli["nome"].apply(title_case_pt)
    df_cli["cidade"] = df_cli["cidade"].apply(title_case_pt)
    df_cli["email"] = df_cli["email"].str.strip().str.lower()
    df_cli["estado"] = df_cli["estado"].str.strip().str.upper()
    df_cli["regiao"] = df_cli["regiao"].str.strip().apply(title_case_pt)

    df_cli["data_cadastro"] = pd.to_datetime(df_cli["data_cadastro"]).dt.date

    before = len(df_cli)
    df_cli = df_cli.dropna(subset=["cliente_id"])
    after = len(df_cli)
    if before != after:
        print(f"  Removidas {before - after} linhas com cliente_id nulo")

    before = len(df_cli)
    df_cli = df_cli.drop_duplicates(subset=["cliente_id"], keep="first")
    after = len(df_cli)
    if before != after:
        print(f"  Removidas {before - after} duplicatas por cliente_id")

    path = os.path.join(silver_dir, "clientes", "data.parquet")
    df_cli.to_parquet(path, index=False)
    print(f"  Linhas silver: {len(df_cli)}")
    print(f"  Salvo em: {path}")

    # ---------------------------------------------------------------
    # Silver Produtos
    # ---------------------------------------------------------------
    print("\n--- Silver Produtos ---")
    df_prod = pd.read_parquet(os.path.join(bronze_dir, "produtos.parquet"))
    count_orig = len(df_prod)
    print(f"  Linhas bronze: {count_orig}")

    df_prod["sku"] = df_prod["sku"].str.strip().str.upper()
    df_prod["nome_produto"] = df_prod["nome_produto"].apply(title_case_pt)
    df_prod["categoria"] = df_prod["categoria"].apply(title_case_pt)
    df_prod["subcategoria"] = df_prod["subcategoria"].apply(title_case_pt)
    df_prod["preco_venda"] = df_prod["preco_venda"].round(2)
    df_prod["preco_custo"] = df_prod["preco_custo"].round(2)

    before = len(df_prod)
    df_prod = df_prod.dropna(subset=["sku"])
    df_prod = df_prod[df_prod["preco_venda"] > 0]
    after = len(df_prod)
    if before != after:
        print(f"  Removidas {before - after} linhas invalidas (sku nulo ou preco <= 0)")

    before = len(df_prod)
    df_prod = df_prod.drop_duplicates(subset=["sku"], keep="first")
    after = len(df_prod)
    if before != after:
        print(f"  Removidas {before - after} duplicatas por sku")

    path = os.path.join(silver_dir, "produtos", "data.parquet")
    df_prod.to_parquet(path, index=False)
    print(f"  Linhas silver: {len(df_prod)}")
    print(f"  Salvo em: {path}")

    # ---------------------------------------------------------------
    # Silver Pedidos (com enriquecimento)
    # ---------------------------------------------------------------
    print("\n--- Silver Pedidos ---")
    df_ped = pd.read_parquet(os.path.join(bronze_dir, "pedidos.parquet"))
    count_orig = len(df_ped)
    print(f"  Linhas bronze: {count_orig}")

    df_ped["data_pedido"] = pd.to_datetime(df_ped["data_pedido"]).dt.date
    df_ped["quantidade"] = df_ped["quantidade"].astype(int)
    df_ped["valor_frete"] = df_ped["valor_frete"].round(2)

    before = len(df_ped)
    df_ped = df_ped.dropna(subset=["pedido_id", "cliente_id", "sku"])
    after = len(df_ped)
    if before != after:
        print(f"  Removidas {before - after} linhas com chaves nulas")

    before = len(df_ped)
    df_ped = df_ped.drop_duplicates(subset=["pedido_id"], keep="first")
    after = len(df_ped)
    if before != after:
        print(f"  Removidas {before - after} duplicatas por pedido_id")

    df_merged = df_ped.merge(
        df_prod[["sku", "preco_venda"]],
        on="sku",
        how="left",
    )

    if df_merged["preco_venda"].isnull().any():
        nulos = df_merged["preco_venda"].isnull().sum()
        print(f"  ATENCAO: {nulos} pedidos sem preco_venda (sku nao encontrado em produtos)")
        print(f"  Preenchendo com 0...")
        df_merged["preco_venda"] = df_merged["preco_venda"].fillna(0.0)

    df_merged["total_pedido"] = (df_merged["quantidade"] * df_merged["preco_venda"]).round(2)

    df_ped_final = df_merged[[
        "pedido_id", "cliente_id", "sku", "data_pedido",
        "quantidade", "valor_frete", "total_pedido",
        "municipio", "estado", "regiao", "id_vendedor",
    ]]

    path = os.path.join(silver_dir, "pedidos", "data.parquet")
    df_ped_final.to_parquet(path, index=False)
    print(f"  Linhas silver: {len(df_ped_final)}")
    print(f"  Salvo em: {path}")

    # ---------------------------------------------------------------
    # Resumo
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  RESUMO TRANSFORMACAO SILVER")
    print("=" * 60)
    print(f"  silver_clientes : {len(df_cli):6d} linhas")
    print(f"  silver_produtos : {len(df_prod):6d} linhas")
    print(f"  silver_pedidos  : {len(df_ped_final):6d} linhas")
    print(f"\nTRANSFORMACAO SILVER CONCLUIDA.")


if __name__ == "__main__":
    main()
