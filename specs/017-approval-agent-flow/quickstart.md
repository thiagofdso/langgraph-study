# Quickstart — Agente com Aprovação Humana

## Pré-requisitos
- Python 3.12.3 utilizando o `venv` do repositório (`source venv/bin/activate`).
- Copie `agente_web/.env` para `agente_aprovacao/.env` sem alterações.
- Configure chaves `GEMINI_API_KEY` e `TAVILY_API_KEY` no `.env` copiado (não editar após a cópia).
- Acesso à internet para executar a ferramenta de pesquisa.

## Passo a passo
1. Ative o ambiente virtual e garanta dependências instaladas (`pip install -r requirements.txt` se necessário).
2. Execute o fluxo manual:
   ```bash
   python agente_aprovacao/main.py
   ```
3. Observe o console:
   - Solicitações para revisar/ajustar os dados quando a validação falhar.
   - Prompts para aprovar ou negar o uso da ferramenta de pesquisa.
   - Mensagem final informando se a resposta usou a ferramenta ou seguiu sem autorização.

## Resultado Esperado
- O script encerra automaticamente após exibir a resposta final (sem loop interativo contínuo).
- Cada tentativa de uso de ferramenta é precedida por confirmação humana.
- Logs indicam quando a resposta foi gerada sem consulta externa por reprovação.

## Resultados de verificação manual — 2025-10-31
- **Cenário aprovação**: Após fornecer uma pergunta válida e autorizar a pesquisa, o fluxo executou Tavily, exibiu a resposta final com referências e registrou a decisão humana como “aprovada”.
- **Cenário validação**: Ao enviar uma pergunta curta (“Oi?”), o agente solicitou correção, aceitou a nova entrada e prosseguiu somente após atingir critérios mínimos.
- **Cenário reprovação**: Negando o uso da pesquisa, o fluxo retornou ao nó inicial, gerou resposta interna sem Tavily e encerrou a sessão com nota “Pesquisa externa não autorizada pelo aprovador.”
- **Cenário expressão matemática**: Informando “1+1”, o agente reconheceu a operação, calculou localmente e entregou a resposta final sem solicitar aprovação humana ou acionar Tavily.
