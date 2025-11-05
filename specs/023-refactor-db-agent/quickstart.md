# Quickstart — agente_banco_dados Refatorado

1. **Ative o ambiente virtual do repositório**
   ```bash
   source venv/bin/activate
   ```

2. **Inicialize o banco local e gere o relatório via CLI tradicional**
   ```bash
   python agente_banco_dados/main.py
   ```
   - A saída deve incluir as contagens de seed e o relatório Markdown completo.

3. **Execute o grafo diretamente (programático)**
   ```python
   from agente_banco_dados import create_app, initialize_database

   initialize_database()
   app = create_app()
   result = app.invoke({})
   print(result["report_markdown"])
   ```

4. **Rodar pelo LangGraph CLI (após registrar no `langgraph.json`)**
   ```bash
   langgraph run agente_banco_dados
   ```

5. **Validar regressão automáticamente**
   ```bash
   pytest tests/test_agente_banco_dados.py
   ```

> **Nota**: Todas as execuções permanecem offline e dependem apenas do SQLite local populado por `initialize_database()`.
