# Baseline – agente_tool (pré-refatoração)

## Contexto

- Data da captura: 2025-11-04
- Comando executado a partir da raiz do repositório:

```bash
python agente_tool/main.py
```

## Saída observada

```
User: quanto é 300 dividido por 4?
Agent: Para calcular 300 dividido por 4, podemos fazer a seguinte operação:

300 ÷ 4 = 75

Então, 300 dividido por 4 é **75**.
```

## Notas

- O fluxo atual utiliza diretamente `main.py`, instanciando o modelo Gemini na importação.
- A ferramenta `calculator` é chamada implicitamente através do grafo atual (LangGraph).
- Não há logs estruturados além do `print` final da resposta.

---

# Baseline – agente_tool (pós-refatoração)

## Contexto

- Data da captura: 2025-11-04
- Comando executado a partir da raiz do repositório:

```bash
python -m agente_tool run "quanto é 300 dividido por 4?"
```

## Saída observada

```
2025-11-03 23:57:27,180 INFO agente_tool.utils.nodes Pergunta validada
2025-11-03 23:57:27,181 INFO agente_tool.utils.nodes Plano de ferramenta criado
2025-11-03 23:57:27,184 INFO agente_tool.utils.nodes Ferramenta executada com sucesso
2025-11-03 23:57:29,221 INFO agente_tool.utils.nodes Resposta obtida do modelo.
2025-11-03 23:57:29,224 INFO agente_tool.utils.nodes Fluxo concluído com sucesso.
2025-11-03 23:57:29,226 INFO agente_tool.cli Execução concluída | pergunta='quanto é 300 dividido por 4?' status=completed duration=2.04s
Resposta do agente: 300 dividido por 4 é **75**.
```

## Notas

- A CLI executa pré-checagens de configuração e registra logs no console e em `agente_tool/logs/agent.log`.
- O modelo decide quando chamar a ferramenta `calculator`; após a execução, o resultado é devolvido ao LLM para gerar a resposta final.
- A formatação final preserva o prefixo `Resposta do agente:` e registra `duration_seconds` no estado retornado.
- Executar `python -m agente_tool` sem argumentos abre o fluxo interativo para inserir a pergunta no terminal.
