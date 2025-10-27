# Feature Specification: Simple Hello Agent

**Feature Branch**: `001-simple-hello-agent`  
**Created**: 2025-10-27  
**Status**: Draft  
**Input**: User description: "Quero um agente de ia simples, estilo hello world ele deve simplesmente responder quantos paízes tem o brasil, deve ficar na pasta agente_simples"

## Clarifications

### Session 2025-10-27
- Q: The question "quantos paízes tem o brasil" (how many countries does Brazil have?) is ambiguous. What is the correct response the agent should give? → A: The question should be "quantos estados tem o brasil" (how many states does Brazil have?).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agent Responds to Question (Priority: P1)

As a user, I want to ask the agent "quantos estados tem o brasil?" and receive a correct answer.

**Why this priority**: This is the core functionality of the agent.

**Independent Test**: The agent can be tested by running it and providing the specific question.

**Acceptance Scenarios**:

1.  **Given** the agent is running, **When** the user asks "quantos estados tem o brasil?", **Then** the agent should respond with the correct answer.

### Edge Cases

*   What happens if the user asks a different question? (The agent is not expected to answer, but the behavior should be defined).
*   What happens if the user provides no input?

## Requirements *(mandatory)*

### Functional Requirements

*   **FR-001**: The agent's code MUST be located in a directory named `agente_simples`.
*   **FR-002**: The agent MUST respond to the exact question "quantos estados tem o brasil?".
*   **FR-003**: The agent's response MUST be accurate. The correct answer is "O Brasil tem 26 estados e 1 Distrito Federal.".

## Success Criteria *(mandatory)*

### Measurable Outcomes

*   **SC-001**: The agent correctly answers the specified question 100% of the time.
*   **SC-002**: The agent's source code is located in the `agente_simples` directory.
