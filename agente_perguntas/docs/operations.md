# Guia Operacional - Agente Perguntas

Este documento consolida processos de operação, escalonamento humano (HITL) e troubleshooting para o agente `agente_perguntas`.

## Fluxo de escalonamento humano (HITL)

1. Execute o agente (`python -m agente_perguntas` ou `--pergunta`).
2. Quando a similaridade ficar abaixo de `AGENTE_PERGUNTAS_CONFIDENCE`, o CLI exibirá o bloco **Encaminhar para humano** com:
   - Pergunta original
   - Melhor correspondência do FAQ e a confiança calculada
3. Forneça a resposta que será enviada ao usuário (Enter usa o texto padrão `ESCALATION_MESSAGE`).
4. Registre notas internas (Enter usa `Encaminhamento registrado manualmente.`).
5. O grafo é retomado automaticamente via `resume_with_human_response` e o resumo final mostra a pergunta como `encaminhar para humano` com as notas digitadas.

## Logs e auditoria

- Todos os atendimentos são registrados no diretório configurado por `AGENTE_PERGUNTAS_LOG_DIR` (padrão `agente_perguntas/logs`).
- Cada entrada JSON contém `question`, `status`, `confidence`, `notes`, `mode` (`demo` ou `single`) e um trecho da resposta.
- Para auditorias, filtre por `status="encaminhar para humano"` e revisite as notas coletadas manualmente.

## Atualização do FAQ

1. Edite `agente_perguntas/utils/prompts.py` e atualize a lista `FAQ_ENTRIES`.
2. Garanta que perguntas e respostas estejam normalizadas (função `_normalize`).
3. Rode `python -m agente_perguntas --pergunta "<nova pergunta>"` para validar.
4. Registre mudanças relevantes em `docs/operations.md` ou `README.md` quando afetarem o fluxo.

## Troubleshooting rápido

| Sintoma | Ação recomendada |
| --- | --- |
| `RuntimeError: GEMINI_API_KEY não configurado` | Confirme se `agente_perguntas/.env` existe e contém a chave. Recarregue o ambiente (`source venv/bin/activate`) e exporte `GEMINI_API_KEY` se necessário. |
| Modelo indisponível / latência alta | Verifique status da API Gemini. Ajuste `GEMINI_MODEL` para uma versão estável e reduza `GEMINI_TEMPERATURE` para 0.0 se respostas estiverem inconsistentes. |
| Diretório de logs não criado | Garanta que `AGENTE_PERGUNTAS_LOG_DIR` aponta para um caminho gravável. O `AppConfig.load()` cria o diretório automaticamente, mas permissões incorretas podem impedir a operação. |

## Procedimento de validação pós-deploy

1. Copie `.env.example`, preencha as variáveis e execute `python -m agente_perguntas` (modo demo).
2. Rode uma pergunta fora do FAQ para validar o fluxo HITL e confirme que o arquivo de log recebeu o registro com `status="encaminhar para humano"`.
3. Execute `pytest agente_perguntas/tests -v` para garantir regressão zero (resultado esperado: `7 passed`).
4. Atualize este documento com qualquer incidente ou lição aprendida.

## QA automatizado

1. Ative o ambiente virtual e garanta que `GEMINI_API_KEY` esteja definido (valor fictício funciona nos testes).
2. Rode:
   ```bash
   pytest agente_perguntas/tests -v
   ```
3. Verifique que todos os testes passem (`7 passed`). Os principais alvos:
   - `test_similarity.py`: normalização e ranking do FAQ.
   - `test_graph.py`: respostas automáticas e retomada HITL.
   - `test_cli.py`: logging estruturado e prompts HITL no CLI.
