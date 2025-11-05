# Contract — Sales Report Generation CLI

## Overview
The CLI command `python -m agente_banco_dados.cli` produces a Markdown report combining deterministic tables and AI-generated insights. This contract documents the expected structure for downstream consumers (automation, QA scripts).

## Input Contract
| Parameter | Type | Source | Notes |
|-----------|------|--------|-------|
| `--` (no args) | n/a | CLI | The command takes no parameters; it relies on environment variables and bundled SQLite data. |

Environment variables:
- `GEMINI_API_KEY` (string, required) — API key for Gemini.
- `GEMINI_MODEL` (string, optional, default `gemini-2.5-flash`).
- `GEMINI_TEMPERATURE` (float between 0 and 1, optional, default `0.25`).

## Output Contract
- **STDOUT** lines emitted in ordem:
  1. `Database ready with {products} products, {sellers} sellers, {sales} sales records.`
  2. `Relatório gerado exclusivamente a partir do banco SQLite local.`
  3. Markdown report (multi-line) whose structure is:

```markdown
# Relatório de Vendas Baseado em SQLite
*Fonte: banco de dados local agente_banco_dados/data/sales.db*

## Produtos mais vendidos
| Produto | Quantidade | Receita |
| ------- | ---------- | ------- |
| ...     | ...        | ...     |

## Melhores vendedores
| Vendedor | Região | Quantidade | Receita |
| -------- | ------ | ---------- | ------- |
| ...      | ...    | ...        | ...     |

## Insights gerados pela IA
1. Tendências marcantes: ...
2. Riscos ou quedas de performance: ...
3. Recomendações acionáveis: ...

*Gerado em 2025-11-05T14:23:11.123456+00:00*
```

- The insights section MUST contain three numbered or clearly separated blocks referencing numeric values from the tables.
- When the LLM fails:
  - Replace the insights section with an explanatory message per FR-006.
  - Append guidance for reconfiguring credentials or retrying later.

## Metadata Exchange
- The LangGraph state returned by `app.invoke({})` MUST include:
  - `metadata.processed_records` — total rows aggregated.
  - `metadata.llm_latency_seconds` when the Gemini call succeeds.
  - `metadata.llm_error` when failure occurs.
  - `metadata.generated_at` as ISO-8601 UTC timestamp.

## Error Handling
- Missing `GEMINI_API_KEY` ⇒ CLI prints error message in place of insights and exits with report explaining the missing key.
- Timeout or provider failure ⇒ CLI prints user-facing guidance and the state contains `llm_error` with the provider message.

## Acceptance Notes
- QA scripts should parse the Markdown to verify:
  - At least 3 insights lines present when LLM succeeds.
  - All currency values maintain format `R$ {value}` with comma decimal separator in tables.
  - `generated_at` timestamp exists regardless of LLM success.
