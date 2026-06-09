#!/usr/bin/env python3
"""
run_pipeline.py - Orquestrador do Pipeline BI E-Commerce

Executa todas as etapas do pipeline em sequencia, usando subprocess.
Arquitetura Medallion: Bronze -> Silver -> Gold
Inclui carga MySQL, export SQLite e deploy automatico.
"""

import subprocess
import sys
import os
import time
from datetime import datetime


def run_step(script_name, description):
    print(f"\n{'#' * 60}")
    print(f"# {description}")
    print(f"{'#' * 60}")
    start = time.time()
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    projeto_root = os.path.dirname(os.path.dirname(__file__))
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=projeto_root,
        capture_output=False,
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"\n[OK] SUCESSO - {description} ({elapsed:.1f}s)")
    else:
        print(f"\n[ERRO] FALHA - {description} (codigo {result.returncode})")
        print("Pipeline interrompido.")
        sys.exit(1)
    return elapsed


def run_step_optional(script_name, description):
    print(f"\n{'#' * 60}")
    print(f"# {description} (opcional)")
    print(f"{'#' * 60}")
    start = time.time()
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    projeto_root = os.path.dirname(os.path.dirname(__file__))
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=projeto_root,
        capture_output=False,
    )
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"\n[OK] SUCESSO - {description} ({elapsed:.1f}s)")
    else:
        print(f"\n[AVISO] FALHA - {description} (codigo {result.returncode})")
        print("Etapa opcional ignorada - pipeline continua.")
    return elapsed


def main():
    print(f"{'=' * 60}")
    print(f"  PIPELINE BI E-COMMERCE - ARQUITETURA MEDALHAO")
    print(f"{'=' * 60}")
    total_start = time.time()
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Projeto: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")

    mandatory = [
        ("00_generate_data.py",    "GERACAO DE DADOS SINTETICOS"),
        ("01_validate_inputs.py",  "VALIDACAO DE SCHEMA (BRONZE)"),
        ("10_bronze_ingestion.py", "INGESTAO BRONZE -> PARQUET"),
        ("20_silver_transform.py", "TRANSFORMACAO SILVER"),
        ("30_gold_model.py",       "MODELAGEM GOLD (STAR SCHEMA)"),
        ("40_quality_checks.py",   "QUALITY CHECKS FINAIS"),
    ]

    optional = [
        ("setup_mysql.py",         "CARGA MYSQL (POWER BI)"),
        ("export_sqlite.py",       "EXPORT SQLITE (DASHBOARD WEB)"),
        ("43_deploy.py",           "DEPLOY HUGGING FACE SPACES"),
    ]

    total_elapsed = 0.0

    for script, desc in mandatory:
        elapsed = run_step(script, desc)
        total_elapsed += elapsed

    for script, desc in optional:
        elapsed = run_step_optional(script, desc)
        total_elapsed += elapsed

    total = time.time() - total_start
    print(f"\n{'=' * 60}")
    print(f"  PIPELINE CONCLUIDO COM SUCESSO!")
    print(f"{'=' * 60}")
    print(f"Tempo total: {total:.1f}s ({total / 60:.1f} min)")
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nPower BI: conecte ao MySQL (localhost:3306 / bi_ecommerce)")
    print(f"Dashboard: https://Nagalli-01-bi-ecommerce-dashboard.hf.space")


if __name__ == "__main__":
    main()
