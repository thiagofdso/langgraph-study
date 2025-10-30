# Feature Specification: Terminal Task Session Agent

**Feature Branch**: `[013-task-agent]`  
**Created**: 2025-10-30  
**Status**: Draft  
**Input**: User description: "Quero um projeto para estudo. Crie na pasta agente_tarefas um agente que gera uma lista de tarefas a partir de uma entrada do usuário e marca tarefas como concluídas mediante comandos simples. O programa deve esperar resposta do usuário no terminal, deve ocorrer em 3 rodadas: 1 entrada para criar lista, indicar qual tarefa marcar e 3 adicionar tarefas. O próximo requisito é o 013."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture initial task list (Priority: P1)

As a learner running the study project, I want to enter several task descriptions in the first terminal prompt and immediately see a numbered list so I can confirm what the agent understood before moving on.

**Why this priority**: Without a reliable first-round list, the rest of the three-step flow cannot operate, so it is foundational to the session.

**Independent Test**: Launch the agent in `agente_tarefas`, provide sample tasks (e.g., "Estudar matemática, Lavar louça"), and verify the program echoes them as a numbered list while the session waits for confirmation.

**Acceptance Scenarios**:

1. **Given** the agent has started round 1, **When** the user submits one or more task descriptions separated by commas or new lines, **Then** the agent displays each task with an index starting at 1 and confirms the session will proceed to round 2 only after the display.
2. **Given** the user enters blank input in round 1, **When** the agent receives the submission, **Then** it asks for at least one task before advancing and does not crash or skip ahead.

---

### User Story 2 - Mark a task as completed (Priority: P2)

As a learner, I want to choose which task from the list is completed during the second prompt using a simple number-based command so I can see how the agent updates task status.

**Why this priority**: Demonstrating completion feedback is the core learning goal after list creation and enables the final summary to be meaningful.

**Independent Test**: From round 2, type the index of an existing task (e.g., "2") and confirm the agent responds with a success message and a refreshed list highlighting the completed item.

**Acceptance Scenarios**:

1. **Given** the numbered list is displayed, **When** the user inputs a valid index or shorthand command that references one task, **Then** the agent marks that task as completed, shows the updated status, and transitions to round 3 only after displaying the confirmation.
2. **Given** the user inputs an index outside the current range, **When** the agent processes the command, **Then** it explains the error, offers one more chance within the same round, and only advances once a valid selection or retry limit response is provided.

---

### User Story 3 - Add new tasks in the final round (Priority: P3)

As a learner, I want to append additional tasks in the third prompt so I can observe how the agent combines newly added activities with the existing completed and pending items.

**Why this priority**: Adding tasks in the final round showcases list growth and prepares a richer summary for the session wrap-up.

**Independent Test**: During round 3, add at least one new task description, confirm the agent acknowledges each addition, and verify the closing summary reflects the expanded list and completion counts.

**Acceptance Scenarios**:

1. **Given** at least one task has been marked completed, **When** the user supplies more task descriptions in round 3, **Then** the agent appends them to the pending section while preserving previous completion states and presents a comprehensive summary before exiting.

---

### Edge Cases

- User submits only whitespace during any prompt—agent must request a valid response without terminating the session.
- User attempts to complete a task that is already marked done—the agent should remind the user of its current status and keep the completion log unchanged.
- Third-round input repeats an existing task description—the agent should flag the duplicate and ask whether to keep or discard it within the same interaction.
- User tries to add tasks after signalling they have none to add—the agent should confirm the decision and close with the current summary rather than looping indefinitely.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The study project MUST reside under `agente_tarefas/` with a terminal entry point that remains idle until the user provides input for each of the three rounds.
- **FR-002**: In round 1, the agent MUST prompt the user for one or more task descriptions, parse the response into individual items, and display a numbered list before proceeding.
- **FR-003**: The agent MUST validate round-1 input, rejecting empty submissions with a clear message and allowing the user to retry without restarting the program.
- **FR-004**: In round 2, the agent MUST accept a simple command that references a single task by its displayed index, mark that task as completed, and present confirmation together with the updated list.
- **FR-005**: If the round-2 command references a non-existent index or repeats an already completed task, the agent MUST present a corrective prompt and offer at least one additional attempt within the same round.
- **FR-006**: In round 3, the agent MUST invite the user to add zero or more new tasks, append valid additions to the list, and preserve completion states captured in earlier rounds.
- **FR-007**: When duplicate task descriptions are proposed in round 3, the agent MUST ask the user whether to accept or skip each duplicate and document the decision in the final summary.
- **FR-008**: After completing round 3, the agent MUST output a closing summary that separates completed and pending tasks, includes totals for each category, and instructs the user on how to restart the session if desired.

### Key Entities

- **Task Item**: A single to-do description with attributes for its display index, textual description, and completion status.
- **Session Timeline**: The ordered collection of interactions across the three rounds, tracking prompts presented, user responses, and transitions between rounds.
- **User Command**: The interpreted intent derived from each user input (e.g., list creation, completion selection, task addition) along with validation results and any follow-up prompts required.

## Assumptions & Constraints

- Interaction language defaults to Portuguese, matching the user request and ensuring prompts feel natural to learners.
- One execution of the agent covers exactly three rounds (create, complete, add) before presenting the final summary and exiting.
- Manual terminal usage is sufficient; no graphical interface or external integrations are expected for this study scenario.
- Sample documentation will provide example inputs for each round so learners understand expected separators and command formats.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: During usability tests, 95% of first-round submissions with at least one task result in a numbered list and readiness for round 2 within 10 seconds of user input.
- **SC-002**: Across five consecutive sessions, every valid round-2 selection updates the chosen task to "completed" and displays confirmation without requiring additional commands.
- **SC-003**: Whenever a user adds at least one task in round 3, the final summary reflects the new total count of pending tasks and distinguishes them from previously completed items in a single closing message.
- **SC-004**: In monitored runs, the agent waits for explicit user input at each round with no unsolicited transitions, ensuring users remain in control of pacing 100% of the time.
