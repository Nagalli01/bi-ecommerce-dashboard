#!/usr/bin/env python3
"""
10_bronze_ingestion.py - Ingestao Bronze (Validacao e Catalogacao)

Le os arquivos parquet de data/bronze/ usando pandas + pyarrow.
Registra metadados e verifica integridade dos dados brutos.
Medallion Architecture: Bronze Layer.
"""

import os
import sys

import pandas as pd
import pyarrow.parquet as pq

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bronze_dir = os.path.join(projeto_root, "data", "bronze")
os.makedirs(bronze_dir, exist_ok=True)

TABELAS = {
    "clientes": os.path.join(bronze_dir, "clientes.parquet"),
    "produtos": os.path.join(bronze_dir, "produtos.parquet"),
    "pedidos": os.path.join(bronze_dir, "pedidos.parquet"),
}


def main():
    print("=" * 60)
    print("  INGESTAO BRONZE - VALIDACAO E CATALOGACAO")
    print("=" * 60)

    row_counts = {}

    for nome, parquet_path in TABELAS.items():
        print(f"\n--- Processando: {nome.upper()} ---")
        print(f"  Arquivo: {parquet_path}")

        if not os.path.exists(parquet_path):
            print(f"  ERRO: Arquivo parquet nao encontrado: {parquet_path}")
            sys.exit(1)

        try:
            pf = pq.ParquetFile(parquet_path)
            schema = pf.schema_arrow
            count = pf.metadata.num_rows
            row_counts[nome] = count

            print(f"  Linhas: {count}")
            print(f"  Schema ({len(schema.names)} colunas):")
            for i, name in enumerate(schema.names):
                print(f"    {i+1:2d}. {name:30s} : {schema.field(i).type}")

            df = pd.read_parquet(parquet_path)
            nulls = df.isnull().sum()
            nulls_pct = (nulls / len(df) * 100).round(2)
            null_cols = nulls[nulls > 0]
            if len(null_cols) > 0:
                print(f"  Colunas com nulos:")
                for col in null_cols.index:
                    print(f"    {col}: {null_cols[col]} ({nulls_pct[col]}%)")
            else:
                print(f"  Nenhum valor nulo encontrado.")

        except Exception as e:
            print(f"  ERRO ao processar {nome}: {e}")
            sys.exit(1)

    print("\n" + "=" * 60)
    print("  RESUMO DA INGESTAO BRONZE")
    print("=" * 60)
    for nome, count in row_counts.items():
        print(f"  {nome:15s}: {count:6d} linhas")
    print(f"\nINGESTAO BRONZE CONCLUIDA.")


if __name__ == "__main__":
    main()
