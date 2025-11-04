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
   - **Output**: lista `tool_plans` com nome/args/call_id para cada ferramenta solicitada; caso contrário lista vazia.
3. `execute_tools`
   - **Precondition**: `tool_plans` definido com ao menos uma entrada.
   - **Output**: lista de `ToolMessage` para cada chamada, preenchendo `tool_calls` com resultados/erros.
4. `invoke_model`
   - **Input**: mensagens completas após ferramentas.
   - **Regras especiais**: somente a primeira invocação inclui o `system_prompt`; a partir da segunda, o histórico recebe uma nova mensagem do usuário `"Continue gerando sua resposta."` para orientar a continuação.
   - **Output**: nova mensagem do modelo com resposta textural.
5. `format_response`
   - **Input**: estado final.
   - **Output**: `resposta` formatada, `duration_seconds` e `status final`.

## Error Handling
- Inputs inválidos retornam resposta orientando o usuário a reformular.
- Falhas na ferramenta retornam `status="error"` com mensagem segura.
- Exceções do modelo registram log e retornam mensagem de indisponibilidade.
