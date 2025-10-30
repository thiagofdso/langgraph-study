# Quickstart – Terminal Task Session Agent

## Pré-requisitos
- Python 3.12.3 utilizando o virtualenv do repositório (`source venv/bin/activate`).
- Variáveis de ambiente configuradas: copie `agente_simples/.env` para `agente_tarefas/.env` e defina `GEMINI_API_KEY` válido.
- Dependências instaladas via `pip install -r requirements.txt` (já cobre langgraph e google-generativeai).

## Passo a passo

1. **Criar a pasta do agente**
   ```bash
   mkdir -p agente_tarefas
   cp agente_simples/.env agente_tarefas/.env
   touch agente_tarefas/__init__.py
   ```

2. **Executar o agente**
   ```bash
   PYTHONPATH=. python agente_tarefas/main.py
   ```

3. **Conduzir as três interações**
   - **Rodada 1**: Digite uma lista de tarefas separadas por vírgula ou novas linhas; o terminal exibirá "Usuário:" seguido da entrada e "Agente:" com a lista numerada.
   - **Rodada 2**: Informe o número da tarefa concluída (ex.: `2`); a resposta confirmará a conclusão e mostrará o estado atualizado.
   - **Rodada 3**: Adicione novas tarefas (ou pressione Enter e confirme que não há novas); o agente retornará o resumo final com contagens e orientação para reiniciar.

4. **Reiniciar a sessão**
   - Para outro exercício, execute novamente o script. Cada execução utiliza um novo `thread_id` configurado no código para manter isoladas as conversas.

## Observações
- Não há loop contínuo: o script encerra automaticamente após exibir o resumo da rodada 3.
- Todas as mensagens são apresentadas em português, incluindo os ecos de entrada do usuário e as respostas do agente.
- Caso o LLM retorne erro, o script deve mostrar mensagem amigável e finalizar a sessão indicando como tentar novamente.
