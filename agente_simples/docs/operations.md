# Guia de Operações do Agente Simples

## 1. Preparação do Ambiente
- Garanta Python 3.12 ativo e ambiente virtual carregado (`source venv/bin/activate`).
- Copie o arquivo `agente_simples/.env.example` para `agente_simples/.env` e preencha:
  - `GEMINI_API_KEY` com a credencial válida.
  - Ajuste opcional de `GEMINI_MODEL`, `GEMINI_TEMPERATURE`, `AGENT_TIMEOUT_SECONDS`, `AGENT_LOCALE`.
- Opcional: defina `AGENTE_SIMPLES_LOG_DIR` para alterar o diretório onde os logs são escritos.

## 2. Execução Padrão
1. No diretório raiz do repositório, execute:
   ```bash
   python -m agente_simples
   ```
2. Responda ao prompt com uma pergunta em português (mínimo 5 caracteres).
3. Receba a resposta formatada no terminal.

## 3. Diagnóstico de Configuração
- O agente executa verificações antes de invocar o modelo:
  - Falhas (`result = fail`) interrompem a execução e exibem instruções de correção, como ausência do `GEMINI_API_KEY`.
  - Alertas (`result = warn`) são exibidos no terminal mas não impedem a execução (ex.: timeout muito baixo, temperatura fora do intervalo).

## 4. Logs e Auditoria
- Logs são gravados em `agente_simples/logs/agent.log` por padrão.
- Cada execução registra: pergunta original, status final (`completed` ou `error`) e duração aproximada.
- Para alterar o diretório de logs, defina `AGENTE_SIMPLES_LOG_DIR` antes de rodar o agente.
- Em caso de erro, procure entradas com `Execução concluída com erro controlado` para obter o contexto.

## 5. Testes de Verificação
- Execute a suíte dedicada:
  ```bash
  pytest agente_simples/tests -v
  ```
- Casos cobertos:
  - Validação dos nodes (`test_nodes.py`).
  - Fluxo do grafo, incluindo falha do provedor (`test_graph.py`).
  - Interações da CLI, incluindo pré-checagens e logging (`test_cli.py`).

## 6. Troubleshooting Rápido
| Sintoma | Ação recomendada |
|---------|------------------|
| Mensagem “Configure GEMINI_API_KEY…” | Confirme o conteúdo do arquivo `.env` e tente novamente. |
| Resposta “Enfrentei um problema ao acessar o modelo…” | Verifique conectividade, limites de uso da API ou credenciais expiradas. |
| Log não gerado | Confirme permissões do diretório `logs/` ou ajuste `AGENTE_SIMPLES_LOG_DIR` para um caminho acessível. |
| Perguntas curtas rejeitadas | Forneça perguntas com contexto (≥ 5 caracteres). |

## 7. Próximos Passos
- Avaliar integração com LangSmith ou LangGraph Studio para auditoria avançada.
- Automatizar execução diária da suíte de testes para garantir estabilidade.
## 8. Validação Rápida
- Ambiente virtual ativo e `.env.example` preenchido conforme seção 1.
- Suíte de testes executada com `pytest agente_simples/tests -v` (todas as verificações passaram).
- Execução manual do CLI validada via testes simulando entradas e capturas de log.

