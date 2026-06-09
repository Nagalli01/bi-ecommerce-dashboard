# GUIA COMPLETO — DASHBOARD BI E-COMMERCE (3 PÁGINAS)

## Conexão MySQL → Power BI

1. **Obter Dados** → **Banco de Dados MySQL**
2. Servidor: `localhost:3306` | Banco: `bi_ecommerce`
3. Aba lateral: clique em **"Banco de dados"** (não "Windows")
4. Usuário: `root` | Senha: `root`
5. Selecione as 5 tabelas e clique **Carregar**

## Relacionamentos (Aba Modelo)

| De (Dimensão) | Campo | Para (Fato) | Campo | Card. |
|---|---|---|---|---|
| `bi_ecommerce dim_clientes` | id_cliente | `bi_ecommerce fact_vendas` | id_cliente | 1:* |
| `bi_ecommerce dim_produtos` | id_produto | `bi_ecommerce fact_vendas` | id_produto | 1:* |
| `bi_ecommerce dim_calendario` | data | `bi_ecommerce fact_vendas` | data_pedido | 1:* |
| `bi_ecommerce dim_vendedores` | id_vendedor | `bi_ecommerce fact_vendas` | id_vendedor | 1:* |

> Marque `dim_calendario` como **Tabela de Data** na coluna `data`.

## Tema Dark

| Elemento | Cor |
|---|---|
| Fundo da página | `#1B1B1B` |
| Fundo dos visuais | `#2D2D2D` |
| Barras/Linhas | `#4A90D9` |
| Texto | `#FFFFFF` |
| Fonte | Segoe UI |

## Medidas DAX

Copie do arquivo `powerbi/dax_medidas_pgs123.txt` — são 14 medidas.
Botão direito em `fact_vendas` → **Nova Medida** → cole uma a uma.

---

# PÁGINA 1 — VISÃO EXECUTIVA

## LINHA 0 — KPI Cards (visuais nativos do Power BI)

| Posição | Card | Medida | Formato |
|---|---|---|---|
| Canto esquerdo | Faturamento | `Faturamento` | R$ (moeda) |
| | Total Pedidos | `Total Pedidos` | Número inteiro |
| | Ticket Médio | `Ticket Medio` | R$ (moeda) |
| Canto direito | Total Vendedores | `Total Vendedores` | Número inteiro |

**Configuração de cada card:**
- Fundo: `#2D2D2D` | Borda: `#1A1A1A` 2px | Cantos: 8px
- Valor: 24pt, cor `#FFFFFF`, bold
- Rótulo: 10pt, cor `#AAAAAA`

## LINHA 1 — Mapa + Ranking (lado a lado)

### Esquerda: Mapa Faturamento por Estado (Visual Python)

**Campos:** arraste `estado` e `total_pedido` da `fact_vendas` para Valores

**Código:** copie o `VISUAL 1.1` de `powerbi/python_visuals_pg1.txt`

### Direita: Ranking de Vendedores (Visual Python)

**Campos:** arraste `nome` da `dim_vendedores` e `total_pedido` da `fact_vendas`

**Código:** copie o `VISUAL 1.2` de `powerbi/python_visuals_pg1.txt`

> Este visual é **fino** — estique na horizontal para caber perfeitamente.

## LINHA 2 — Detalhamento

### Esquerda: Top 10 Municípios (Visual Python)

**Campos:** arraste `municipio` e `total_pedido` da `fact_vendas`

**Código:** copie o `VISUAL 1.3` de `powerbi/python_visuals_pg1.txt`

### Direita: Evolução Mensal (Visual Python)

**Campos:** arraste `mes_num`, `nome_mes` da `dim_calendario` e `total_pedido` da `fact_vendas`

**Código:** copie o `VISUAL 1.4` de `powerbi/python_visuals_pg1.txt`

---

# PÁGINA 2 — VENDEDORES

## LINHA 0 — KPI Cards

| Posição | Card | Medida | Formato |
|---|---|---|---|
| Esquerda | Melhor Vendedor | `Melhor Vendedor` | Texto |
| Direita | Fat. Médio/Vendedor | `Faturamento Medio Vendedor` | R$ |

## LINHA 1

### Esquerda: Participação % (Visual Python — Donut)

**Campos:** arraste `nome` da `dim_vendedores` e `total_pedido` da `fact_vendas`

**Código:** copie o `VISUAL 2.1` de `powerbi/python_visuals_pg2.txt`

### Direita: Faturamento por Região (Visual Python)

**Campos:** arraste `regiao` da `dim_vendedores` e `total_pedido` da `fact_vendas`

**Código:** copie o `VISUAL 2.2` de `powerbi/python_visuals_pg2.txt`

## LINHA 2 — Tabela de Vendedores (Visual Nativo Power BI)

**Campos:** `Ranking Vendedor`, `nome`, `regiao`, `Faturamento`

**Formatação:**
- Fundo: `#2D2D2D` | Cabeçalho: `#2D2D2D`
- Texto cabeçalho: `#FFFFFF` bold 10pt
- Texto corpo: `#AAAAAA` 9pt
- Ordenar por: `Ranking Vendedor` ASC
- Faturamento formatado como R$

---

# PÁGINA 3 — PRODUTOS & CATEGORIAS

## LINHA 0 — KPI Cards

| Posição | Card | Medida | Formato |
|---|---|---|---|
| | Total Categorias | `Total Categorias` | Número inteiro |
| | Preço Médio | `Preco Medio` | R$ |
| Canto direito | Ticket Médio/Categoria | `Ticket Medio Categoria` | R$ |

## LINHA 1

### Esquerda: Faturamento por Categoria (Visual Python)

**Campos:** arraste `categoria` da `dim_produtos` e `total_pedido` da `fact_vendas`

**Código:** copie o `VISUAL 3.1` de `powerbi/python_visuals_pg3.txt`

### Direita: Top 10 Produtos (Visual Python)

**Campos:** arraste `nome_produto` da `dim_produtos` e `total_pedido` da `fact_vendas`

**Código:** copie o `VISUAL 3.2` de `powerbi/python_visuals_pg3.txt`

---

# ARQUIVOS DE REFERÊNCIA

| Arquivo | Uso |
|---|---|
| `dax_medidas_pgs123.txt` | Todas as 14 medidas DAX prontas |
| `python_visuals_pg1.txt` | 4 scripts Python da Página 1 |
| `python_visuals_pg2.txt` | 2 scripts Python da Página 2 |
| `python_visuals_pg3.txt` | 2 scripts Python da Página 3 |

# DICAS

- **Visual fino não renderiza?** Clique no visual Python, vá em Formatar → Geral → ajuste Altura/Largura ou redimensione com o mouse.
- **Erro de coluna?** O código mostra a lista de colunas disponíveis. Confira se arrastou os campos certos.
- **Mapa não aparece?** Confirme que o arquivo `data/brazil_states.geojson` existe.
- **Fonte Segoe UI não aparece?** É a fonte padrão do Windows. Se falhar, use `sans-serif`.
