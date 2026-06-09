#!/usr/bin/env python3
"""
    00_generate_data.py - Geracao de Dados Sinteticos para Nexus

Gera dados sinteticos realistas para o pipeline de BI:
- 1500 clientes
- 250 produtos
- 8000 pedidos

Utiliza apenas biblioteca padrao Python + pandas/pyarrow.
"""

import os
import random
import datetime
import sys

import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

projeto_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bronze_dir = os.path.join(projeto_root, "data", "bronze")
os.makedirs(bronze_dir, exist_ok=True)

clientes_path = os.path.join(bronze_dir, "clientes.parquet")
produtos_path = os.path.join(bronze_dir, "produtos.parquet")
pedidos_path = os.path.join(bronze_dir, "pedidos.parquet")


def check_idempotent():
    if os.path.exists(clientes_path) and os.path.exists(produtos_path) and os.path.exists(pedidos_path):
        print("Todos os arquivos parquet ja existem em data/bronze/. Geracao ignorada (idempotente).")
        return True
    return False


FIRST_NAMES_M = [
    "Joao", "Jose", "Antonio", "Francisco", "Carlos", "Paulo", "Pedro", "Lucas",
    "Marcos", "Luiz", "Gabriel", "Rafael", "Daniel", "Bruno", "Felipe", "Andre",
    "Marcelo", "Eduardo", "Guilherme", "Leonardo", "Ricardo", "Fernando", "Rodrigo",
    "Diego", "Alexandre", "Vinicius", "Thiago", "Mateus", "Gustavo", "Fabio",
]

FIRST_NAMES_F = [
    "Maria", "Ana", "Francisca", "Antonia", "Juliana", "Marcia", "Fernanda",
    "Patricia", "Aline", "Sandra", "Camila", "Amanda", "Bruna", "Jessica",
    "Leticia", "Beatriz", "Larissa", "Vanessa", "Gabriela", "Carolina",
    "Tatiane", "Priscila", "Renata", "Isabela", "Simone", "Adriana",
    "Claudia", "Mariana", "Luana", "Raquel",
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
    "Pereira", "Lima", "Gomes", "Ribeiro", "Martins", "Carvalho", "Araujo",
    "Barbosa", "Costa", "Rocha", "Nunes", "Mendes", "Vieira",
]

DOMAINS = ["email.com", "provedor.com.br", "webmail.com", "net.com.br", "correio.com"]

CITIES_BY_STATE = {
    "SP": ["Sao Paulo", "Campinas", "Santos", "Sao Jose dos Campos", "Ribeirao Preto", "Sorocaba", "Sao Bernardo do Campo", "Guarulhos", "Osasco", "Piracicaba"],
    "RJ": ["Rio de Janeiro", "Niteroi", "Petropolis", "Nova Iguacu", "Duque de Caxias", "Volta Redonda", "Campos dos Goytacazes", "Angra dos Reis", "Cabo Frio", "Teresopolis"],
    "MG": ["Belo Horizonte", "Uberlandia", "Juiz de Fora", "Contagem", "Betim", "Montes Claros", "Governador Valadares", "Ipatinga", "Pocos de Caldas", "Uberaba"],
    "RS": ["Porto Alegre", "Caxias do Sul", "Pelotas", "Canoas", "Santa Maria", "Gravatai", "Novo Hamburgo", "Passo Fundo", "Bento Goncalves", "Erechim"],
    "PR": ["Curitiba", "Londrina", "Maringa", "Ponta Grossa", "Cascavel", "Foz do Iguacu", "Guarapuava", "Paranagua", "Colombo", "Sao Jose dos Pinhais"],
    "BA": ["Salvador", "Feira de Santana", "Vitoria da Conquista", "Itabuna", "Ilheus", "Juazeiro", "Porto Seguro", "Teixeira de Freitas", "Camacari", "Lauro de Freitas"],
    "PE": ["Recife", "Jaboatao dos Guararapes", "Olinda", "Caruaru", "Petrolina", "Paulista", "Garanhuns", "Igarassu", "Gravata", "Serra Talhada"],
    "CE": ["Fortaleza", "Caucaia", "Juazeiro do Norte", "Maracanau", "Sobral", "Crato", "Iguatu", "Quixada", "Caninde", "Itapipoca"],
    "AM": ["Manaus", "Parintins", "Itacoatiara", "Manacapuru", "Coari", "Tabatinga", "Tefe", "Maues", "Autazes", "Presidente Figueiredo"],
    "DF": ["Brasilia", "Ceilandia", "Taguatinga", "Samambaia", "Planaltina", "Gama", "Aguas Claras", "Guara", "Sobradinho", "Recanto das Emas"],
}

STATE_TO_REGION = {
    "SP": "Sudeste", "RJ": "Sudeste", "MG": "Sudeste",
    "RS": "Sul", "PR": "Sul",
    "BA": "Nordeste", "PE": "Nordeste", "CE": "Nordeste",
    "AM": "Norte",
    "DF": "Centro-Oeste",
}

CATEGORIES = {
    "Smartphones": ["iPhone", "Samsung Galaxy", "Motorola Moto", "Xiaomi Redmi", "Asus Zenfone", "LG", "OnePlus", "Nokia"],
    "Notebooks": ["Dell Inspiron", "Lenovo ThinkPad", "Acer Aspire", "HP Pavilion", "MacBook", "Samsung Book", "Asus VivoBook", "Positivo"],
    "Acessorios": ["Capa Protetora", "Película", "Carregador", "Cabo USB", "Fone de Ouvido", "Suporte", "Adaptador", "Power Bank"],
    "Audio": ["Fone Bluetooth", "Caixa de Som", "Soundbar", "Headset Gamer", "Microfone", "Home Theater", "Amplificador", "Fone Com Fio"],
    "Tablets": ["iPad", "Samsung Tab", "Lenovo Tab", "Amazon Fire", "Multilaser", "Philco", "Positivo", "DL"],
    "Monitores": ["LG Monitor", "Samsung Monitor", "Dell Monitor", "Acer Monitor", "AOC Monitor", "Philips Monitor", "ASUS Monitor", "Lenovo Monitor"],
    "Perifericos": ["Teclado", "Mouse", "Webcam", "Hub USB", "Mousepad", "Headset", "Gamepad", "Leitor de Cartao"],
    "Armazenamento": ["HD Externo", "SSD", "Pen Drive", "Cartao SD", "HD Interno", "SSD NVMe", "SSD SATA", "NAS"],
}

SELLER_IDS = list(range(1, 16))


def random_phone():
    ddd = str(random.randint(11, 99))
    first = str(random.randint(90000, 99999))
    last = str(random.randint(1000, 9999))
    return f"({ddd}) {first}-{last}"


def random_date(start, end):
    delta = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta))


def generate_email(first, last):
    first_clean = first.lower().replace(" ", "").replace("~", "a").replace("ç", "c")
    last_clean = last.lower().replace(" ", "").replace("~", "a").replace("ç", "c")
    dominio = random.choice(DOMAINS)
    return f"{first_clean}.{last_clean}@{dominio}"


def generate_full_name():
    if random.random() < 0.5:
        first = random.choice(FIRST_NAMES_M)
    else:
        first = random.choice(FIRST_NAMES_F)
    last1 = random.choice(LAST_NAMES)
    last2 = random.choice(LAST_NAMES)
    return f"{first} {last1} {last2}"


def generate_clientes(n=1500):
    print(f"Gerando {n} clientes...")
    data = []
    for cliente_id in range(1, n + 1):
        nome = generate_full_name()
        nome_parts = nome.split()
        first = nome_parts[0]
        last = nome_parts[-1]
        email = generate_email(first, last)
        telefone = random_phone()
        estado = random.choice(list(CITIES_BY_STATE.keys()))
        cidade = random.choice(CITIES_BY_STATE[estado])
        regiao = STATE_TO_REGION[estado]
        data_cadastro = random_date(datetime.date(2023, 1, 1), datetime.date(2026, 6, 30))
        data.append({
            "cliente_id": cliente_id,
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "cidade": cidade,
            "estado": estado,
            "regiao": regiao,
            "data_cadastro": data_cadastro,
        })
    return pd.DataFrame(data)


def generate_subcategoria(categoria):
    return random.choice(CATEGORIES[categoria])


def generate_produtos(n=250):
    print(f"Gerando {n} produtos...")
    data = []
    categorias = list(CATEGORIES.keys())
    for i in range(1, n + 1):
        sku = f"SKU-{i:03d}"
        categoria = categorias[(i - 1) % len(categorias)]
        subcategoria = generate_subcategoria(categoria)
        nome_produto = f"{subcategoria} {random.randint(100, 999)}"
        preco_venda = round(random.uniform(30.0, 3000.0), 2)
        preco_custo = round(preco_venda * random.uniform(0.55, 0.80), 2)
        estoque = random.randint(0, 500)
        data.append({
            "sku": sku,
            "nome_produto": nome_produto,
            "categoria": categoria,
            "subcategoria": subcategoria,
            "preco_venda": preco_venda,
            "preco_custo": preco_custo,
            "estoque": estoque,
        })
    return pd.DataFrame(data)


def generate_pedidos(clientes_df, produtos_df, n=8000):
    print(f"Gerando {n} pedidos...")
    cliente_ids = clientes_df["cliente_id"].tolist()
    skus = produtos_df["sku"].tolist()
    estados = list(CITIES_BY_STATE.keys())

    start_date = datetime.date(2025, 1, 1)
    end_date = datetime.date(2026, 6, 9)

    # Power-law: alguns clientes compram mais
    weights = [1.0 / (i ** 0.5) for i in range(1, len(cliente_ids) + 1)]
    total_w = sum(weights)
    probs = [w / total_w for w in weights]

    data = []
    for pedido_id in range(1, n + 1):
        cliente_id = random.choices(cliente_ids, weights=probs, k=1)[0]
        sku = random.choice(skus)
        data_pedido = random_date(start_date, end_date)
        quantidade = random.randint(1, 4)
        valor_frete = round(random.uniform(5.0, 35.0), 2)
        estado = random.choice(estados)
        municipio = random.choice(CITIES_BY_STATE[estado])
        regiao = STATE_TO_REGION[estado]
        id_vendedor = random.choice(SELLER_IDS)
        data.append({
            "pedido_id": pedido_id,
            "cliente_id": cliente_id,
            "sku": sku,
            "data_pedido": data_pedido,
            "quantidade": quantidade,
            "valor_frete": valor_frete,
            "municipio": municipio,
            "estado": estado,
            "regiao": regiao,
            "id_vendedor": id_vendedor,
        })
    return pd.DataFrame(data)


def print_info(df, name):
    print(f"\n--- {name} ---")
    print(f"Linhas: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    print(f"Tipos:\n{df.dtypes}")
    print(f"Primeiras 5 linhas:\n{df.head()}")


def main():
    if check_idempotent():
        return

    print("=" * 60)
    print("  GERACAO DE DADOS SINTETICOS - BI E-COMMERCE")
    print("=" * 60)

    clientes_df = generate_clientes(1500)
    print_info(clientes_df, "CLIENTES")
    clientes_df.to_parquet(clientes_path, engine="pyarrow", index=False)
    print(f"\nSalvo: {clientes_path}")

    produtos_df = generate_produtos(250)
    print_info(produtos_df, "PRODUTOS")
    produtos_df.to_parquet(produtos_path, engine="pyarrow", index=False)
    print(f"\nSalvo: {produtos_path}")

    pedidos_df = generate_pedidos(clientes_df, produtos_df, 8000)
    print_info(pedidos_df, "PEDIDOS")
    pedidos_df.to_parquet(pedidos_path, engine="pyarrow", index=False)
    print(f"\nSalvo: {pedidos_path}")

    print("\n" + "=" * 60)
    print("  GERACAO DE DADOS CONCLUIDA COM SUCESSO!")
    print("=" * 60)


if __name__ == "__main__":
    main()
