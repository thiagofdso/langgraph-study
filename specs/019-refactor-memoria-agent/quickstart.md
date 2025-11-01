# Quickstart: agente_memoria Refatorado

## Pré-requisitos
- Python 3.12.3 ativo no virtualenv `venv/`
- Variável `GEMINI_API_KEY` disponível (arquivo `.env` em `agente_memoria/`)
- Dependências instaladas via `pip install -r requirements.txt`

## Passos de Desenvolvimento
1. **Configurar ambiente**
   ```bash
   cp agente_simples/.env.example agente_memoria/.env
   # edite GEMINI_API_KEY e demais parâmetros necessários
   ```
2. **Executar pré-checagem**
   ```bash
   python -m agente_memoria.cli --check
   ```
   - Saída "pass" → pronto para execução
   - Saída "fail" → seguir mensagem orientativa
3. **Rodar o agente**
   ```bash
   python -m agente_memoria --thread conversa-demo
   # ou: python agente_memoria/main.py --thread conversa-demo
   ```
   - Comandos disponíveis na CLI: `/reset`, `/thread novo-id`, `/sair`
4. **Inspecionar logs**
   - Arquivos em `agente_memoria/logs/agent.log`
   - Contêm `thread_id`, pergunta, status, duração
5. **Executar testes**
   ```bash
   pytest agente_memoria/tests -v
   ```
   - `test_nodes.py` cobre validações e chamadas ao modelo
   - `test_graph.py` verifica memória multi-turno e reset
6. **Visualizar grafo (opcional)**
   ```bash
   langgraph dev --graph agente_memoria/graph.py:app
   ```

## Fluxo de Trabalho Sugerido
- Ajustar configuração → rodar pré-checagem → executar conversa → revisar logs → rodar testes
- Documentar alterações adicionais em `agente_memoria/docs/operations.md`
