# 📊 Layout do Dashboard — Power BI

## Tema Padrão

| Propriedade | Valor |
|-------------|-------|
| Modo | Dark |
| Fundo da Página | `#262626` |
| Fundo de Visuais/Cards | `#323130` |
| Cor da Fonte | `#FFFFFF` (branco) |
| Fonte | Segoe UI |
| Tamanho Título | 12pt |
| Tamanho Valor (Cards) | 24pt |
| Tamanho Texto (Tabelas) | 10pt |

---

## PÁGINA 1 — VISÃO EXECUTIVA

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  ╔══════════════════════════╗ ╔══════════════════════════╗ ╔══════════════════════════╗  ╔══════════════════════╗  │
│  ║     FATURAMENTO         ║ ║    TOTAL PEDIDOS         ║ ║    TICKET MÉDIO         ║  ║   TOTAL VENDEDORES   ║  │
│  ║     ────────────        ║ ║    ────────────          ║ ║    ────────────         ║  ║   ────────────────   ║  │
│  ║     R$ XXX.XXX,XX       ║ ║      X.XXX               ║ ║     R$ XXX,XX           ║  ║         15           ║  │
│  ╚══════════════════════════╝ ╚══════════════════════════╝ ╚══════════════════════════╝  ╚══════════════════════╝  │
│  Card | Cor fundo: #323130  Card | Cor fundo: #323130   Card | Cor fundo: #323130     Card | Cor fundo: #323130  │
│  Borda: #1A1A1A, 2px        Borda: #1A1A1A, 2px         Borda: #1A1A1A, 2px           Borda: #1A1A1A, 2px        │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│  FATURAMENTO POR ESTADO                      │  FATURAMENTO POR REGIÃO                      │
│  ───────────────────────                     │  ───────────────────────                     │
│                                              │                                              │
│  SP ████████████████████ R$ XXX.XXX          │  Sudeste    ██████████████ R$ XXX.XXX        │
│  RJ ████████████████ R$ XXX.XXX              │  Sul        ███████████ R$ XXX.XXX           │
│  MG ████████████ R$ XXX.XXX                  │  Nordeste   ████████ R$ XXX.XXX              │
│  RS ████████ R$ XXX.XXX                      │  Centro-O.  ██████ R$ XXX.XXX                │
│  BA ██████ R$ XXX.XXX                        │  Norte      ████ R$ XXX.XXX                  │
│  PR █████ R$ XXX.XXX                         │                                              │
│  ...                                          │                                              │
│                                              │                                              │
│  Visual: Gráfico de Barras Horizontal        │  Visual: Gráfico de Barras Horizontal        │
│  Eixo Y: estado                              │  Eixo Y: regiao                              │
│  Eixo X: Faturamento                         │  Eixo X: Faturamento                         │
│  Ordenação: Decrescente                      │  Ordenação: Decrescente                      │
│  Cor: #4A90D9 (azul)                         │  Cor: #50B86C (verde)                        │
│  Altura: 300px                               │  Altura: 300px                               │
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘

┌────────────────────────────────────────────────┬────────────────────────────────────────────┐
│  TOP 10 MUNICÍPIOS                             │  RANKING DE VENDEDORES                      │
│  ────────────────                              │  ─────────────────────                      │
│                                                │                                            │
│  São Paulo     ████████████ R$ XXX.XXX         │  ┌──────┬────────────────┬────────┬──────┐ │
│  Rio de Janeiro██████████ R$ XXX.XXX           │  │ Rank │ Nome           │ Região │ Fat. │ │
│  Belo Horizonte████████ R$ XXX.XXX             │  ├──────┼────────────────┼────────┼──────┤ │
│  Brasília      ██████ R$ XXX.XXX               │  │  1   │ Vendedor A     │ Sudeste│ R$.. │ │
│  Curitiba      █████ R$ XXX.XXX                │  │  2   │ Vendedor B     │ Sul    │ R$.. │ │
│  Salvador      ████ R$ XXX.XXX                 │  │  3   │ Vendedor C     │ Nordeste│R$..│ │
│  Fortaleza     ████ R$ XXX.XXX                 │  │ ...  │ ...            │ ...    │ ...  │ │
│  Recife        ███ R$ XXX.XXX                  │  │ 15   │ Vendedor O     │ Norte  │ R$.. │ │
│  Manaus        ███ R$ XXX.XXX                  │  └──────┴────────────────┴────────┴──────┘ │
│  Porto Alegre  ██ R$ XXX.XXX                   │                                            │
│                                                │  Visual: Tabela                            │
│  Visual: Gráfico de Barras Horizontal          │  Colunas: Ranking, Nome, Região, Fat.      │
│  Eixo Y: municipio                             │  Ordenação: Faturamento DESC               │
│  Eixo X: Faturamento                           │  Cor cabeçalho: #323130                    │
│  Filtro: Top N = 10 (por Faturamento)          │  Altura: 300px                             │
│  Ordenação: Decrescente                        │                                            │
│  Cor: #E8A838 (laranja)                        │                                            │
│  Altura: 300px                                 │                                            │
└────────────────────────────────────────────────┴────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  EVOLUÇÃO MENSAL DO FATURAMENTO                                                            │
│  ─────────────────────────────                                                            │
│                                                                                            │
│  R$ XXXK ┤                      ╱╲                                                         │
│          │         ╱╲          ╱  ╲        ╱╲                                              │
│  R$ XXXK ┤        ╱  ╲   ╱╲  ╱    ╲  ╱╲  ╱  ╲    ╱╲                                        │
│          │   ╱╲ ╱    ╲ ╱  ╲╱      ╲╱  ╲╱    ╲╲╱  ╲                                       │
│  R$ XXXK ┤  ╱  ╱      ╲╱                      ╲    ╲                                       │
│          │ ╱                                                                               │
│  R$ XXXK ┼────────────────────────────────────────────────────────────                     │
│          Jan  Fev  Mar  Abr  Mai  Jun  Jul  Ago  Set  Out  Nov  Dez                        │
│                                                                                            │
│  Visual: Gráfico de Área                                                                   │
│  Eixo X: nome_mes (ordenado por mes_num)                                                  │
│  Eixo Y: Faturamento                                                                       │
│  Cor da área: #4A90D9 com 40% de transparência                                            │
│  Cor da linha: #4A90D9                                                                     │
│  Altura: 250px | Largura: Full-width                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## PÁGINA 2 — VENDEDORES

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  ╔══════════════════════════════════════════╗ ╔══════════════════════════════════════════╗│
│  ║        MELHOR VENDEDOR                  ║ ║     FATURAMENTO MÉDIO VENDEDOR           ║│
│  ║        ──────────────                   ║ ║     ────────────────────────             ║│
│  ║        [Nome do Top 1]                  ║ ║     R$ XX.XXX,XX                          ║│
│  ║        R$ XX.XXX,XX                     ║ ║                                           ║│
│  ╚══════════════════════════════════════════╝ ╚══════════════════════════════════════════╝│
│  Medida: Melhor Vendedor (TOPN)              Medida: Faturamento Medio Vendedor            │
│  Altura: 120px                               Altura: 120px                                 │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  RANKING COMPLETO DE VENDEDORES                                                            │
│  ─────────────────────────────                                                            │
│                                                                                            │
│  ┌────────┬───────────────────────┬─────────────┬─────────────────┐                       │
│  │ Ranking│ Nome                  │ Região      │ Faturamento     │                       │
│  ├────────┼───────────────────────┼─────────────┼─────────────────┤                       │
│  │   1    │ Vendedor A            │ Sudeste     │ R$ XXX.XXX,XX   │                       │
│  │   2    │ Vendedor B            │ Sul         │ R$ XXX.XXX,XX   │                       │
│  │   3    │ Vendedor C            │ Nordeste    │ R$ XXX.XXX,XX   │                       │
│  │   4    │ Vendedor D            │ Sudeste     │ R$ XXX.XXX,XX   │                       │
│  │   5    │ Vendedor E            │ Centro-Oeste│ R$ XXX.XXX,XX   │                       │
│  │  ...   │ ...                   │ ...         │ ...             │                       │
│  │  15    │ Vendedor O            │ Norte       │ R$ XXX.XXX,XX   │                       │
│  └────────┴───────────────────────┴─────────────┴─────────────────┘                       │
│                                                                                            │
│  Visual: Tabela                                                                            │
│  Colunas: Ranking | Nome | Região | Faturamento                                           │
│  Ordenação: Ranking ASC                                                                    │
│  Total de linhas: 15                                                                       │
│  Altura: 350px | Largura: Full-width                                                       │
│  Cor cabeçalho: #323130                                                                    │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────┬───────────────────────────────────────────────┐
│  PARTICIPAÇÃO % POR VENDEDOR              │  FATURAMENTO POR REGIÃO DO VENDEDOR           │
│  ──────────────────────────              │  ────────────────────────────────────          │
│                                           │                                               │
│           ╭──────────╮                    │  ┌──────────────────────────────────────────┐ │
│         ╭─┤  Vendedor │╮                   │  │ Sudeste  ████████ Vendedor A             │ │
│        │  │    A      │ │                  │  │          ██████ Vendedor B               │ │
│        │  ╰──────────╯ │                  │  │          ████ Vendedor C                 │ │
│        │               │                  │  │ Sul      ████████ Vendedor D             │ │
│        │    Vendedor   │                  │  │          ████ Vendedor E                 │ │
│        │       B       │                  │  │ Nordeste ████████ Vendedor F             │ │
│        │               │                  │  │          ██████ Vendedor G               │ │
│        ╰───────────────╯                  │  │ C.Oeste  ██████ Vendedor H               │ │
│                                           │  │          ████ Vendedor I                 │ │
│  Visual: Gráfico de Rosca (Donut)         │  │ Norte    ████ Vendedor J                 │ │
│  Legenda: dim_vendedores[nome]            │  └──────────────────────────────────────────┘ │
│  Valores: Participacao Vendedor (%)       │                                               │
│  Cor: Paleta variada por vendedor         │  Visual: Barras Empilhadas                    │
│  Altura: 300px                            │  Eixo X: regiao                               │
│                                           │  Legenda: nome (vendedor)                     │
│                                           │  Valores: Faturamento                         │
│                                           │  Altura: 300px                                │
└───────────────────────────────────────────┴───────────────────────────────────────────────┘
```

---

## PÁGINA 3 — GEOGRÁFICA

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  FATURAMENTO POR ESTADO                                                                    │
│  ───────────────────────                                                                  │
│                                                                                            │
│  SP ████████████████████████████████ R$ XXX.XXX,XX                                         │
│  RJ ██████████████████████ R$ XXX.XXX,XX                                                   │
│  MG █████████████████ R$ XXX.XXX,XX                                                        │
│  RS █████████████ R$ XXX.XXX,XX                                                            │
│  BA ██████████ R$ XXX.XXX,XX                                                               │
│  PR █████████ R$ XXX.XXX,XX                                                                │
│  SC ████████ R$ XXX.XXX,XX                                                                 │
│  PE ███████ R$ XXX.XXX,XX                                                                  │
│  CE ██████ R$ XXX.XXX,XX                                                                   │
│  GO █████ R$ XXX.XXX,XX                                                                    │
│  ...                                                                                       │
│                                                                                            │
│  Visual: Gráfico de Barras Horizontal                                                     │
│  Eixo Y: estado                                                                            │
│  Eixo X: Faturamento                                                                       │
│  Ordenação: Decrescente                                                                    │
│  Cor: #4A90D9 (azul)                                                                       │
│  Altura: 300px | Largura: Full-width                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  FATURAMENTO POR REGIÃO                                                                    │
│  ───────────────────────                                                                  │
│                                                                                            │
│  Sudeste      ████████████████████████████████ R$ XXX.XXX,XX                               │
│  Sul          ██████████████████████ R$ XXX.XXX,XX                                         │
│  Nordeste     ████████████████ R$ XXX.XXX,XX                                               │
│  Centro-Oeste ██████████ R$ XXX.XXX,XX                                                     │
│  Norte        ██████ R$ XXX.XXX,XX                                                         │
│                                                                                            │
│  Visual: Gráfico de Barras Horizontal                                                     │
│  Eixo Y: regiao                                                                            │
│  Eixo X: Faturamento                                                                       │
│  Ordenação: Decrescente                                                                    │
│  Cor: #50B86C (verde)                                                                      │
│  Altura: 300px | Largura: Full-width                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  FATURAMENTO POR MUNICÍPIO (TOP 15)                                                        │
│  ─────────────────────────────────                                                        │
│                                                                                            │
│  São Paulo       ██████████████████████ R$ XXX.XXX,XX                                      │
│  Rio de Janeiro  █████████████████ R$ XXX.XXX,XX                                           │
│  Belo Horizonte  █████████████ R$ XXX.XXX,XX                                               │
│  Brasília        ███████████ R$ XXX.XXX,XX                                                 │
│  Curitiba        █████████ R$ XXX.XXX,XX                                                   │
│  Salvador        ████████ R$ XXX.XXX,XX                                                    │
│  Fortaleza       ███████ R$ XXX.XXX,XX                                                     │
│  Recife          ██████ R$ XXX.XXX,XX                                                      │
│  Manaus          ██████ R$ XXX.XXX,XX                                                      │
│  Porto Alegre    █████ R$ XXX.XXX,XX                                                       │
│  Goiânia         █████ R$ XXX.XXX,XX                                                       │
│  Belém           ████ R$ XXX.XXX,XX                                                        │
│  São Luís        ████ R$ XXX.XXX,XX                                                        │
│  Natal           ███ R$ XXX.XXX,XX                                                         │
│  Campo Grande    ███ R$ XXX.XXX,XX                                                         │
│                                                                                            │
│  Visual: Gráfico de Barras Horizontal                                                     │
│  Eixo Y: municipio                                                                         │
│  Eixo X: Faturamento                                                                       │
│  Filtro: Top N = 15 (por Faturamento)                                                      │
│  Ordenação: Decrescente                                                                    │
│  Cor: #E8A838 (laranja)                                                                    │
│  Altura: 300px | Largura: Full-width                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## FILTROS GLOBAIS (Presentes em todas as páginas)

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│  FILTROS                                                                                   │
│  ───────                                                                                   │
│                                                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │    Ano       │  │   Região     │  │   Estado     │  │  Categoria   │                   │
│  │  ──────────  │  │  ──────────  │  │  ──────────  │  │  ──────────  │                   │
│  │  ☐ 2024      │  │  ☐ Todas     │  │  ☐ Todos     │  │  ☐ Todas     │                   │
│  │  ☐ 2025      │  │  ☐ Sudeste   │  │  ☐ SP        │  │  ☐ Smartphone│                   │
│  │              │  │  ☐ Sul       │  │  ☐ RJ        │  │  ☐ Notebook  │                   │
│  │              │  │  ☐ Nordeste  │  │  ☐ MG        │  │  ☐ Tablet    │                   │
│  │              │  │  ☐ C-Oeste   │  │  ☐ ...       │  │  ☐ ...       │                   │
│  │              │  │  ☐ Norte     │  │              │  │              │                   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘                   │
│                                                                                            │
│  Fontes:                                                                                   │
│  - Ano: dim_calendario[ano]                                                                │
│  - Região: dim_clientes[regiao] ou fact_vendas[regiao]                                    │
│  - Estado: dim_clientes[estado] ou fact_vendas[estado]                                    │
│  - Categoria: dim_produtos[categoria]                                                      │
│                                                                                            │
│  Comportamento:                                                                            │
│  - Todos os filtros afetam todas as páginas                                                │
│  - Seleção múltipla com checkbox                                                           │
│  - Filtro em cascata (ex: selecionar região → estados disponíveis)                         │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

## Interações e Cross-Filtering

```
┌──────────────────────────────────────────┐
│  INTERAÇÕES ENTRE VISUAIS                │
│  ────────────────────────                │
│                                          │
│  1. Selecionar barra no gráfico de       │
│     Estado → Filtra demais visuais       │
│     por aquele estado selecionado.       │
│                                          │
│  2. Selecionar vendedor na tabela de     │
│     Ranking → Destaca faturamento        │
│     daquele vendedor em todos visuais.   │
│                                          │
│  3. Selecionar mês no gráfico de         │
│     Evolução → Filtra período nos        │
│     cards e rankings.                    │
│                                          │
│  4. Tooltip ao passar mouse sobre        │
│     barras:                              │
│     • Estado: Faturamento, Pedidos,      │
│       Ticket Médio                       │
│     • Vendedor: Nome, Região,            │
│       Participação %                     │
│                                          │
│  5. Drill-through:                      │
│     Estado → Municípios do estado        │
│     (navegação entre páginas)            │
└──────────────────────────────────────────┘
```
