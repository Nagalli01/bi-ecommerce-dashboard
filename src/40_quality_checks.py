#!/usr/bin/env python3
"""
40_quality_checks.py - Quality Checks Finais

Realiza verificacoes abrangentes de qualidade dos dados
nas camadas Silver e Gold. Gera relatorio em data/quality_report.txt.
"""

import os
import sys
from datetime import datetime

import pandas as pd
import numpy as np

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
silver_dir = os.path.join(projeto_root, "data", "silver")
gold_dir = os.path.join(projeto_root, "data", "gold")
report_path = os.path.join(projeto_root, "data", "quality_report.txt")

PASS = "[PASS]"
FAIL = "[FAIL]"
INFO = "[INFO]"

results = []


def log(line):
    print(line)
    results.append(line)


def main():
    print("=" * 60)
    print("  QUALITY CHECKS FINAIS")
    print("=" * 60)

    # ---------------------------------------------------------------
    # Load data
    # ---------------------------------------------------------------
    df_s_cli = pd.read_parquet(os.path.join(silver_dir, "clientes", "data.parquet"))
    df_s_prod = pd.read_parquet(os.path.join(silver_dir, "produtos", "data.parquet"))
    df_s_ped = pd.read_parquet(os.path.join(silver_dir, "pedidos", "data.parquet"))

    df_dim_cli = pd.read_parquet(os.path.join(gold_dir, "dim_clientes", "data.parquet"))
    df_dim_prod = pd.read_parquet(os.path.join(gold_dir, "dim_produtos", "data.parquet"))
    df_dim_cal = pd.read_parquet(os.path.join(gold_dir, "dim_calendario", "data.parquet"))
    df_dim_vend = pd.read_parquet(os.path.join(gold_dir, "dim_vendedores", "data.parquet"))
    df_fact = pd.read_parquet(os.path.join(gold_dir, "fact_vendas", "data.parquet"))

    # ---------------------------------------------------------------
    # 1. Row counts per layer
    # ---------------------------------------------------------------
    log("\n" + "=" * 40)
    log("1. CONTAGENS POR CAMADA")
    log("=" * 40)

    checks = [
        ("Silver Clientes", len(df_s_cli), "> 0"),
        ("Silver Produtos", len(df_s_prod), "> 0"),
        ("Silver Pedidos",  len(df_s_ped),  "> 0"),
        ("dim_clientes",    len(df_dim_cli), "<= 1500"),
        ("dim_produtos",    len(df_dim_prod), "<= 250"),
        ("dim_calendario",  len(df_dim_cal), "> 0"),
        ("dim_vendedores",  len(df_dim_vend), "== 15"),
        ("fact_vendas",     len(df_fact),    "<= 8000"),
    ]

    for label, count, expected in checks:
        log(f"  {label:20s}: {count:6d}  (esperado: {expected})")

    # ---------------------------------------------------------------
    # 2. Null analysis
    # ---------------------------------------------------------------
    log("\n" + "=" * 40)
    log("2. ANALISE DE NULOS (% nas colunas-chave)")
    log("=" * 40)

    null_checks = [
        ("dim_clientes", df_dim_cli, ["id_cliente", "nome", "cidade", "estado", "regiao"]),
        ("dim_produtos", df_dim_prod, ["id_produto", "nome_produto", "categoria", "preco_venda"]),
        ("dim_calendario", df_dim_cal, ["data", "dia", "mes", "nome_mes", "trimestre", "ano"]),
        ("dim_vendedores", df_dim_vend, ["id_vendedor", "nome", "regiao"]),
        ("fact_vendas", df_fact, ["pedido_id", "id_cliente", "id_produto", "data_pedido", "id_vendedor", "total_pedido"]),
    ]

    for table_name, df, cols in null_checks:
        log(f"\n  [{table_name}]")
        for col in cols:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                null_pct = (null_count / len(df) * 100).round(2) if len(df) > 0 else 0.0
                status = PASS if null_pct == 0 else f"{FAIL} ({null_count} registros)"
                log(f"    {col:20s}: {null_pct:6.2f}%  {status}")

    # ---------------------------------------------------------------
    # 3. Referential integrity
    # ---------------------------------------------------------------
    log("\n" + "=" * 40)
    log("3. INTEGRIDADE REFERENCIAL (ORFAOS)")
    log("=" * 40)

    ref_checks = [
        ("id_cliente", df_fact["id_cliente"].drop_duplicates(), df_dim_cli["id_cliente"].drop_duplicates(), "dim_clientes"),
        ("id_produto", df_fact["id_produto"].drop_duplicates(), df_dim_prod["id_produto"].drop_duplicates(), "dim_produtos"),
        ("id_vendedor", df_fact["id_vendedor"].drop_duplicates(), df_dim_vend["id_vendedor"].drop_duplicates(), "dim_vendedores"),
    ]

    all_clean = True
    for fk_name, fact_keys, dim_keys, dim_name in ref_checks:
        fact_set = set(fact_keys.dropna())
        dim_set = set(dim_keys.dropna())
        orphans = fact_set - dim_set
        if len(orphans) > 0:
            log(f"  {FAIL} fact_vendas.{fk_name} -> {dim_name}: {len(orphans)} orfaos encontrados")
            all_clean = False
        else:
            log(f"  {PASS} fact_vendas.{fk_name} -> {dim_name}: 0 orfaos")

    fact_dates = set(pd.to_datetime(df_fact["data_pedido"]).dropna().apply(lambda x: x.date()))
    cal_dates = set(pd.to_datetime(df_dim_cal["data"]).dropna().apply(lambda x: x.date()))
    date_orphans = fact_dates - cal_dates
    if len(date_orphans) > 0:
        log(f"  {FAIL} fact_vendas.data_pedido -> dim_calendario: {len(date_orphans)} datas orfas")
        all_clean = False
    else:
        log(f"  {PASS} fact_vendas.data_pedido -> dim_calendario: 0 datas orfas")

    if all_clean:
        log(f"\n  >>> Integridade referencial 100% OK.")

    # ---------------------------------------------------------------
    # 4. Date range
    # ---------------------------------------------------------------
    log("\n" + "=" * 40)
    log("4. VALIDACAO DE DATAS")
    log("=" * 40)

    fact_dates_series = pd.to_datetime(df_fact["data_pedido"]).dropna().apply(lambda x: x.date())
    if len(fact_dates_series) > 0:
        min_d = min(fact_dates_series)
        max_d = max(fact_dates_series)
        log(f"  Data minima: {min_d}")
        log(f"  Data maxima: {max_d}")
        log(f"  Range esperado: 2023-01-01 a 2024-12-31")

        if min_d >= pd.Timestamp("2023-01-01").date():
            log(f"  {PASS} Data minima dentro do range esperado.")
        else:
            log(f"  {FAIL} Data minima FORA do range esperado.")

        if max_d <= pd.Timestamp("2024-12-31").date():
            log(f"  {PASS} Data maxima dentro do range esperado.")
        else:
            log(f"  {FAIL} Data maxima FORA do range esperado.")

    # ---------------------------------------------------------------
    # 5. Business metrics
    # ---------------------------------------------------------------
    log("\n" + "=" * 40)
    log("5. METRICAS DE NEGOCIO")
    log("=" * 40)

    faturamento = df_fact["total_pedido"].sum()
    total_pedidos = df_fact["pedido_id"].nunique()
    ticket_medio = faturamento / total_pedidos if total_pedidos > 0 else 0
    total_vendedores = df_fact["id_vendedor"].nunique()
    total_clientes = df_fact["id_cliente"].nunique()
    total_produtos = df_fact["id_produto"].nunique()

    log(f"  Faturamento Total   : R$ {faturamento:,.2f}")
    log(f"  Total Pedidos       : {total_pedidos:,}")
    log(f"  Ticket Medio        : R$ {ticket_medio:,.2f}")
    log(f"  Total Vendedores    : {total_vendedores}")
    log(f"  Clientes Ativos     : {total_clientes}")
    log(f"  Produtos Vendidos   : {total_produtos}")

    if faturamento > 0 and total_pedidos > 0 and ticket_medio > 0:
        log(f"  {PASS} Metricas validas.")
    else:
        log(f"  {FAIL} Metricas invalidas.")

    # ---------------------------------------------------------------
    # 6. Distribution
    # ---------------------------------------------------------------
    log("\n" + "=" * 40)
    log("6. DISTRIBUICAO")
    log("=" * 40)

    log("\n  Top 5 Estados por Faturamento:")
    state_rev = df_fact.groupby("estado")["total_pedido"].sum().sort_values(ascending=False)
    for estado, rev in state_rev.head(5).items():
        log(f"    {estado}: R$ {rev:,.2f}")

    log("\n  Faturamento por Regiao:")
    region_rev = df_fact.groupby("regiao")["total_pedido"].sum().sort_values(ascending=False)
    for regiao, rev in region_rev.items():
        log(f"    {regiao}: R$ {rev:,.2f}")

    log("\n  Top 5 Vendedores:")
    seller_rev = df_fact.groupby("id_vendedor")["total_pedido"].sum().sort_values(ascending=False)
    df_vend_map = df_dim_vend.set_index("id_vendedor")["nome"].to_dict()
    for vid, rev in seller_rev.head(5).items():
        nome = df_vend_map.get(vid, f"ID {vid}")
        log(f"    {nome}: R$ {rev:,.2f}")

    # ---------------------------------------------------------------
    # Save report
    # ---------------------------------------------------------------
    log("\n" + "=" * 40)
    log("RELATORIO SALVO EM: " + report_path)
    log("=" * 40)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"QUALITY REPORT - BI E-COMMERCE\n")
        f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        for line in results:
            f.write(line + "\n")

    print(f"\nQUALITY CHECKS CONCLUIDOS.")


if __name__ == "__main__":
    main()
