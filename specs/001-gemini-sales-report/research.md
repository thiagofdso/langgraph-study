# Research Notes — Relatório de Vendas com Insights Gemini

## Decision: Reutilizar padrão de configuração LLM do `agente_simples`
- **Rationale**: O `langgraph-tasks.md` requer uma fábrica dedicada (`utils/llm.py`) que delega a criação do cliente Gemini para `config.py`, espelhando o desenho comprovado em `agente_simples`. Essa abordagem já contempla carregamento de `.env`, validação da chave `GEMINI_API_KEY` e separação clara entre configuração e lógica de nós.
- **Alternatives considered**: Instanciar o modelo diretamente em `generate_insights_node`; rejeitado por dificultar testes (impossível monkeypatch sem duplicar lógica) e por violar a separação preconizada nos demais agentes do repositório.

## Decision: Inserir nó intermediário `generate_insights` no grafo
- **Rationale**: A especificação exige narrativa gerada pela IA antes da renderização final. A arquitetura atual tem apenas `load_sales_metrics` → `render_sales_report`; criar um nó intermediário mantém a coesão do pipeline e permite registrar métricas de latência, alinhado às instruções de `langgraph-tasks.md`.
- **Alternatives considered**: Invocar a IA dentro do próprio `render_sales_report`; rejeitado porque combinaria responsabilidades (consulta à IA + formatação final) e dificultaria identificar falhas de LLM separadamente.

## Decision: Novo módulo `utils/prompts.py` com prompt estruturado
- **Rationale**: O prompt precisa ser reaproveitável e testável, e o documento de tarefas recomenda centralizar o template para manutenção. Também facilita atualizar o prompt sem tocar nos nós.
- **Alternatives considered**: Manter o prompt como string inline em `generate_sales_insights`; rejeitado por comprometer legibilidade e dificultar futuras evoluções (por exemplo, localizar regras adicionais).

## Decision: Propagar metadados de execução no estado
- **Rationale**: O spec define requisitos de auditoria (SC-002, FR-007). Armazenar `llm_latency_seconds` e `processed_records` dentro de `metadata` permite expor essas informações ao consumidor ou logs, seguindo o padrão já existente (`metadata` dicionário).
- **Alternatives considered**: Registrar apenas em logs; rejeitado porque exigiria parsing de logs para testes e violaria FR-007, que pede disponibilidade “em metadados acessíveis”.

## Decision: Atualizar `graph-nodes-patterns.md` com o novo node
- **Rationale**: Constituição (Princípio XXIII) exige manter catálogo sincronizado. O novo node `generate_insights` possui responsabilidade inédita (chamar IA para síntese de dados tabulares) e precisa ser documentado.
- **Alternatives considered**: Reutilizar nome existente como `invoke_model`; rejeitado pois a função difere (usa prompt específico e retorna narrativa complementar a dados já agregados).
