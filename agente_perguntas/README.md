# Agente Perguntas

Projeto de estudo: agente em LangGraph que responde perguntas frequentes a partir de um FAQ embutido no prompt e encaminha dúvidas desconhecidas para atendimento humano.

## Execução rápida
```bash
python agente_perguntas/main.py
```
O script executará três perguntas demonstrativas (duas respondidas pelo FAQ, uma escalada). Quando a dúvida não estiver no FAQ, o programa solicitará via console a resposta e as notas do especialista; pressione Enter para usar o texto padrão.

## Pré-requisitos
- Ativar o ambiente virtual `venv/`
- Configurar `GEMINI_API_KEY` no arquivo `.env`

## Interação humana
Quando o agente não encontra uma resposta no FAQ, ele:
1. Mostra o bloco “Encaminhar para humano” com a melhor correspondência encontrada.
2. Solicita no console a mensagem que deve ser enviada ao usuário (ou Enter para usar o texto padrão).
3. Permite registrar notas internas sobre o encaminhamento.

Assim que as entradas forem fornecidas, o fluxo continua e o resumo final exibirá a pergunta como “encaminhar para humano” com as notas digitadas.
