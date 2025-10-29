# Pesquisa: Como usar Tavily com LangGraph no Python

Fonte: Perplexity (consulta em 2025-10-29)

## Resumo
- Instalar dependências: `pip3 install -U langgraph langchain langchain-tavily python-dotenv`.
- Obter chave de API do Tavily e armazenar em `.env`.
- Criar ambiente virtual opcional com `python3 -m venv .venv`.
- Configurar `TavilySearch` com a chave carregada via `python-dotenv`.
- Construir agente no LangGraph combinando o LLM escolhido e a ferramenta do Tavily.

## Passo a Passo detalhado
1. Verifique instalação de Python e pip (`python3 --version`, `pip3 --version`).
2. Crie conta no Tavily e obtenha a chave API (plano gratuito com limite mensal).
3. Instale bibliotecas necessárias:
   ```bash
   pip3 install -U langgraph langchain langchain-tavily python-dotenv
   ```
4. (Opcional) Crie e ative ambiente virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\\Scripts\\activate  # Windows
   ```
5. Crie um arquivo `.env` com `TAVILY_API_KEY=...`.
6. No script Python:
   ```python
   import os
   from dotenv import load_dotenv
   from langchain import LLMChain, PromptTemplate
   from langchain.agents import initialize_agent
   from langchain.llms import AI21
   from langchain.tools import TavilySearch

   load_dotenv()

   tavily_tool = TavilySearch(api_key=os.getenv("TAVILY_API_KEY"))
   tools = [tavily_tool]
   llm = AI21()
   agent = initialize_agent(llm, tools)

   question = "Qual é a capital do Brasil?"
   response = agent.run(question)
   print(response)
   ```
7. Execute o agente com perguntas para validar a integração.

## Sugestões de pesquisas adicionais
- "Tavily API documentation"
- "LangGraph tutorial with Tavily integration"
- "Python examples for LangGraph and Tavily"

## Referências (Perplexity)
1. https://www.youtube.com/watch?v=JtQEjfzE_Ko
2. https://www.youtube.com/watch?v=LS4pALyrm00
3. https://dev.to/vedantkhairnar/building-your-first-ai-agent-tavily-x-langgraph-8c4
4. https://camelcaseguy.com/tavily-aiagent/
5. https://www.datacamp.com/tutorial/langgraph-agents
6. https://tavily.com
7. https://python.langchain.com/docs/tutorials/agents/
8. https://python.langchain.com/docs/integrations/tools/tavily_search/
9. https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/
10. https://blog.tavily.com/discover-the-power-of-langgraph-my-adventure-in-building-gpt-newspaper/
11. https://www.tavily.com/tutorials
12. https://langchain-ai.github.io/langgraph/concepts/why-langgraph/
13. https://www.tavily.com/tutorials/tavily-101

