# Data Model: Calculator Agent

## Entities

### Agent
-   **Description**: The core AI entity responsible for processing user input, identifying calculation needs, and orchestrating the use of the calculator tool.
-   **Attributes**:
    -   `id`: Unique identifier for the agent instance (UUID).
    -   `llm_model`: The specific language model used (e.g., `gemini-2.5-flash`).
    -   `tools`: A list of tools available to the agent, including the `Calculator Tool`.

### Calculator Tool
-   **Description**: A specialized tool designed to perform mathematical evaluations.
-   **Attributes**:
    -   `name`: "calculator" (string).
    -   `description`: A description of the tool's capabilities (string, e.g., "Evaluates mathematical expressions").
    -   `function`: The underlying function that executes the calculation (callable).
-   **Relationships**:
    -   Many-to-one with `Agent` (an agent can have multiple tools, including a calculator).
