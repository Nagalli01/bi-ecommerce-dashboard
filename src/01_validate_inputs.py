#!/usr/bin/env python3
"""
01_validate_inputs.py - Validacao de Schema dos Dados Bronze

Le os arquivos parquet em data/bronze/ e gera relatorio de validacao:
- Schema (colunas e tipos)
- Contagem de linhas
- Nulos por coluna
- Amostra de dados
"""

import os
import sys
from datetime import datetime

import pandas as pd

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bronze_dir = os.path.join(projeto_root, "data", "bronze")
os.makedirs(bronze_dir, exist_ok=True)

ARQUIVOS = {
    "clientes": "clientes.parquet",
    "produtos": "produtos.parquet",
    "pedidos": "pedidos.parquet",
}


def validate_file(nome_tabela, filename):
    filepath = os.path.join(bronze_dir, filename)
    if not os.path.exists(filepath):
        return f"ERRO: Arquivo nao encontrado: {filepath}"

    df = pd.read_parquet(filepath, engine="pyarrow")

    lines = []
    lines.append("=" * 60)
    lines.append(f"  TABELA: {nome_tabela.upper()}")
    lines.append("=" * 60)
    lines.append(f"Arquivo: {filepath}")
    lines.append("")

    lines.append("--- SCHEMA ---")
    for col, dtype in df.dtypes.items():
        lines.append(f"  {col}: {dtype}")
    lines.append(f"\nTotal de colunas: {len(df.columns)}")
    lines.append("")

    lines.append("--- ROW COUNT ---")
    lines.append(f"Total de linhas: {len(df)}")
    lines.append("")

    lines.append("--- VALORES NULOS ---")
    nulls = df.isnull().sum()
    total = len(df)
    has_nulls = False
    for col, n_null in nulls.items():
        pct = (n_null / total) * 100 if total > 0 else 0
        lines.append(f"  {col}: {n_null} nulos ({pct:.2f}%)")
        if n_null > 0:
            has_nulls = True
    if not has_nulls:
        lines.append("  Nenhuma coluna possui valores nulos.")
    lines.append("")

    lines.append("--- AMOSTRA (5 LINHAS) ---")
    lines.append(df.head(5).to_string(index=False))
    lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("  VALIDACAO DE SCHEMA - BRONZE")
    print("=" * 60)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_lines = []
    log_lines.append(f"RELATORIO DE VALIDACAO - BRONZE")
    log_lines.append(f"Gerado em: {timestamp}")
    log_lines.append(f"Projeto: {projeto_root}")
    log_lines.append("")

    for nome_tabela, filename in ARQUIVOS.items():
        try:
            result = validate_file(nome_tabela, filename)
            log_lines.append(result)
            print(result)
        except Exception as e:
            error_msg = f"ERRO na tabela {nome_tabela}: {e}"
            log_lines.append(error_msg)
            print(error_msg)

    log_path = os.path.join(bronze_dir, "validation_log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

    print(f"\nLog de validacao salvo em: {log_path}")
    print("\nVALIDACAO CONCLUIDA.")


if __name__ == "__main__":
    main()
