# Feature Specification: Dynamic Task Agent Graph

**Feature Branch**: `001-task-agent-update`  
**Created**: 2025-11-19  
**Status**: Draft  
**Input**: User description: "Altere o projeto agente_tarefas, ele não deve mais executar cli e main, deve funcionar apenas via langgraph cli, o grafo do agente precisa ser ajustado para ser dinamico, ao invés de executar um fluxo pre estabelecido o agente deve receber a mensagem do cliente e atualizar a lista de tarefa, a mensagem pode incluir tarefas, remover ou concluir tarefas, ou simplesmente pedir para listar as tarefas, minha sugestão é que a llm responda com um json estruturado para atualizar a lista, exemplo um campo operação e um campo valores com operações predefinidas {op:listar} para listar tarefas, {op:add,tasks[estudar,fazer compras]} para adicionar as tarefas estudar e fazer compras, {op:del,tasks:[estudar]} para remover tarefas estudar. As tarefas não precisam ter um estado como pendente, concluido, o agente deve apenas gerenciar a lista, ao final do grafo precisa ser respondido com a lista atual após as operações, caso a operação seja apenas listar ele já exibe, senão ele primeiro executa as operações de adicionar ou remover tarefas, o exemplo que dei foi com uma única operação mas pode ter mais de uma operação, exemplo adicione na lista a tarefa fazer compras e remova a tarefa estudar"

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Atualizar lista em uma única mensagem (Priority: P1)

As an operations coordinator using the LangGraph CLI, I want to send natural-language instructions that describe which tasks to add or remove so the agent updates the shared list and confirms the new list in the same turn.

**Why this priority**: This is the primary flow that replaces the legacy CLI, enabling the business to maintain a single interaction model focused on quick task updates.

**Independent Test**: Trigger the agent through LangGraph CLI with a message like "Adicione estudar e revisar orçamento" and verify that the conversation ends with the updated list and confirmation of applied operations.

**Acceptance Scenarios**:

1. **Given** the list is empty, **When** the user sends "Adicione estudar e comprar mantimentos", **Then** the agent produces JSON operations with `{op:add,tasks:["estudar","comprar mantimentos"]}` and replies with the updated list showing both tasks.
2. **Given** the list already contains "estudar" and "ler", **When** the user asks "Remova estudar e adicione fazer compras", **Then** the agent executes the delete followed by the add and returns the list `["ler","fazer compras"]` in the final response.

---

### User Story 2 - Consultar lista atual sob demanda (Priority: P2)

As a team member checking progress, I want to ask the agent to list current tasks without changing them so I can review what remains outstanding.

**Why this priority**: Visibility into the current list is essential for coordination, and listing alone should not risk unintended modifications.

**Independent Test**: With any existing task list, send "Liste as tarefas" and confirm the agent only returns the ordered list plus a note that no changes were made.

**Acceptance Scenarios**:

1. **Given** the list contains "viajar" and "organizar relatórios", **When** the user submits "Liste minhas tarefas", **Then** the agent emits `{op:listar}` and replies only with the two tasks in order.

---

### User Story 3 - Receber orientação quando a instrução for ambígua (Priority: P3)

As a user who may write vague requests, I want the agent to explain what went wrong when it cannot derive the required JSON operations so I can restate my intent without corrupting the list.

**Why this priority**: Self-serve guidance reduces support needs and ensures the list is never altered by misinterpreted commands.

**Independent Test**: Send an intentionally unclear prompt (e.g., "faça algo"), verify that no tasks change, and the agent asks for clarification describing the structure it expects.

**Acceptance Scenarios**:

1. **Given** the list contains any tasks, **When** the user sends a message that the LLM cannot convert into `{op:...}` actions, **Then** the agent replies with an explanatory prompt and leaves the list untouched.

---

### Edge Cases

- Attempting to remover (delete) a task that is not on the list must not raise errors; the agent should acknowledge it was not found and still output the current list.
- When the same task appears in both add and delete instructions within one message, the agent must honor the order returned by the operations JSON so outcomes are deterministic.
- If the structured JSON cannot be parsed or is missing required fields, the agent must ask for clarification and clearly state that the list remains unchanged.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The agente_tarefas experience MUST be invoked exclusively through the LangGraph CLI; legacy `cli` and direct `main` execution paths must be disabled or guide users to the supported entrypoint.
- **FR-002**: Each user message MUST be transformed into a structured set of operations represented as JSON objects containing at least `op` (listar, add, del) and `tasks` (array when applicable).
- **FR-003**: The agent MUST support multiple operations in one turn and execute them sequentially exactly as described by the JSON returned by the LLM.
- **FR-004**: The system MUST maintain an in-memory task list scoped to the active LangGraph CLI session, storing each task as a unique, trimmed string without status metadata.
- **FR-005**: Add operations MUST append every provided task that is not already present (case-insensitive comparison) and confirm additions back to the user.
- **FR-006**: Delete operations MUST remove every matching task if it exists, report which ones were absent, and leave the list untouched for tasks that were not found.
- **FR-007**: List operations MUST return the ordered list exactly as stored and explicitly state that no changes were made during that turn.
- **FR-008**: After completing any add or delete operations, the agent MUST always present the final list so users can immediately see the new state without issuing a separate listar command.
- **FR-009**: If the structured JSON is invalid, missing, or fails validation, the agent MUST stop processing, inform the user how to format the request, and preserve the existing task list.
- **FR-010**: Every response MUST include a concise natural-language summary of the operations executed plus the resulting list to improve readability for non-technical users.

### Key Entities *(include if feature involves data)*

- **Task List**: Ordered collection of unique textual tasks maintained per session; used by all operations and displayed at the end of each turn.
- **Operation Instruction**: Structured object emitted by the LLM containing the `op` keyword and optional `tasks` array, dictating how the agent mutates or inspects the task list.
- **User Request Context**: Aggregated data for the current turn, including the original message, parsed operations, and any validation errors used to craft the final response.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: During UAT, 100% of attempts to start agente_tarefas outside the LangGraph CLI are blocked or redirected, ensuring a single supported interface.
- **SC-002**: 95% of requests that include add or delete instructions yield the correct updated list and confirmation in no more than one LangGraph turn as verified by automated conversation tests.
- **SC-003**: 100% of listar-only requests return the unchanged ordered list within 3 seconds of the prompt per performance monitoring.
- **SC-004**: In all negative-test runs (minimum of 5 scenarios), invalid or ambiguous instructions result in clarification guidance with zero unintended task mutations, as confirmed by log review.

## Assumptions

- Task descriptions are treated as unique strings ignoring letter case and leading/trailing whitespace.
- A single LangGraph CLI session corresponds to one user at a time; shared persistence or multi-user merges are out of scope.
- Supported operations are limited to listar, add, and del; any future operations will require additional specification.
