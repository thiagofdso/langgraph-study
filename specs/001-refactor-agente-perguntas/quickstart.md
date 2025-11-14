# Quickstart: Agente Perguntas Refatorado

1. **Preparar ambiente**
   - Ative o ambiente virtual do repositório:
     ```bash
     source venv/bin/activate
     ```
   - Copie o template de variáveis:
     ```bash
     cp agente_perguntas/.env.example agente_perguntas/.env
     ```
   - Preencha `agente_perguntas/.env` com `GEMINI_API_KEY` e ajuste opcionalmente `GEMINI_MODEL`, `GEMINI_TEMPERATURE`, `AGENTE_PERGUNTAS_CONFIDENCE`, `AGENTE_PERGUNTAS_LOG_DIR`.

2. **Executar o agente (modo demo)**
   ```bash
   python -m agente_perguntas
   ```
   - O CLI exibirá três perguntas demonstrativas.
   - Perguntas identificadas no FAQ retornam resposta automática com confiança.
   - Perguntas desconhecidas abrirão prompts para mensagem e notas do especialista (HITL).

3. **Executar pergunta única**
   ```bash
   python -m agente_perguntas --pergunta "Vocês oferecem suporte 24 horas?"
   ```
   - A saída indicará se a dúvida foi respondida automaticamente ou escalada.
   - Logs estruturados serão gravados no diretório definido em `AGENTE_PERGUNTAS_LOG_DIR` (padrão `agente_perguntas/logs`).

4. **Rodar testes automatizados**
   ```bash
   pytest agente_perguntas/tests -v
   ```
   - Garante cobertura para utilitários de similaridade, nodes do grafo, CLI e cenários HITL com mocks.

5. **Documentação operacional**
   - Consulte `agente_perguntas/docs/operations.md` para procedimentos de atualização do FAQ, troubleshooting de configuração e orientações para escalonamento humano.
