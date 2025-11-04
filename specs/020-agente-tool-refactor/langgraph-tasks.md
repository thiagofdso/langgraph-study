# Plano de Refatoração – `agente_tool`

## Contexto e Objetivos
- O projeto `agente_tool` está concentrado em `main.py`, mistura definição de estado, configuração de modelo, ferramentas e grafo em um único arquivo, dificultando manutenção, testes e reutilização.
- Desejamos alinhar sua estrutura às boas práticas observadas em `agente_simples` e `agente_memoria`, incluindo separação de responsabilidades (`state.py`, `config.py`, `utils/nodes.py`, `utils/tools.py`, `graph.py`, `cli.py`), documentação, testes e governança.
- O fluxo precisa seguir os padrões de nós definidos em `graph-nodes-patterns.md`, além de introduzir novas nomenclaturas necessárias para agentes com ferramentas e atualizar o catálogo compartilhado.

## Convenções Obrigatórias
- Respeitar os princípios XXII e XXIII do Constitution: atualizações incrementais no `langgraph.json` e consulta/atualização do catálogo `graph-nodes-patterns.md`.
- Reutilizar nomenclaturas já existentes para funcionalidades equivalentes (`validate_input`, `invoke_model`, `format_response`) e documentar novas responsabilidades de nós e ferramentas.
- Manter docstrings em todas as funções exportadas e cobrir comportamentos determinísticos com testes.

---

## Fase 0 – Descoberta e Baseline
- [ ] **T000 | Auditoria funcional atual**
  - Executar `python agente_tool/main.py` para registrar comportamento atual, mensagens e chamadas ao `calculator`.
  - Anotar dependências implícitas (uso direto de `GEMINI_API_KEY`, ausência de checkpointer, ausência de logging).
  - Guardar transcript em `agente_tool/docs/baseline.md` com o formato:
    ```markdown
    ## Execução 2025-11-04
    - Entrada: "quanto é 300 dividido por 4?"
    - Saída: "75"
    - Observações: sem validação de input, resultado correto, sem logs.
    ```

---

## Fase 1 – Estrutura e Configuração
- [ ] **T010 | Criar esqueleto de pacote alinhado aos agentes de referência**
  - Seguir estrutura:
    ```
    agente_tool/
      __init__.py
      graph.py
      state.py
      config.py
      cli.py
      utils/
        __init__.py
        nodes.py
        tools.py
        logging.py (opcional se houver lógica extra)
      docs/
        baseline.md
    ```
  - Garantir que `__init__.py` exporte funções relevantes (`create_app`).

- [ ] **T011 | Configuração centralizada (`config.py`)**
  - Inspirar-se em `agente_memoria/config.py` para criar `AppConfig` com criação de LLM e checkpointer.
  - Exemplo esperado:
    ```python
    from dataclasses import dataclass
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_google_genai import ChatGoogleGenerativeAI

    @dataclass
    class AppConfig:
        model_name: str = "gemini-2.5-flash"
        temperature: float = 0.0

        def create_llm(self):
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
            )

        def create_checkpointer(self):
            return MemorySaver()

    config = AppConfig()
    ```
  - Carregar `.env` via `python-dotenv` apenas dentro da função de fábrica para evitar efeitos colaterais em import.
  - Incluir teste rápido em docstring explicando uso.

- [ ] **T012 | Estado tipado (`state.py`)**
  - Reutilizar padrão de TypedDict com reducer para mensagens, conforme `agente_simples/state.py`.
  - Acrescentar campos para metadados de rota de ferramentas (`selected_tools`, `tool_plans`, `status`).
  - Modelo sugerido:
    ```python
    class GraphState(TypedDict, total=False):
        messages: Annotated[list[BaseMessage], add_messages]
        metadata: dict[str, Any]
        status: str
        resposta: str
        selected_tools: list[str]
        tool_call: dict[str, Any]
    ```
  - Criar `ThreadConfig` mínimo com `thread_id` validado (reuso de `agente_memoria`).

- [ ] **T013 | Arquivos de ambiente e dependências**
  - Criar `agente_tool/.env.example` com placeholders `GEMINI_API_KEY` e comentários curtos.
  - Revisar `requirements.txt` da raiz para incluir dependências requeridas (`python-dotenv` caso não exista).
  - Atualizar `README.md` do agente com instruções de novo comando CLI (ver Fase 4).

---

## Fase 2 – Nodes, Tools e Catálogo de Padrões
- [ ] **T020 | Extrair ferramentas para `utils/tools.py`**
  - Mover o decorator `@tool` `calculator` para arquivo próprio com validação de entrada segura (evitar `eval` direto).
  - Exemplo de implementação com `ast.literal_eval`:
    ```python
    import ast
    from langchain_core.tools import tool

    @tool
    def calculator(expression: str) -> str:
        """Avalia expressões matemáticas simples com segurança."""
        try:
            parsed = ast.parse(expression, mode="eval")
            result = eval(compile(parsed, filename="<calculator>", mode="eval"), {"__builtins__": {}})
            return str(result)
        except Exception as exc:
            return f"Error: {exc}"
    ```
  - Adicionar docstring explicando limitações e casos de erro.

- [ ] **T021 | Criar nodes em `utils/nodes.py` seguindo padrões**
  - Reutilizar nomes existentes do catálogo:
    - `validate_input` – validar pergunta e anexar metadata (`graph-nodes-patterns.md`).
    - `invoke_model` – chamar LLM, passando metadata e mensagens.
    - `format_response` – formatar resposta final e setar status.
  - Introduzir novos nodes específicos para fluxo com ferramentas:
    - `plan_tool_usage` – analisar mensagem e decidir se a ferramenta deve ser chamada (retorna lista `tool_plans`).
    - `execute_tools` – encaminhar para `ToolNode` quando apropriado e registrar resultado da ferramenta em `metadata`.
  - Cada função deve possuir docstring clara e logging (usar `get_logger` inspirado nos outros agentes).
  - Exemplo de docstring e retorno:
    ```python
    def plan_tool_usage(state: GraphState) -> dict[str, Any]:
        """Decide se a próxima etapa requer execução de ferramentas."""
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", None)
        if tool_calls:
            return {
                "status": DEFAULT_STATUS_VALIDATED,
                "tool_plans": [
                    {"name": tool_calls[0]["name"], "args": tool_calls[0]["args"]}
                ],
            }
        return {"tool_plans": []}
    ```

- [ ] **T022 | Atualizar `graph-nodes-patterns.md` com novos padrões**
  - Acrescentar linhas para `plan_tool_usage` e `execute_tools`, incluindo explicações, caminhos e referência cruzada para este projeto.
  - Garantir que a tabela de “Padrões Compartilhados” continue válida; se for necessário, criar subseção “Padrões de Ferramentas”.

- [ ] **T023 | Exportar utilitários em `utils/__init__.py`**
  - Expor `get_logger`, `calculator_tool`, `validate_input`, `plan_tool_usage`, `execute_tools`, `invoke_model`, `format_response`.
  - Docstring curta explicando o propósito do pacote utilitário.

---

## Fase 3 – Construção do Graph e Registro
- [ ] **T030 | `graph.py` com fábrica de app**
  - Criar função `create_app(checkpointer=None)` replicando padrão dos outros agentes:
    ```python
    from langgraph.graph import StateGraph, START, END
    from agente_tool.state import GraphState
    from agente_tool.utils import (
        calculator_tool,
        execute_tools_node,
        format_response_node,
        invoke_model_node,
        plan_tool_usage_node,
        validate_question_node,
    )

    def create_app(checkpointer=None):
        builder = StateGraph(GraphState)
        builder.add_node("validate_input", validate_question_node)
        builder.add_node("plan_tool_usage", plan_tool_usage_node)
        builder.add_node("invoke_model", invoke_model_node)
        builder.add_node("execute_tools", execute_tools_node)
        builder.add_node("format_response", format_response_node)

        builder.add_edge(START, "validate_input")
        builder.add_edge("validate_input", "plan_tool_usage")
        builder.add_conditional_edges(
            "plan_tool_usage",
            decide_next_step,  # função utilitária que decide se chama ferramenta ou LLM
            {
                "invoke_model": "invoke_model",
                "execute_tools": "execute_tools",
            },
        )
        builder.add_edge("execute_tools", "invoke_model")
        builder.add_edge("invoke_model", "format_response")
        builder.add_edge("format_response", END)

        if checkpointer is None:
            checkpointer = config.create_checkpointer()
        return builder.compile(checkpointer=checkpointer)
    ```
  - Implementar `decide_next_step` no mesmo módulo ou em `utils/nodes.py`, com nomenclatura alinhada (ex.: `route_tool_usage`).
  - Ajustar import para `calculator_tool` proveniente de `utils/tools.py`.

- [ ] **T031 | Registrar agente no `langgraph.json` de forma incremental**
  - Acrescentar entrada `"agente-tool": "agente_tool/graph.py:create_app"` mantendo as existentes.
  - Executar `langgraph dev --config langgraph.json` para validar que todos os agentes compilam (opcional mas recomendado registrar no `docs/baseline.md`).

- [ ] **T032 | CLI e ponto de entrada**
  - Criar `agente_tool/cli.py` com comando `run` semelhante a `agente_simples/cli.py`, usando `Typer` ou `argparse`.
  - Atualizar `main.py` para servir apenas como script fino que chama `cli.run()` ou remover caso CLI substitua.
  - Exemplo:
    ```python
    def run(question: str):
        app = create_app()
        config = {"configurable": {"thread_id": f"calculator-{uuid4()}"}}
        result = app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
        print(result["resposta"])
    ```
  - Atualizar `__main__.py` se necessário para suportar `python -m agente_tool`.

---

## Fase 4 – Logging, Observabilidade e Segurança
- [ ] **T040 | Logging consistente**
  - Criar `utils/logging.py` ou reutilizar padrão de `agente_simples` para configurar logger com prefixo do módulo.
  - Inserir logs de nível `info`/`debug` nos nodes (`validate_input`, `plan_tool_usage`, `execute_tools`, `invoke_model`, `format_response`).

- [ ] **T041 | Sanitização e validação de entradas**
  - Garantir que `validate_input` retorne erro amigável se expressão estiver vazia ou ambígua.
  - Exemplo de retorno:
    ```python
    if not question or len(question.strip()) < 5:
        return {
            "status": DEFAULT_STATUS_ERROR,
            "resposta": "Forneça uma pergunta mais detalhada para usar o agente calculadora.",
        }
    ```
  - Atualizar `plan_tool_usage` para validar dados de `tool_calls`.

- [ ] **T042 | Proteção contra `eval` inseguro**
  - Já prevista em T020, validar se `calculator` não expõe builtins perigosos. Adicionar testes cobrindo casos maliciosos (`__import__("os").system("rm -rf /")` deve resultar em erro controlado).

---

## Fase 5 – Testes
- [ ] **T050 | Testes unitários de nodes (`tests/test_nodes.py`)**
  - Casos mínimos:
    - `validate_input` aceita pergunta válida e rejeita string curta.
    - `plan_tool_usage` retorna plano quando `tool_calls` existe e `None` caso contrário.
    - `invoke_model` mocka LLM retornando `AIMessage`.
    - `execute_tools` retorna mensagens contendo saída do `calculator`.
  - Usar `pytest` e fixtures semelhantes aos agentes de referência.

- [ ] **T051 | Teste de integração do grafo (`tests/test_graph.py`)**
  - Simular fluxo completo com checkpointer em memória.
  - Exemplo:
    ```python
    def test_graph_invokes_calculator(monkeypatch):
        app = create_app(checkpointer=MemorySaver())
        config = {"configurable": {"thread_id": "test-1"}}
        state = {"messages": [HumanMessage(content="Use a calculadora: 2+2")]}
        result = app.invoke(state, config=config)
        assert result["resposta"].startswith("Resposta do agente:")
        assert "4" in result["resposta"]
    ```

- [ ] **T052 | Testes de segurança da ferramenta**
  - Cobrir expressões inválidas e maliciosas garantindo resposta `"Error:"`.
  - Adicionar teste para grandes números ou operações complexas (ex.: `"(2+3)*4"`).

---

## Fase 6 – Documentação e Governança
- [ ] **T060 | Atualizar README e quickstart**
  - Incluir instruções de CLI (`python -m agente_tool run "2+2"`), dependências e arquitetura do projeto.
  - Acrescentar seção sobre como adicionar novas ferramentas seguindo os padrões estabelecidos.

- [ ] **T061 | Documentação interna**
  - Em `agente_tool/docs/architecture.md`, descrever fluxo dos nodes, incluindo diagrama simples (pode ser em texto).
  - Exemplo:
    ```markdown
    START → validate_input → plan_tool_usage
      ↳ (sem ferramenta) invoke_model → format_response → END
      ↳ (com ferramenta) execute_tools → invoke_model → format_response → END
    ```

- [ ] **T062 | Governança**
  - Se novos padrões de nodes forem adicionados, garantir que `graph-nodes-patterns.md` registre os nomes e responsabilidades.
  - Atualizar `PROJETOS.md` descrevendo a refatoração (caso documento seja usado para catálogo).
  - Registrar no `Sync Impact Report` da constituição se houver necessidade futura (não obrigatório agora, mas deixar anotado).

---

## Fase 7 – Verificação Final
- [ ] **T070 | Checklist de conformidade**
  - Executar `pytest` e `ruff check .` na raiz.
  - Rodar `langgraph dev --config langgraph.json` para assegurar que todos os agentes compilam e aparecem no dashboard.
  - Validar que `python -m agente_tool --help` mostra comandos esperados.

- [ ] **T071 | Captura de evidências**
  - Atualizar `agente_tool/docs/baseline.md` com nova execução pós-refatoração (mesmo formato da Fase 0).
  - Documentar eventuais TODOs ou decisões pós-implementação.

---

## Referências Cruzadas
- `agente_simples/graph.py`, `agente_simples/utils/nodes.py`, `agente_simples/config.py` – base para estrutura modular e logging.
- `agente_memoria/graph.py`, `agente_memoria/state.py`, `agente_memoria/utils/nodes.py` – implementação de checkpointer e metadados.
- `graph-nodes-patterns.md` – catálogo de nomes de nodes; deve ser atualizado com `plan_tool_usage` e `execute_tools`.
- Constituição (v1.8.0) – princípios XXI, XXII, XXIII regendo docstrings, manutenção incremental do `langgraph.json` e padronização de nodes.
