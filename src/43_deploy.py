#!/usr/bin/env python3
"""
43_deploy.py - Exporta CSVs da Gold para deploy/ e envia ao Hugging Face Spaces
"""
import os
import sys
import subprocess
import pandas as pd
from datetime import datetime

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
deploy_dir = os.path.join(projeto_root, "deploy")
deploy_data = os.path.join(deploy_dir, "data")
gold_dir = os.path.join(projeto_root, "data", "gold")

tabelas = {
    "dim_clientes":    os.path.join(gold_dir, "dim_clientes", "data.parquet"),
    "dim_produtos":    os.path.join(gold_dir, "dim_produtos", "data.parquet"),
    "dim_calendario":  os.path.join(gold_dir, "dim_calendario", "data.parquet"),
    "dim_vendedores":  os.path.join(gold_dir, "dim_vendedores", "data.parquet"),
    "fact_vendas":     os.path.join(gold_dir, "fact_vendas", "data.parquet"),
}


def export_csvs():
    os.makedirs(deploy_data, exist_ok=True)
    for nome, path in tabelas.items():
        df = pd.read_parquet(path)
        csv_path = os.path.join(deploy_data, f"{nome}.csv")
        df.to_csv(csv_path, index=False)
        print(f"  {nome}: {len(df)} linhas -> {csv_path}")


def copy_sqlite():
    src = os.path.join(projeto_root, "data", "bi_ecommerce.db")
    dst_data = os.path.join(deploy_data, "bi_ecommerce.db")
    if os.path.exists(src):
        import shutil
        shutil.copy2(src, dst_data)
        tamanho = os.path.getsize(src) / 1024
        print(f"  bi_ecommerce.db copiado ({tamanho:.0f} KB)")


def git_push():
    if not os.path.isdir(os.path.join(deploy_dir, ".git")):
        print("  [AVISO] Repositorio git nao encontrado em deploy/ - pulando push")
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        subprocess.run(
            ["git", "add", "."],
            cwd=deploy_dir,
            capture_output=True,
            check=True,
        )

        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=deploy_dir,
            capture_output=True,
            text=True,
            check=True,
        )

        if not status.stdout.strip():
            print("  Nenhuma alteracao para commitar")
            return True

        subprocess.run(
            ["git", "commit", "-m", f"Pipeline deploy {timestamp}"],
            cwd=deploy_dir,
            capture_output=True,
            check=True,
        )
        print(f"  Commit: Pipeline deploy {timestamp}")

        result = subprocess.run(
            ["git", "push", "origin", "HEAD"],
            cwd=deploy_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("  Push concluido - Hugging Face Spaces atualizado")
            return True
        else:
            print(f"  [AVISO] Push falhou: {result.stderr.strip()}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"  [AVISO] Erro no git: {e}")
        return False


def main():
    print("=" * 60)
    print("  DEPLOY - HUGGING FACE SPACES")
    print("=" * 60)

    print("\n[1/3] Exportando CSVs...")
    export_csvs()

    print("\n[2/3] Copiando SQLite...")
    copy_sqlite()

    print("\n[3/3] Enviando para Hugging Face...")
    git_push()

    print("\n" + "=" * 60)
    print("  DEPLOY CONCLUIDO")
    print(f"  Dashboard: https://Nagalli-01-bi-ecommerce-dashboard.hf.space")
    print("=" * 60)


if __name__ == "__main__":
    main()
