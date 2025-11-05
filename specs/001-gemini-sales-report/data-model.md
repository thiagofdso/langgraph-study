# Data Model — Relatório de Vendas com Insights Gemini

## Entities

### ProductSummary
- **Fields**
  - `product_name` (str, required): nome exibido no relatório.
  - `total_quantity` (int ≥ 0, required): unidades vendidas agregadas.
  - `total_revenue` (float ≥ 0.0, required): receita total em reais.
- **Derived From**: `sales` + `products` (SQLite).
- **Usage**: alimenta tabelas de produtos e contexto do prompt.

### SellerSummary
- **Fields**
  - `seller_name` (str, required)
  - `region` (str, default `"Sem região"` quando nulo)
  - `total_quantity` (int ≥ 0, required)
  - `total_revenue` (float ≥ 0.0, required)
- **Derived From**: `sales` + `sellers` (SQLite).
- **Usage**: alimenta tabelas de vendedores e prompt da IA.

### InsightSummary (novo)
- **Fields**
  - `headline` (str, required): título curto do insight.
  - `rationale` (str, required): narrativa completa gerada pela IA.
  - `supporting_metrics` (list[str], optional): referências textuais a dados usados.
- **Source**: resposta da Gemini; validado para conter ao menos três blocos/tópicos.
- **Usage**: compõe a seção “Insights gerados pela IA” e fundamenta recomendações.

### ReportMetadata
- **Fields**
  - `generated_at` (ISO 8601 UTC, required após renderização)
  - `processed_records` (int ≥ 0, opcional): contagem de linhas agregadas.
  - `llm_latency_seconds` (float ≥ 0.0, opcional): duração da chamada à IA.
  - `llm_error` (str, opcional): mensagem de erro quando IA falhar.
- **Usage**: auditoria e monitoramento interno, atendimento à FR-007.

## Relationships
- `ReportState.top_products` → coleção de `ProductSummary`.
- `ReportState.top_sellers` → coleção de `SellerSummary`.
- `ReportState.insights` → coleção de `InsightSummary` (pode estar ausente se IA falhar).
- `ReportState.metadata` → `ReportMetadata` parcial, agregando campos durante o fluxo.

## Validation Rules
- `top_products` e `top_sellers` devem existir antes de `generate_insights` executar; se vazios, prompt orienta o modelo a indicar ausência de dados.
- `InsightSummary.rationale` deve produzir pelo menos três parágrafos/blocos identificáveis; validação será coberta em testes verificando termos-chave.
- `metadata.generated_at` sempre preenchido na etapa final (`render_sales_report`).
- Em caso de falha de IA, `report_markdown` inclui mensagem clara e `metadata.llm_error` registra o motivo.
