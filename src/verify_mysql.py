from sqlalchemy import create_engine, text

engine = create_engine("mysql+pymysql://root:root@localhost:3306/bi_ecommerce")

with engine.connect() as conn:
    for table in ["dim_clientes", "dim_produtos", "dim_calendario", "dim_vendedores", "fact_vendas"]:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
        count = result.scalar()
        print(f"  {table:25s} {count:,} linhas")

    result = conn.execute(text("SELECT SUM(total_pedido) FROM fact_vendas"))
    revenue = result.scalar()
    print(f"\n  Faturamento total: R$ {revenue:,.2f}")

    result = conn.execute(text("SELECT COUNT(DISTINCT pedido_id) FROM fact_vendas"))
    orders = result.scalar()
    print(f"  Total pedidos: {orders:,}")

engine.dispose()
