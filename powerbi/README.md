# Power BI — Dashboard BI E-Commerce (3 Páginas)

## Arquivos de Montagem

| # | Arquivo | Conteúdo |
|---|---------|----------|
| 1 | `dax_medidas_pgs123.txt` | 14 medidas DAX prontas (com prefixo MySQL) |
| 2 | `python_visuals_pg1.txt` | Página 1: Mapa BR + Ranking Vendedores + Top 10 Municípios + Evolução Mensal |
| 3 | `python_visuals_pg2.txt` | Página 2: Donut Participação % + Barras Fat. por Região |
| 4 | `python_visuals_pg3.txt` | Página 3: Barras Fat. por Categoria + Top 10 Produtos |
| 5 | `dashboard_completo.md` | **Guia completo** com layout, cores, campos, posicionamento |
| 6 | `dax_measures_mysql.txt` | Versão anterior (medidas individuais) |
| 7 | `python_maps.txt` | Versão anterior (mapas + barras) |
| 8 | `python_vendedores_maps.txt` | Versão anterior (ranking vendedores) |
| 9 | `python_visuals.txt` | Versão anterior |
| 10 | `model_relationships.txt` | Relacionamentos e cardinalidade |
| 11 | `dashboard_spec.txt` | Especificação detalhada original |

## Como Começar

1. **Conectar ao MySQL:** `localhost:3306` | banco `bi_ecommerce` | root/root
2. **Criar relacionamentos** (ver `model_relationships.txt`)
3. **Criar medidas DAX** (copiar de `dax_medidas_pgs123.txt`)
4. **Montar visuais** seguindo `dashboard_completo.md`

## Tema

| Elemento | Cor |
|---|---|
| Fundo | `#1B1B1B` |
| Cards | `#2D2D2D` |
| Barras/Linhas | `#4A90D9` |
| Texto | `#FFFFFF` |

## Pré-requisitos Python (Power BI)

```bash
pip install matplotlib geopandas seaborn numpy
```
