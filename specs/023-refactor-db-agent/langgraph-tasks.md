# LangGraph Task Plan — Refatorar `agente_banco_dados`

## Contexto Atual
- O agente depende de `main.py` como ponto único: inicializa o banco SQLite, coleta métricas com `reporting.py` e imprime o relatório Markdown diretamente.
- Não existe função `create_app()` compatível com LangGraph CLI, nem separação clara de estado, nodes ou CLI como em `agente_simples`.
- `config.py`, `db_init.py` e `reporting.py` concentram lógica reutilizável, mas estão acoplados ao fluxo procedimental atual.
- Arquitetura-alvo: espelhar `agente_simples` (módulos dedicados para estado, grafo, CLI, utils) mantendo funcionalidade idêntica.

## Objetivos de Refatoração
- Introduzir organização modular (state/graph/utils/cli) sem alterar o relatório gerado ou a inicialização do banco.
- Expor `create_app()` e `app` prontos para LangGraph CLI, preservando o caminho legacy (`python agente_banco_dados/main.py`).
- Reaproveitar lógica existente de banco e relatórios, apenas redistribuindo responsabilidades.
- Manter cobertura de testes atual e adicionar casos específicos para o novo fluxo, se necessário.
- Atualizar documentação e catálogo de nomes de nodes para refletir o novo desenho.

## Tarefas Planejadas

### 1. Congelar comportamento atual e artefatos (Baseline)
- Rodar o fluxo vigente (`python agente_banco_dados/main.py`) para capturar saída e garantir que o relatório atual sirva como regressão.
- Persistir amostra do relatório e contagens de seed para comparação posterior.
- Registrar instruções de execução no plano de QA.

```bash
python agente_banco_dados/main.py > /tmp/relatorio_atual.md
head -n 10 /tmp/relatorio_atual.md
```

### 2. Padronizar camada de dados (`db_init`) e contratos de retorno
- Revisar `db_init.py` para garantir funções idempotentes e preparar retornos tipados que serão consumidos pelos novos nodes.
- Introduzir `TypedDict` para os resumos de seed, mantendo assinaturas públicas.

```python
# agente_banco_dados/database.py
class SeedCounts(TypedDict):
    products: int
    sellers: int
    sales: int

def initialize_database() -> SeedCounts:
    with get_connection() as connection:
        apply_schema(connection)
        seed_products(connection)
        seed_sellers(connection)
        seed_sales(connection)
        connection.commit()
        return get_row_counts(connection)
```

### 3. Criar contrato de estado dedicado (`state.py`)
- Mapear campos utilizados pelo fluxo (métricas, relatório Markdown, metadata de execução).
- Expor `ReportState` e estruturas auxiliares (`ProductSummary`, `SellerSummary`) alinhadas ao padrão do projeto.

```python
# agente_banco_dados/state.py
class ProductSummary(TypedDict):
    product_name: str
    total_quantity: int
    total_revenue: float

class SellerSummary(TypedDict):
    seller_name: str
    region: str
    total_quantity: int
    total_revenue: float

class ReportState(TypedDict, total=False):
    top_products: list[ProductSummary]
    top_sellers: list[SellerSummary]
    report_markdown: str
    metadata: dict[str, Any]
```

### 4. Encapsular lógica de consulta e renderização em nodes reutilizáveis
- Criar `agente_banco_dados/utils/nodes.py` (espelhando `agente_simples`) com duas funções puras: coleta de métricas e renderização Markdown.
- Cada node deve retornar apenas o delta de estado, sem efeitos colaterais.

```python
# agente_banco_dados/utils/nodes.py
def load_sales_metrics(_: ReportState) -> dict[str, object]:
    return {
        "top_products": query_top_products(),
        "top_sellers": query_top_sellers(),
    }

def render_sales_report(state: ReportState) -> dict[str, object]:
    report_md = build_markdown_report(
        state["top_products"],
        state["top_sellers"],
    )
    return {
        "report_markdown": report_md,
        "metadata": {"generated_at": datetime.now().isoformat()},
    }
```

### 5. Construir módulo do grafo com `create_app()`
- Adicionar `agente_banco_dados/graph.py` definindo `create_app()` e `app` (instância compilada) análogos a `agente_simples/graph.py`.
- Usar nomes de nodes alinhados ao catálogo e à nova estrutura.

```python
# agente_banco_dados/graph.py
from langgraph.graph import StateGraph, START, END

def create_app():
    builder = StateGraph(ReportState)
    builder.add_node("load_sales_metrics", load_sales_metrics)
    builder.add_node("render_sales_report", render_sales_report)
    builder.add_edge(START, "load_sales_metrics")
    builder.add_edge("load_sales_metrics", "render_sales_report")
    builder.add_edge("render_sales_report", END)
    return builder.compile()

app = create_app()
```

### 6. Reestruturar CLI e ponto de entrada
- Criar `agente_banco_dados/cli.py` para executar preflight (inicialização do banco) e acionar o grafo compilado.
- Ajustar `main.py` para delegar ao CLI (sem alterar a experiência do usuário).

```python
# agente_banco_dados/cli.py
def main() -> None:
    counts = initialize_database()
    print(
        "Database ready with "
        f"{counts['products']} products, "
        f"{counts['sellers']} sellers, "
        f"{counts['sales']} sales records."
    )
    result = app.invoke({})
    print(result["report_markdown"])

# agente_banco_dados/main.py
from agente_banco_dados.cli import main

if __name__ == "__main__":
    main()
```

### 7. Atualizar exports e integração com LangGraph CLI
- Expor `create_app` e `app` em `agente_banco_dados/__init__.py`.
- Adicionar (ou atualizar) `langgraph.json` do agente para apontar `agente_banco_dados/graph.py:app`.

```python
# agente_banco_dados/__init__.py
from .graph import app, create_app

__all__ = ["app", "create_app"]
```

```json
{
  "dependencies": ["."],
  "graphs": {
    "agente_banco_dados": "agente_banco_dados/graph.py:app"
  },
  "env": "agente_banco_dados/.env"
}
```

### 8. Garantir cobertura de testes e fixtures
- Criar teste dedicado (ex.: `tests/test_agente_banco_dados.py`) validando `create_app()` e o relatório gerado.
- Reutilizar o banco seed (ou fixtures temporárias) para comparar resultados com baseline.

```python
# tests/test_agente_banco_dados.py
from agente_banco_dados import create_app
from agente_banco_dados.database import initialize_database

def test_report_generation_matches_baseline(tmp_path):
    initialize_database()
    app = create_app()
    result = app.invoke({})
    assert "# Relatório de Vendas" in result["report_markdown"]
    assert "Produtos mais vendidos" in result["report_markdown"]
```

### 9. Revisar documentação e instruções operacionais
- Atualizar `agente_banco_dados/README.md` com novo fluxo (CLI, LangGraph CLI, módulos).
- Documentar como importar `create_app()` para integrações programáticas.

Exemplo de atualização no README:

```markdown
### Executando com LangGraph CLI
langgraph run agente_banco_dados -- --print-report
```

```python
from agente_banco_dados import create_app

app = create_app()
markdown = app.invoke({})["report_markdown"]
```

### 10. Sincronizar catálogo de nomes de nodes
- Acrescentar entradas correspondentes aos novos nodes em `graph-nodes-patterns.md`, garantindo consistência com outros agentes.

```markdown
| `load_sales_metrics` | Consulta produtos e vendedores no SQLite antes da renderização. | `agente_banco_dados/utils/nodes.py#L1-L12` |
| `render_sales_report` | Converte métricas em Markdown final, adicionando metadata gerada. | `agente_banco_dados/utils/nodes.py#L15-L27` |
```

### 11. Validar regressão e checklist final
- Executar testes automatizados e o script manual para confirmar que o relatório permanece idêntico ao baseline salvo na Tarefa 1.
- Revisar checklist de spec e atualizar notas com qualquer desvio observado.

```bash
pytest tests/test_agente_banco_dados.py
python agente_banco_dados/main.py > /tmp/relatorio_refatorado.md
diff -u /tmp/relatorio_atual.md /tmp/relatorio_refatorado.md
```

---

**Observação**: Todas as tarefas acima representam planejamento. Nenhum arquivo deve ser modificado antes da execução efetiva das tarefas listadas.
