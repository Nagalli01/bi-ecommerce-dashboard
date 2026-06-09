from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root:root@localhost:3306/bi_ecommerce")

indexes = [
    "CREATE INDEX idx_fact_cliente  ON fact_vendas (id_cliente)",
    "CREATE INDEX idx_fact_produto  ON fact_vendas (id_produto(20))",
    "CREATE INDEX idx_fact_data     ON fact_vendas (data_pedido)",
    "CREATE INDEX idx_fact_vendedor ON fact_vendas (id_vendedor)",
]

with engine.connect() as conn:
    for idx in indexes:
        try:
            conn.execute(text(idx))
            conn.commit()
            print(f"OK: {idx[:60]}...")
        except Exception as e:
            print(f"SKIP (ja existe): {idx[:60]}...")

    result = conn.execute(text(
        "SELECT TABLE_NAME, TABLE_ROWS "
        "FROM information_schema.tables "
        "WHERE table_schema = 'bi_ecommerce' "
        "ORDER BY TABLE_NAME"
    ))
    print()
    for row in result:
        print(f"  {row[0]:25s} {row[1]} linhas")

engine.dispose()
print("\nBanco MySQL pronto para Power BI!")
