# Agent Workflow Contract – agente_tool

## Command Entry Point
- **Command**: `python -m agente_tool run "<pergunta>"`
- **Inputs**:
  - `pergunta: str` – mensagem do usuário, mínimo 5 caracteres úteis.
- **Outputs**:
  - `resposta: str` – texto formatado iniciado por `Resposta do agente:`.
  - `status: str` – `"completed"` ou `"error"` conforme resultado.

## Node Responsibilities
1. `validate_input`
   - **Input**: mensagens acumuladas.
   - **Output**: metadata com pergunta e hora de início; `status="validated"` ou `status="error"`.
2. `plan_tool_usage`
   - **Input**: metadata e mensagens.
  - **Output**: `tool_plan` com nome/args quando ferramenta for necessária; caso contrário `None`.
3. `execute_tools`
   - **Precondition**: `tool_plan` definido.
   - **Output**: mensagem com resultado da ferramenta e atualização do `status`.
4. `invoke_model`
   - **Input**: mensagens completas após ferramentas.
   - **Output**: nova mensagem do modelo com resposta textural.
5. `format_response`
   - **Input**: estado final.
   - **Output**: `resposta` formatada, `duration_seconds` e `status final`.

## Error Handling
- Inputs inválidos retornam resposta orientando o usuário a reformular.
- Falhas na ferramenta retornam `status="error"` com mensagem segura.
- Exceções do modelo registram log e retornam mensagem de indisponibilidade.
