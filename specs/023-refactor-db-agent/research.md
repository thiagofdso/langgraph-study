# Phase 0 Research — Refactor agente_banco_dados

## Decision 1 — Estrutura modular espelhando `agente_simples`
- **Decision**: Reorganizar `agente_banco_dados` para a mesma topologia de pacotes usada em `agente_simples` (`state`, `utils/nodes.py`, `graph.py`, `cli.py`, testes dedicados), mantendo módulos existentes de banco e relatório.
- **Rationale**: Facilita manutenção e onboarding (já documentado em `PROJETOS.md`), habilita o uso imediato do LangGraph CLI com `create_app()` e atende às boas práticas listadas em `langgraph-tasks.md`.
- **Alternatives considered**: Ajustar apenas `main.py` para expor `create_app()` sem reorganizar arquivos — rejeitado por não resolver o acoplamento atual nem alinhar com o padrão institucional de agentes.

## Decision 2 — Reutilizar consultas e formatação atuais em nodes puros
- **Decision**: Encapsular `query_top_products`, `query_top_sellers` e `build_markdown_report` em nós puros (`load_sales_metrics`, `render_sales_report`) sem alterar as consultas SQL ou o layout do Markdown.
- **Rationale**: Garante paridade de saída (SC-001), reduz risco de regressão e cumpre a exigência de manter funcionalidade.
- **Alternatives considered**: Reescrever formatação usando bibliotecas externas (ex.: `tabulate`) — rejeitado para evitar diferenças no relatório e dependências adicionais.

## Decision 3 — Manter inicialização do banco no CLI
- **Decision**: Preservar `initialize_database()` como passo explícito do CLI antes de invocar o grafo, registrando as contagens de seed como hoje.
- **Rationale**: Mantém experiência atual do usuário e suporta execuções repetidas idempotentes, além de atender ao requisito de relatórios exclusivamente a partir do SQLite local.
- **Alternatives considered**: Invocar `initialize_database()` dentro de um node inicial do grafo — rejeitado por misturar efeitos colaterais com nodes puramente funcionais e complicar testes.

## Decision 4 — Atualização incremental de catálogos e registros
- **Decision**: Atualizar `graph-nodes-patterns.md` com os novos nomes de nodes e acrescentar o grafo em `langgraph.json` apenas se ainda não listado.
- **Rationale**: Cumpre os Princípios XXII e XXIII da Constituição e mantém governança sobre nomenclatura.
- **Alternatives considered**: Nenhuma atualização — rejeitado, pois violaria o catálogo de padrões e dificultaria rastreabilidade.
