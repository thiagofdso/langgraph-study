# Quickstart for Router Persona Agent

This feature implements a router agent that directs user input to either an informal or formal persona agent based on the user's age. It also includes a simulation of two conversations to demonstrate its functionality.

## Setup

1.  **Dependencies**: Ensure all required Python dependencies are installed (refer to `requirements.txt`).
2.  **Environment Variables**: Set up necessary environment variables (e.g., `GEMINI_API_KEY`) in a `.env` file.

## Running the Simulation

To run the agent simulation, execute the `main.py` script located in the `multi_agentes_roteador` directory:

```bash
PYTHONPATH=. python multi_agentes_roteador/main.py
```

The program will then simulate two conversations, one with a young user and one with a non-young user, demonstrating the routing and persona-based responses.
