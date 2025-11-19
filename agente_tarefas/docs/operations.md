# Operações do agente_tarefas

Este documento resume o fluxo operacional do agente de tarefas em três rodadas.

1. **Preparação**
   - Configure `agente_tarefas/.env` com `GEMINI_API_KEY` (e outras variáveis opcionais como `GEMINI_MODEL`).
   - Ative o virtualenv do repositório (`source venv/bin/activate`).
   - Execute `python -m agente_tarefas` para iniciar a sessão.

2. **Ciclo de três rodadas**
   - **Rodada 1:** o CLI coleta tarefas separadas por vírgula e envia o prompt `build_round1_prompt` ao modelo.
   - **Rodada 2:** o usuário escolhe o número da tarefa concluída. O estado é atualizado e enviado via `build_round2_prompt`.
   - **Rodada 3:** novas tarefas opcionais são inseridas. Duplicatas geram confirmações que alimentam o resumo (`build_round3_prompt`).

3. **State & Logs**
   - O grafo usa `AgentState` definido em `state.py` com `messages`, `tasks`, `completed_ids` e `timeline`.
   - Entradas de timeline são gravadas em memória e podem ser exportadas para `logs/` conforme necessidade.

4. **Testes**
   - Rode `pytest agente_tarefas/tests` para validar utilitários (`rounds`, `graph`, `cli`).

5. **Suporte**
   - Ajuste prompts em `utils/prompts.py` mantendo o tom e as três rodadas.
   - Para instrumentação adicional, adicione middleware ao builder em `graph.py`.
