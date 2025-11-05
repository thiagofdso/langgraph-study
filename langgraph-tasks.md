# Tarefas de Refatoração – agente_web

## Contexto
- Seguir o `graph-nodes-patterns.md` para manter nomes e responsabilidades de nodes (`buscar` → `resumir`).
- Garantir estrutura de projeto equivalente aos agentes mais recentes (state/config/graph/utils).
- Avaliar e aplicar `ToolNode` para a etapa de busca web, alinhado ao padrão do `agente_tool`.

## Tarefas Principais

### 1. Estruturar o pacote `agente_web` em camadas
- [x] Criar `state.py`, `config.py`, `graph.py` e `utils/`.
- [x] Mover lógica de nodes para `utils/nodes.py`, mantendo ordem `buscar` → `resumir`.
- [x] Expor símbolos principais em `agente_web/__init__.py`.

```python
# agente_web/state.py
class GraphState(TypedDict, total=False):
    question: str
    metadata: dict[str, Any]
    search_results: list[dict[str, Any]]
    summary: str
    warnings: list[str]
```

### 2. Centralizar configuração e credenciais
- [x] Criar `AppConfig` com carregamento automático de `.env`.
- [x] Validar `TAVILY_API_KEY` e `GEMINI_API_KEY` com mensagens amigáveis.
- [x] Padronizar criação de ferramentas/modelos/checkpointer.

```python
config = AppConfig()
search_tool = config.create_search_tool()  # garante TAVILY_API_KEY
summary_model = config.create_model()      # garante GEMINI_API_KEY
```

### 3. Integrar `ToolNode` para a busca Tavily
- [x] Instanciar `ToolNode` (mesmo padrão do `agente_tool`) e reutilizá-lo dentro do node `buscar`.
- [x] Construir `tool_call` determinístico com UUID e argumentos normalizados.
- [x] Normalizar a resposta do `ToolMessage` e propagar avisos consistentes.

```python
tool_calls = build_search_tool_calls(question, tool_name, max_results=cfg.tavily_max_results)
tool_response = tool_runner.invoke(tool_calls)
messages = tool_response.get("messages") or []
results = parse_tool_payload(messages[-1].content)
```

### 4. Preservar estado imutável e boas práticas de warnings
- [x] Evitar mutação direta do estado (retornar dicionário com diffs).
- [x] Adicionar helper `merge_warnings` para manter lista copiável.
- [x] Acrescentar avisos de poucos resultados e erros externos.

```python
warnings = merge_warnings(state.get("warnings"))
if len(results) < 2:
    warnings = merge_warnings(warnings, "Poucos resultados encontrados.")
return {"search_results": final_results, "warnings": warnings}
```

### 5. Refinar geração do resumo com Gemini
- [x] Reutilizar prompts de `prompts.py` e limitar fontes (`SUMMARY_MAX_SOURCES`).
- [x] Tratar respostas lista/str do Gemini e capturar exceções externas.
- [x] Fornecer fallback quando não houver resultados.

```python
response = model.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
content = response.content if isinstance(response.content, str) else "".join(part.get("text", "") for part in response.content)
```

### 6. Atualizar CLI e relatório smoke test
- [x] Padronizar `main(argv)` retornando `int` e gravar saída em `smoke_test_output.txt`.
- [x] Reaproveitar `AppConfig.default_question` quando o usuário não informar pergunta.
- [x] Tratar `ConfigurationError` e informar comando de correção.

```python
def main(argv: Optional[list[str]] = None) -> int:
    question = " ".join(argv or sys.argv[1:]).strip() or config.default_question
    final_state = run_graph(question, app_config=config)
    report = render_output(final_state, question)
    _write_report(report)
    return 0
```

## Checklist Pós-Refatoração
- [x] Estrutura modular criada (`state`, `config`, `graph`, `utils`).
- [x] `ToolNode` utilizado para a busca.
- [x] Ordem dos nodes preservada (`buscar` → `resumir`).
- [x] Warnings e erros tratados sem mutação de estado.
- [x] CLI gera relatório e persiste `smoke_test_output.txt`.
- [ ] Adicionar testes unitários para `buscar`/`resumir` (seguinte iteração).
- [ ] Documentar .env.example específico do agente.

