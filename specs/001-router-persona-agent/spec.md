# Feature Specification: Router Persona Agent

**Feature Branch**: `001-router-persona-agent`  
**Created**: 2025-10-28  
**Status**: Draft  
**Input**: User description: "Quero que crie na pasta multi_agentes_roteador, aproveitando o que existe no agente_memoria e no multi_agentes_sequencial, um sistema com um agente roteador que recebe uma mensagem introdutoria em que o usuario informa a idade e uma pergunta. O roteador entao deve verificar pela idade se o usuário e jovem (ate 30 anos), caso seja jovem direciona para um agente que responde usando emojis e uma linguagem mais informal, caso nao seja jovem direciona para outro agente com linguagem mais seria e cordial. O programa deve simular duas conversas uma com uma perssoa jovem e outra com uma pessoa que nao é jovem."

## User Scenarios & Testing (mandatory)

### User Story 1 - Young User Interaction (Priority: P1)

As a young user (up to 30 years old), I want to interact with the system and receive responses using emojis and informal language, so that the conversation feels natural and engaging.

**Why this priority**: This is a core functionality demonstrating the agent's ability to adapt its persona based on user age.

**Independent Test**: The agent can be fully tested by providing an age <= 30 and a question, and verifying that the response contains emojis and informal language.

**Acceptance Scenarios**:

1.  **Given** the router agent receives input with age <= 30 and a question, **When** the router processes the input, **Then** the response comes from the informal agent, containing emojis and informal language.

---

### User Story 2 - Non-Young User Interaction (Priority: P1)

As a non-young user (over 30 years old), I want to interact with the system and receive responses using formal and cordial language, so that the conversation is respectful and professional.

**Why this priority**: This is a core functionality demonstrating the agent's ability to adapt its persona based on user age.

**Independent Test**: The agent can be fully tested by providing an age > 30 and a question, and verifying that the response uses serious and cordial language.

**Acceptance Scenarios**:

1.  **Given** the router agent receives input with age > 30 and a question, **When** the router processes the input, **Then** the response comes from the formal agent, using serious and cordial language.

---

### User Story 3 - Simulated Conversations (Priority: P1)

As a developer, I want the program to simulate two conversations, one with a young person and one with a non-young person, to demonstrate the router's functionality.

**Why this priority**: This story provides a clear demonstration and verification of the router's core functionality.

**Independent Test**: The program can be executed, and the output can be verified to show two distinct conversations, each demonstrating the appropriate agent persona based on the simulated age.

**Acceptance Scenarios**:

1.  **Given** the program is executed, **When** the simulation runs, **Then** it outputs two distinct conversations, each demonstrating the appropriate agent persona based on the simulated age.

### Edge Cases

-   What happens if the age is not provided or is invalid (e.g., negative, non-numeric)?
-   How does the system handle ambiguous questions that might fit both personas?

## Requirements (mandatory)

### Functional Requirements

-   **FR-001**: The system MUST include a router agent.
-   **FR-002**: The router agent MUST receive an introductory message containing the user's age and a question.
-   **FR-003**: The router agent MUST determine if the user is "young" (age <= 30).
-   **FR-004**: If the user is "young", the router MUST direct the interaction to an informal agent.
-   **FR-005**: The informal agent MUST respond using emojis and informal language.
-   **FR-006**: If the user is NOT "young", the router MUST direct the interaction to a formal agent.
-   **FR-007**: The formal agent MUST respond using serious and cordial language.
-   **FR-008**: The system MUST leverage existing components from `agente_memoria` and `multi_agentes_sequencial`.
-   **FR-009**: The program MUST simulate two conversations: one with a young user and one with a non-young user.
-   **FR-010**: The project code MUST be located in the `multi_agentes_roteador` folder.

### Key Entities

-   **Router Agent**: Responsible for receiving user input (age, question) and directing to the appropriate persona agent.
-   **Informal Agent**: Responds to young users with emojis and informal language.
-   **Formal Agent**: Responds to non-young users with serious and cordial language.
-   **User Input**: Contains age and a question.

## Success Criteria (mandatory)

### Measurable Outcomes

-   **SC-001**: The router agent correctly directs 100% of young users (age <= 30) to the informal agent.
-   **SC-002**: The router agent correctly directs 100% of non-young users (age > 30) to the formal agent.
-   **SC-003**: The informal agent's responses consistently contain emojis and informal language.
-   **SC-004**: The formal agent's responses consistently use serious and cordial language.
-   **SC-005**: The program successfully simulates two distinct conversations, demonstrating both persona agents.

## Assumptions

-   The `agente_memoria` and `multi_agentes_sequencial` folders contain reusable components that can be adapted for the informal and formal agents, or for the overall agent structure.
-   The age will be provided as a numerical value in the introductory message.
-   The definition of "informal" and "formal" language will be implemented based on common linguistic patterns and the use of emojis.