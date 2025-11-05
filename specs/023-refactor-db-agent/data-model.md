# Data Model — Refactor agente_banco_dados

## Entities

### ProductSummary
- **Fields**
  - `product_name: str` — nome exibido no relatório.
  - `total_quantity: int` — quantidade total vendida (soma das linhas de vendas).
  - `total_revenue: float` — receita total agregada.
- **Source**: Resultado direto de `query_top_products()` (SQLite).
- **Validation**: Quantidade e receita devem ser não-negativas; dados derivam de consultas SQL com `CHECK` no banco garantindo integridade.

### SellerSummary
- **Fields**
  - `seller_name: str`
  - `region: str` — texto amigável (usa fallback “Sem região”).
  - `total_quantity: int`
  - `total_revenue: float`
- **Source**: Resultado de `query_top_sellers()` com união das tabelas `sales` e `sellers`.
- **Validation**: Mesmos limites de integridade do banco; `region` pode ser string vazia substituída por fallback na consulta.

### SeedCounts
- **Fields**
  - `products: int`
  - `sellers: int`
  - `sales: int`
- **Purpose**: Fornecer resumo pós-seed para logs do CLI e verificações de integridade.
- **Validation**: Deve satisfazer `MIN_SEED_*` definidos em `config.py`; violações levantam `RuntimeError`.

### ReportState (LangGraph)
- **Fields**
  - `top_products: list[ProductSummary]`
  - `top_sellers: list[SellerSummary]`
  - `report_markdown: str`
  - `metadata: dict[str, Any]` — inclui `generated_at` e demais anotações leves.
- **Lifecycle**
  1. Inicialização vazia (`{}`) quando o grafo inicia.
  2. `load_sales_metrics` popula `top_products` e `top_sellers`.
  3. `render_sales_report` gera `report_markdown` e preenche `metadata`.
  4. Resultado final devolvido ao CLI e testado contra baseline.
- **Validation**: Nodes assumem que métricas foram preenchidas anteriormente; falta de métricas deve lançar erro controlado durante desenvolvimento (testes cobrirão o fluxo feliz).
