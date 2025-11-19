# Feature Specification: Graph-Managed Task Workflow

**Feature Branch**: `001-refactor-task-graph`  
**Created**: 2025-11-19  
**Status**: Draft  
**Input**: User description: "Quero que o projeto agente_tarefas seja reestruturado de forma que o estado das tarefas não seja atualizado diretamente no cli como está sendo feito, ele deve ser feito através de nodes dentro do grafo. Pontos importantes: o teste via main deve continuar funcionando, via pytest e via langgraph cli também. Deve ser acresentado nodes e ajustado o grafo conforme necessário."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CLI session managed by the graph (Priority: P1)

As a Portuguese-speaking user que executa `python -m agente_tarefas`, quero completar as três rodadas enquanto o grafo controla todas as mudanças no estado das tarefas, para que o fluxo fique consistente e rastreável em qualquer interface.

**Why this priority**: A experiência principal acontece no CLI; remover a lógica de estado local é essencial para manter o agente confiável e preparado para futuras integrações.

**Independent Test**: Simular uma sessão completa com entradas conhecidas e verificar que as listas de tarefas, IDs concluídos e timeline retornados pelo grafo refletem exatamente os inputs do usuário sem mutações diretas no CLI.

**Acceptance Scenarios**:

1. **Given** um usuário informa tarefas na Rodada 1, **When** o CLI envia apenas as mensagens ao grafo, **Then** o próprio grafo grava a lista de `TaskItem` e retorna a resposta que o CLI exibe.
2. **Given** uma tarefa é marcada como concluída na Rodada 2, **When** o CLI envia o ID selecionado ao grafo, **Then** o grafo atualiza o estado (status e `completed_ids`) e devolve uma mensagem que reflete o novo progresso.
3. **Given** novas tarefas (com possíveis duplicatas) são informadas na Rodada 3, **When** o CLI confirma as escolhas com o usuário, **Then** o grafo registra quais itens entraram, adiciona notas de duplicidade e fornece o resumo final.

---

### User Story 2 - Automated validation protects the flow (Priority: P2)

Como QA/DevOps, quero que os testes automatizados exercitem o grafo refatorado (main module, suíte de testes e execuções programáticas) para detectar qualquer regressão quando o estado é gerenciado pelos nodes.

**Why this priority**: Sem cobertura automatizada, uma alteração no grafo poderia quebrar o CLI tradicional, a suíte de testes ou integrações futuras.

**Independent Test**: Executar o conjunto de testes automatizados e um smoke test via módulo principal, verificando que estados retornados pelo grafo permanecem consistentes em execuções repetidas.

**Acceptance Scenarios**:

1. **Given** um ambiente limpo, **When** a suíte automatizada roda, **Then** cada teste que antes inspecionava o estado do CLI passa a validar as saídas do grafo (incluindo nodes recém-criados) sem depender de mutações locais.
2. **Given** um operador roda o módulo principal (`python -m agente_tarefas`) em modo interativo controlado, **When** a sessão termina, **Then** o log interno mostra que cada rodada foi registrada no estado do grafo.

---

### User Story 3 - LangGraph CLI operators mirror the experience (Priority: P3)

Como operador que usa o comando `langgraph run agente-tarefas`, preciso que o grafo execute toda a jornada sem qualquer dependência do CLI customizado, garantindo que ambientes headless também reflitam o estado correto.

**Why this priority**: A CLI oficial do LangGraph precisa compartilhar o mesmo grafo para habilitar execuções em pipelines ou demonstrações remotas.

**Independent Test**: Invocar o grafo pelo LangGraph CLI com entradas mockadas e validar que o estado agregado (tarefas, timeline, duplicatas) vem exclusivamente dos nodes novos.

**Acceptance Scenarios**:

1. **Given** o comando `langgraph run agente-tarefas` recebe entradas preparadas, **When** o grafo processa cada rodada, **Then** os nodes criados atualizam o estado e retornam os mesmos resumos usados pelo CLI tradicional.
2. **Given** uma execução é retomada a partir de um checkpointer, **When** o LangGraph CLI reenvia mensagens para rodadas subsequentes, **Then** o estado restaurado mantém tarefas e IDs concluídos porque foram persistidos via nodes, não via CLI.

---

### Edge Cases

- Quando a Rodada 2 é acionada sem que a Rodada 1 tenha gravado tarefas (por reconexão ou nova thread), o grafo deve rejeitar a solicitação de conclusão com feedback claro e manter o estado inalterado.
- Quando tarefas duplicadas são propostas na Rodada 3, os nodes precisam registrar a decisão do usuário (manter ou descartar) para que o resumo final e a timeline reflitam exatamente o histórico.
- Quando o mesmo ID de tarefa é marcado como concluído mais de uma vez, o grafo deve responder com uma mensagem de erro amigável e preservar a consistência da lista `completed_ids`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O grafo deve ser reorganizado em múltiplos nodes especializados (ingestão inicial, conclusão, inclusão de novas tarefas e geração de resposta) que encapsulam qualquer mutação de `tasks`, `completed_ids` e `timeline`.
- **FR-002**: O CLI e demais chamadores só podem enviar entradas do usuário e mensagens ao grafo; qualquer modificação em estruturas de estado deve ser realizada pelos nodes antes de retornar o resultado.
- **FR-003**: Cada node precisa retornar o estado completo e consistente após sua execução, permitindo que o próximo passo (ou um re-run) leia os dados sem depender de variáveis locais do CLI.
- **FR-004**: O grafo deve validar a ordem das rodadas (por exemplo, impedir Rodada 2 sem tarefas carregadas) e devolver mensagens específicas quando a sequência for violada.
- **FR-005**: Timeline e notas operacionais precisam ser enriquecidas dentro do grafo, vinculando cada rodada ao respectivo input do usuário, ID de tarefa afetado e resumo entregue.
- **FR-006**: A execução via módulo principal (`python -m agente_tarefas`) deve continuar funcionando ponta a ponta, comprovando que o CLI se tornou apenas um coletor de entrada e exibidor de respostas.
- **FR-007**: As suítes de teste existentes e novas devem conseguir injetar modelos/dados fake para validar a lógica dos nodes sem depender do CLI interativo.
- **FR-008**: O comando `langgraph run agente-tarefas` deve operar sobre o mesmo grafo refatorado, preservando comportamento e resultados equivalentes ao CLI personalizado.
- **FR-009**: O grafo precisa expor pontos claros para adicionar nodes complementares no futuro (ex.: logs, reflexão), sem exigir retorno de lógica de estado ao CLI.

### Key Entities *(include if feature involves data)*

- **TaskItem**: Representa cada tarefa com `id`, descrição, status e a rodada que o originou; passa a ser alterado apenas pelos nodes responsáveis.
- **TimelineEntry**: Registro ordenado das três rodadas contendo input do usuário, resposta do agente e notas de duplicidades; usado para auditoria do fluxo.
- **SessionContext**: Conjunto formado por `messages`, `tasks`, `completed_ids`, `timeline` e metadados de thread que circula entre os nodes e garante continuidade em qualquer entrada (CLI, testes, LangGraph CLI).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em uma sessão completa iniciada pelo CLI principal do agente, o log do grafo evidencia exatamente três mutações de estado (uma por rodada) executadas por nodes, com zero atribuições diretas do coletor de entrada — condição verificada durante QA.
- **SC-002**: Todos os testes automatizados e smoke tests relacionados ao agente de tarefas executam até o fim sem falhas na primeira rodada após o refactor, demonstrando que o novo grafo é compatível com os entry points existentes.
- **SC-003**: A interface oficial de execução do grafo (CLI usada em pipelines e demos) conclui a jornada das três rodadas sem erros e produz um resumo final contendo todas as tarefas registradas, comprovando suporte a ambientes headless.
- **SC-004**: Para cada sessão concluída, o estado final contém três entradas de timeline e pelo menos um item em `completed_ids`, garantindo que todo o ciclo foi tratado pelos nodes refatorados.

## Assumptions & Dependencies

- O CLI continuará responsável apenas por coletar inputs/confirmar duplicatas e poderá ser adaptado para repassar essas decisões como mensagens ou metadados aos nodes.
- O checkpointer configurado atualmente permanece válido; os nodes precisam somente respeitar o formato já usado em `AgentState`.
- Os prompts existentes (round1/round2/round3) continuarão sendo chamados, mas agora partirão de nodes que já possuem o estado atualizado.
- Não há novas integrações externas além das já suportadas; a refatoração foca apenas no agente `agente_tarefas` e seus testes associados.
