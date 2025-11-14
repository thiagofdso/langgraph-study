# Quickstart - Agente Perguntas

Siga este roteiro para configurar o ambiente local, validar o fluxo demo e executar perguntas individuais.

## 1. Preparar ambiente
```bash
cd /root/code/langgraph
source venv/bin/activate
pip install -r requirements.txt
cp agente_perguntas/.env.example agente_perguntas/.env
```
Edite `agente_perguntas/.env` e informe `GEMINI_API_KEY`. Ajuste, se necessário, `GEMINI_MODEL`, `GEMINI_TEMPERATURE`, `AGENTE_PERGUNTAS_CONFIDENCE` e `AGENTE_PERGUNTAS_LOG_DIR`.

## 2. Executar fluxo demonstrativo
```bash
python -m agente_perguntas
```
- São executadas 3 perguntas predefinidas.
- Perguntas respondidas automaticamente mostram `status=respondido automaticamente`.
- Perguntas fora do FAQ acionam o bloco **Encaminhar para humano** e exigem mensagem/notas do especialista.

## 3. Executar pergunta única
```bash
python -m agente_perguntas --pergunta "Vocês oferecem suporte 24 horas?"
```
- O CLI indicará se foi respondido pelo FAQ ou escalado.
- Use `--thread-id <id>` para depurar sessões repetidas.

## 4. Verificar logs
```bash
ls -1 ${AGENTE_PERGUNTAS_LOG_DIR:-agente_perguntas/logs}
```
Cada execução cria/atualiza `agent.log` com entradas JSON estruturadas. Abra o arquivo para confirmar os campos `question`, `status`, `confidence` e `notes`.

## 5. Rodar testes automatizados
```bash
pytest agente_perguntas/tests -v
```
A suíte cobre utilitários de similaridade, grafo e CLI. Inclua-a no fluxo de validação antes de abrir PRs.

## Validações recentes

| Data (UTC-3) | Escopo | Notas |
| --- | --- | --- |
| 2025-11-10 | `python -m agente_perguntas --pergunta "Como altero minha senha?"` e `pytest agente_perguntas/tests -v` | Validado com `GEMINI_API_KEY` fictício (`dummy`). CLI respondeu automaticamente e a suíte reportou `7 passed`. |
