# Documento de Tarefa: Relatório de Vendas com Insights Gemini

## 1. Análise Atual
### 1.1 Estado Atual
- **Project Structure**: `agente_banco_dados` segue o padrão básico LangGraph (packages `graph.py`, `state.py`, `utils/nodes.py`, `reporting.py`).
- **State Schema**: `ReportState` transporta métricas agregadas (`top_products`, `top_sellers`) e `report_markdown`, sem narrativa adicional.
- **Nodes/Tasks**: Dois nós (`load_sales_metrics`, `render_sales_report`). O segundo apenas concatena markdown estático sem IA.
- **Middleware**: Inexistente; fluxo 100% síncrono.
- **Performance**: Execução rápida (<1s) por tratar apenas agregações locais; não há integração com serviços externos.
- **API**: Graph API declarativa com `StateGraph` compilado em `graph.py`.

### 1.2 Impacto da Mudança
- **Componentes afetados**:
  - `config.py`: ampliar configuração para criação do cliente Gemini com tratamento de credenciais.
  - `utils/nodes.py`: inserir novo nó para gerar narrativa com IA, ajustar fluxo para combinar texto com markdown existente.
  - `reporting.py`: reutilizado como fornecedor das tabelas (sem alterações estruturais, mas retornos serão insumo para prompts).
  - `state.py`: estender contrato para suportar insights gerados e detalhes de execução.
  - Logs/erro: garantir mensagens claras em português conforme spec.
- **Riscos**:
  - Falhas de autenticação na API do Gemini interrompendo a geração.
  - Narrativa desconexa se prompt não enfatizar uso dos números fornecidos.
  - Tempo de execução maior; deve permanecer <30s.

## 2. Requisitos & Objetivos
### 2.1 Objetivo Principal
Modificar o agente para que o relatório final una tabelas de métricas com uma narrativa produzida pela Gemini (`gemini-2.5-flash`), entregando pelo menos três insights acionáveis ligados aos dados do SQLite, com mensagens de erro pedagógicas quando a IA falhar.

### 2.2 Escolha de API
Manter Graph API atual. O fluxo continua linear (carregar métricas → gerar narrativa → compor relatório) e a organização existente facilita adicionar um novo nó sem reescrever a orquestração.

### 2.3 Estrutura do Projeto
Continuar com a estrutura básica. Acrescentar submódulos utilitários conforme necessário (`utils/prompts.py`, `utils/llm.py`) para isolar prompt e criação de LLM, seguindo padrão observado em `agente_simples`.

## 3. Organização de Arquivos
### 3.1 Estrutura Base (após mudanças)
```
agente_banco_dados/
├── config.py
├── graph.py
├── reporting.py
├── state.py
└── utils/
    ├── __init__.py
    ├── llm.py          # Novo: fábrica do LLM Gemini
    ├── nodes.py
    └── prompts.py      # Novo: prompt template da narrativa
```

### 3.2 Padrões de Importação
- `config.py` expõe uma dataclass `AppConfig` semelhante ao `agente_simples.config`.
- `utils/nodes.py` importa funções locais explicitamente (`from agente_banco_dados.utils.llm import create_sales_llm`).
- Evitar imports relativos implícitos.

## 4. Implementação Detalhada

### 4.1 State & Config
1. **Estender `ReportState`** para suportar insights e metadados adicionais.
   ```python
   # agente_banco_dados/state.py
   class InsightSummary(TypedDict):
       """Narrativa gerada pela IA com contexto dos dados."""
       headline: str
       rationale: str
       supporting_metrics: list[str]

   class ReportState(TypedDict, total=False):
       top_products: List[ProductSummary]
       top_sellers: List[SellerSummary]
       insights: List[InsightSummary]        # novo
       report_markdown: str
       metadata: Dict[str, Any]
       llm_latency_seconds: float            # novo
       processed_records: int                # novo
   ```

2. **Transformar `config.py` em fábrica de LLM** (reaproveitar abordagem do `agente_simples`):
   ```python
   # agente_banco_dados/config.py
   import os
   from dataclasses import dataclass
   from typing import Optional
   from dotenv import load_dotenv
   from langchain_google_genai import ChatGoogleGenerativeAI

   load_dotenv()

   class ConfigurationError(RuntimeError):
       ...

   @dataclass
   class AppConfig:
       model_name: str = os.getenv("GEMINI_MODEL", DEFAULT_MODEL_ID)
       temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.25"))
       timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
       locale: str = os.getenv("AGENT_LOCALE", "pt-BR")
       api_key: Optional[str] = os.getenv("GEMINI_API_KEY")

       def create_llm(self) -> ChatGoogleGenerativeAI:
           if not self.api_key:
               raise ConfigurationError(
                   "GEMINI_API_KEY ausente. Configure .env antes de gerar o relatório."
               )
           return ChatGoogleGenerativeAI(
               model=self.model_name,
               temperature=self.temperature,
               api_key=self.api_key,
           )

   config = AppConfig()
   ```

### 4.2 Nodes/Tasks/Middleware
1. **Criar prompt estruturado** em `utils/prompts.py`:
   ```python
   # agente_banco_dados/utils/prompts.py
   from __future__ import annotations
   from textwrap import dedent

   SALES_INSIGHT_SYSTEM = dedent(
       """
       Você é uma analista de vendas experiente. Gere insights acionáveis em português brasileiro.
       Regras:
       - Sempre referencie números exatos das tabelas fornecidas.
       - Produza exatamente três blocos:
         1. Tendências marcantes
         2. Riscos ou quedas de performance
         3. Recomendações acionáveis
       - Para cada bloco, cite o(s) produto(s) ou vendedor(es) relevantes e explique o impacto no negócio.
       - Se os dados estiverem vazios, oriente o usuário a revisar o banco ou executar nova consulta.
       """
   ).strip()

   def build_sales_prompt(products: list[dict], sellers: list[dict]) -> str:
       lines = ["Dados consolidados:"]
       lines.append("Produtos mais vendidos:")
       for item in products:
           lines.append(
               f"- {item['product_name']}: {item['total_quantity']} unidades, "
               f"receita R$ {item['total_revenue']:.2f}"
           )
       lines.append("Vendedores com maior receita:")
       for seller in sellers:
           lines.append(
               f"- {seller['seller_name']} ({seller['region']}): "
               f"{seller['total_quantity']} unidades, receita R$ {seller['total_revenue']:.2f}"
           )
       lines.append("Tarefa: gere os três blocos de insights seguindo as regras.")
       return "\n".join(lines)
   ```

2. **Adicionar fábrica do LLM** em `utils/llm.py` para reutilização e testes:
   ```python
   # agente_banco_dados/utils/llm.py
   from time import perf_counter
   from langchain_core.messages import HumanMessage, SystemMessage
   from agente_banco_dados.config import config, ConfigurationError
   from agente_banco_dados.utils.prompts import SALES_INSIGHT_SYSTEM, build_sales_prompt

   def generate_sales_insights(products, sellers):
       """Invoca o Gemini e retorna texto bruto e metadados."""
       llm = config.create_llm()
       start = perf_counter()
       response = llm.invoke(
           [
               SystemMessage(content=SALES_INSIGHT_SYSTEM),
               HumanMessage(content=build_sales_prompt(products, sellers)),
           ]
       )
       latency = perf_counter() - start
       content = getattr(response, "content", "")
       return content, latency
   ```

3. **Refatorar nós em `utils/nodes.py`**:
   - `load_sales_metrics` passa a calcular `processed_records`.
   - Novo nó `generate_insights_node`.
   - `render_sales_report` combina narrativa + tabelas.

   ```python
   # agente_banco_dados/utils/nodes.py
   from agente_banco_dados.utils.llm import generate_sales_insights

   def load_sales_metrics(_: ReportState) -> Dict[str, object]:
       products_raw = query_top_products()
       sellers_raw = query_top_sellers()
       total_records = len(products_raw) + len(sellers_raw)
       return {
           "top_products": _normalise_products(products_raw),
           "top_sellers": _normalise_sellers(sellers_raw),
           "metadata": {"processed_records": total_records},
       }

   def generate_insights_node(state: ReportState) -> Dict[str, object]:
       products = state["top_products"]
       sellers = state["top_sellers"]
       try:
           text, latency = generate_sales_insights(products, sellers)
           return {
               "insights": [{"headline": "Narrativa gerada", "rationale": text, "supporting_metrics": []}],
               "metadata": {
                   **state.get("metadata", {}),
                   "llm_latency_seconds": latency,
               },
           }
       except ConfigurationError as exc:
           return {
               "report_markdown": (
                   "Não foi possível gerar insights automáticos.\n"
                   f"Motivo: {exc}\n"
                   "Configure a variável GEMINI_API_KEY e tente novamente."
               ),
               "metadata": {**state.get("metadata", {}), "llm_error": str(exc)},
           }
       except Exception as exc:
           return {
               "report_markdown": (
                   "Ocorreu um erro ao acessar o serviço de IA. "
                   "Tente novamente em instantes ou verifique sua conexão."
               ),
               "metadata": {**state.get("metadata", {}), "llm_error": str(exc)},
           }

   def render_sales_report(state: ReportState) -> Dict[str, object]:
       markdown = build_markdown_report(state["top_products"], state["top_sellers"])
       insights_text = state.get("insights", [{}])[0].get("rationale", "").strip()
       combined = "\n\n".join(
           [
               markdown,
               "## Insights gerados pela IA",
               insights_text or "Os dados foram carregados, mas nenhum insight foi produzido desta vez.",
               f"*Gerado em {datetime.now(tz=timezone.utc).isoformat()}*",
           ]
       )
       metadata = {**state.get("metadata", {}), "generated_at": datetime.now(tz=timezone.utc).isoformat()}
       return {"report_markdown": combined, "metadata": metadata}
   ```

### 4.3 Graph Construction
Atualizar `graph.py` para incluir o novo nó entre a carga e a renderização:
```python
# agente_banco_dados/graph.py
from agente_banco_dados.utils import load_sales_metrics, generate_insights_node, render_sales_report

def create_app():
    builder = StateGraph(ReportState)
    builder.add_node("load_sales_metrics", load_sales_metrics)
    builder.add_node("generate_insights", generate_insights_node)
    builder.add_node("render_sales_report", render_sales_report)

    builder.add_edge(START, "load_sales_metrics")
    builder.add_edge("load_sales_metrics", "generate_insights")
    builder.add_edge("generate_insights", "render_sales_report")
    builder.add_edge("render_sales_report", END)
    return builder.compile()
```

## 5. Testing Strategy
### 5.1 Unit Tests
- `tests/test_nodes.py` (criar ou expandir):
  - Mockar `generate_sales_insights` para testar path feliz e paths de erro.
  - Validar que `render_sales_report` inclui seção de insights e timestamp.

  ```python
  def test_generate_insights_success(monkeypatch):
      def fake_generate(products, sellers):
          return "Insight A\nInsight B\nInsight C", 0.42
      monkeypatch.setattr(nodes, "generate_sales_insights", fake_generate)
      state = {"top_products": [...], "top_sellers": [...], "metadata": {}}
      result = nodes.generate_insights_node(state)
      assert "insights" in result
      assert result["metadata"]["llm_latency_seconds"] == 0.42
  ```

### 5.2 Integration Tests
- Adicionar teste que executa `app.invoke({})` com banco seed e valida:
  - Presença da seção `## Insights gerados pela IA`.
  - Para testar sem chamar IA real, usar monkeypatch no `create_llm` retornando stub que devolve resposta fixa.

  ```python
  def test_app_invoke_generates_report(monkeypatch):
      class FakeLLM:
          def invoke(self, messages):
              return type("Resp", (), {"content": "1. Tendência...\n2. Risco...\n3. Ação..."})

      monkeypatch.setattr(config, "create_llm", lambda: FakeLLM())
      result = app.invoke({})
      assert "## Insights gerados pela IA" in result["report_markdown"]
      assert "Tendência" in result["report_markdown"]
  ```

## 6. Deployment & Monitoring
### 6.1 Estrutura Final
- Confirmar que novos módulos (`utils/llm.py`, `utils/prompts.py`) estão incluídos em `__all__` de `utils/__init__.py`.
- Garantir que `langgraph.json` continue apontando para `agente_banco_dados/graph.py:app`.
- Atualizar `.env.example` com `GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_TEMPERATURE`.

### 6.2 Checklist
- [ ] Revisão de código focada em manuseio de credenciais e mensagens de erro.
- [ ] `pytest` com monkeypatch para LLM passando.
- [ ] Tempo de execução medido (<30s) com latência simulada da IA.
- [ ] Mensagens de log informam `processed_records` e `llm_latency_seconds`.
- [ ] Documentação (`README.md` do agente) atualizada com instruções de configuração de IA.
- [ ] Variáveis `.env.example` revisadas e commitadas.
