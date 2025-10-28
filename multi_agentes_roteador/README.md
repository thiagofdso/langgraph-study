# Router Persona Agent

This project implements a router agent using Langgraph that directs user interactions to different persona agents based on the user's age. It features an informal agent for young users (age <= 30) and a formal agent for non-young users (age > 30). The system also includes a simulation to demonstrate its functionality with two distinct conversations.

## Features

-   **Router Agent**: Routes user input based on age criteria.
-   **Informal Persona Agent**: Responds with emojis and informal language for young users.
-   **Formal Persona Agent**: Responds with serious and cordial language for non-young users.
-   **Langgraph Integration**: Utilizes Langgraph for state management and graph-based agent orchestration.
-   **In-memory Persistence**: Uses `InMemorySaver` for managing conversation state per `thread_id`.
-   **Simulated Conversations**: Demonstrates the routing and persona-based responses with example interactions.

## Setup

1.  **Clone the repository** (if you haven't already):

    ```bash
    git clone <repository_url>
    cd langgraph
    ```

2.  **Create a Python Virtual Environment** (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:

    Ensure all required Python dependencies are installed. You can do this by running:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**:

    Create a `.env` file in the root of the project and add your `GEMINI_API_KEY`:

    ```dotenv
    GEMINI_API_KEY="your_gemini_api_key_here"
    ```

    Replace `"your_gemini_api_key_here"` with your actual Google Gemini API key.

## Running the Simulation

To run the agent simulation, execute the `main.py` script located in the `multi_agentes_roteador` directory:

```bash
PYTHONPATH=. python multi_agentes_roteador/main.py
```

The program will then simulate two conversations:

-   One with a young user (age 25) asking "Qual é a capital da França?".
-   One with a non-young user (age 45) asking "Poderia me informar a capital da França, por gentileza?".

### Expected Output

The output will demonstrate the router directing the questions to the appropriate persona agent, with responses tailored to the user's age and persona.

```text
--- Conversation for Thread ID: young_user_1 (Age: 25) ---
User: 25: Qual é a capital da França?
Agent: E aí, meu chapa! 🤩 Essa é moleza demais! A capital da França é a lindíssima **Paris**! 🇫🇷✨

Cidade do amor, da Torre Eiffel, dos croissants... ai, que delícia! 💖🥐🗼 É tipo um sonho, tá ligado? 😎

Acertou em cheio! Mandou bem na pergunta! 😉

--- Conversation for Thread ID: non_young_user_1 (Age: 45) ---
User: 45: Poderia me informar a capital da França, por gentileza?
Agent: Com certeza! A capital da França é **Paris**.

Se precisar de mais alguma informação, estou à disposição.
```
