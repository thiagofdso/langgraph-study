# Contract — agente_banco_dados Execution Interfaces

## CLI Entry Point (`python agente_banco_dados/main.py`)

| Aspect        | Specification                                                                 |
|---------------|-------------------------------------------------------------------------------|
| Arguments     | Nenhum argumento obrigatório; aceita variáveis de ambiente herdadas (.env).   |
| Precondition  | Ambiente virtual ativo; arquivo `.env` opcional com `GEMINI_API_KEY` ignorado.|
| Side effects  | Cria diretório `agente_banco_dados/data/` (se ausente) e popula `sales.db`.    |
| Output (stdout) | Mensagem de prontidão do banco + relatório Markdown contendo as seções:      |
| Exit status   | `0` em sucesso; exceções propagadas caso seed falhe ou consulta levante erro.  |

### Output Envelope
```
Database ready with {products} products, {sellers} sellers, {sales} sales records.
Relatório gerado exclusivamente a partir do banco SQLite local.
# Relatório de Vendas Baseado em SQLite
...
```

## Programmatic Graph (`agente_banco_dados.create_app`)

| Aspect        | Specification                                                                 |
|---------------|-------------------------------------------------------------------------------|
| Signature     | `def create_app() -> CompiledGraph[ReportState]`                              |
| Invocation    | `app = create_app(); result = app.invoke({})`                                 |
| Input State   | Dicionário vazio; o grafo internaliza consultas para preencher o estado.      |
| Output State  | `{"report_markdown": str, "top_products": [...], "top_sellers": [...], "metadata": {...}}` |
| Determinismo  | Saída determinística com base no conteúdo atual de `sales.db`.                |
| Side effects  | Nenhum — assume que o banco já foi inicializado antes da chamada.             |

### LangGraph CLI Registration
```
"graphs": {
  "agente_banco_dados": "agente_banco_dados/graph.py:app"
}
```

Usuários podem executar via:
```bash
langgraph run agente_banco_dados
```
desde que o banco local esteja preparado (rodar CLI previamente ou garantir seed manualmente).
