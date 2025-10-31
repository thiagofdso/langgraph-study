# Agente de Reflexão com Evidências Web

Este agente combina LangGraph, Gemini e Tavily para responder à pergunta fixa
"Como funciona o Google Agent Development Kit?" usando o padrão Reflexion com
três nós (geração, decisão e reflexão).

## Estrutura do Fluxo

1. **gerar_resposta** — produz um rascunho inicial (ou revisado) usando apenas o
   modelo Gemini, incorporando orientações existentes e incrementando o contador
   de execuções.
2. **decidir_fluxo** — avalia se o limite de iterações foi atingido, encerrando
   o fluxo quando necessário ou encaminhando para nova reflexão.
3. **refletir_com_evidencias** — pesquisa conteúdo com Tavily, associa cada
   fonte a um identificador `ref-n` e gera críticas estruturadas que guiam a
   próxima versão do rascunho.

## Pré-requisitos

- Python 3.12.3 com `venv` ativado (`source venv/bin/activate`).
- Variáveis `GEMINI_API_KEY` e `TAVILY_API_KEY` definidas em
  `agente_reflexao_web/.env` (cópia direta de `agente_web/.env`).
- Acesso à internet para consultas Tavily e invocações Gemini.

## Execução

```bash
python agente_reflexao_web/main.py
```

A execução imprime:
- Resposta final com URLs das fontes diretamente no texto.
- Seção de referências correspondentes às evidências utilizadas.
- Histórico completo das iterações (rascunhos e reflexões), útil para auditoria.
- Avisos sobre limitações (ex.: falta de evidências ou limite de iterações).

## Teste Manual

Execute o script com as credenciais válidas. O fluxo encerra automaticamente
após no máximo três reflexões. Caso as credenciais não estejam configuradas, o
script encerra informando a ausência de chaves.
