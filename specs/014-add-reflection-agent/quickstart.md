# Quickstart – Iterative Reflection Agent Guidance

1. **Create project folder**  
   - Duplicate the folder structure from `agente_simples/` into a new root-level directory `agente_reflexao_basica/`.
   - Copy the `.env` file from `agente_simples/` without modifications (required by Constitution Principle XII).

2. **Install dependencies (once per repo setup)**  
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   > LangGraph, langchain-core, and google-generativeai are already listed in the shared requirements file.

3. **Populate agent code**  
   - Centralize toda a lógica em `agente_reflexao_basica/main.py`, replicando o estilo do projeto `multi_agentes_sequencial`.
   - Defina o `StateGraph` com nós `generate` e `reflect`, além da função `should_continue` que retorna `END` quando `len(state["messages"]) > 6`.
   - Mantenha prompts embutidos e não adicione novos parâmetros na execução.

4. **Run the agent**  
   ```bash
   python agente_reflexao_basica/main.py
   ```
   - The script should print each draft, its corresponding reflection, and the final refined answer.

5. **Review outputs**  
   - Confirm the final answer cites at least four learning priorities.
   - Verify the number of reflections equals the configured iteration limit minus one.
   - Record the execution in `PROJETOS.md` once implementation is merged.
