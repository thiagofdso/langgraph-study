# Panorama dos Projetos de Agentes

Visão geral dos projetos localizados nos diretórios `agente_*`, `multi_agentes_*` e `pdf_to_md`, detalhando a funcionalidade de cada um e a abordagem técnica utilizada para cumpri-la.

## agente_simples
- **Objetivo funcional**: responder a uma pergunta digitada pelo usuário com uma única chamada ao modelo.
- **Abordagem técnica**: define um `StateGraph` minimalista com um único nó `agent` que invoca o `ChatGoogleGenerativeAI` (modelo `gemini-2.5-flash`) e retorna o texto produzido diretamente ao usuário.

## agente_memoria
- **Objetivo funcional**: demonstrar uma conversa curta onde o agente lembra do que foi dito anteriormente para resolver instruções encadeadas.
- **Abordagem técnica**: usa um `StateGraph` que acumula mensagens via `add_messages` e persiste o histórico com `InMemorySaver`, permitindo que o Gemini responda levando em conta perguntas e respostas anteriores.

## agente_tool
- **Objetivo funcional**: ensinar o agente a responder perguntas textuais e acionar uma calculadora quando detectar solicitação matemática.
- **Abordagem técnica**: combina um nó LLM com um `ToolNode` do LangGraph; o Gemini é configurado com tool calling e, quando gera uma chamada de ferramenta, o fluxo direciona para a calculadora (implementada com `eval`) antes de voltar ao modelo.

## agente_web
- **Objetivo funcional**: executar uma pesquisa na web sobre um tema fixo, sintetizar os achados e registrar um relatório local.
- **Abordagem técnica**: constrói um grafo sequencial (`buscar` → `resumir`) onde Tavily (`TavilySearch`) obtém até cinco resultados e o Gemini gera um resumo curto e referências; warnings e fontes são salvos e também escritos em `smoke_test_output.txt`.

## agente_imagem
- **Objetivo funcional**: transformar um mapa mental em imagem para uma estrutura em Markdown.
- **Abordagem técnica**: em três nós valida a imagem com Pillow, converte para Base64 (utilitário próprio) e envia ao Gemini em formato multimodal; a resposta é analisada para produzir o Markdown final ou sinalizar erro.

## agente_pdf
- **Objetivo funcional**: responder a uma pergunta específica com base em um PDF técnico do OpenShift, exibindo a resposta em Markdown.
- **Abordagem técnica**: carrega o PDF com `PyPDFLoader`, concatena o conteúdo relevante e faz uma invocação ao Gemini com temperatura baixa, armazenando a resposta como campo `markdown_output` no estado.

## agente_banco_dados
- **Objetivo funcional**: gerar um relatório de vendas usando apenas dados de um banco SQLite local.
- **Abordagem técnica**: inicializa o banco com `db_init`, consulta agregações no módulo `reporting` (SQL puro) e executa um grafo simples que coleta métricas e monta um relatório Markdown com tabelas formatadas manualmente.

## agente_perguntas
- **Objetivo funcional**: atuar como atendente FAQ, respondendo automaticamente quando a similaridade com o FAQ for alta ou escalando para humano quando não for.
- **Abordagem técnica**: mantém o FAQ embutido em prompt, calcula similaridade tokenizada, e roda um grafo com nó único que pode interromper via `interrupt`; após resposta humana, retoma o fluxo com `Command.resume`, registrando confiança e status.

## agente_mcp
- **Objetivo funcional**: integrar um agente LangGraph a servidores MCP (matemática e clima), demonstrando execução de ferramentas externas.
- **Abordagem técnica**: utiliza `MultiServerMCPClient` para descobrir ferramentas, vincula o Gemini com `bind_tools` e executa um grafo assíncrono; o nó `BasicToolNode` trata `tool_calls` emitindo `ToolMessage`, enquanto o fluxo é consumido com `graph.astream` para exibir respostas parciais.

## agente_tarefas
- **Objetivo funcional**: conduzir o usuário em três rodadas no terminal para registrar tarefas, concluir uma atividade e adicionar novas antes do encerramento.
- **Abordagem técnica**: organiza prompts síncronos no CLI, gera mensagens de contexto específicas para cada rodada e usa `StateGraph` com `InMemorySaver` para persistir tarefas, itens concluídos e timeline; o Gemini produz confirmações e o resumo final em português.

## multi_agentes_orquestracao
- **Objetivo funcional**: exemplificar um orquestrador que planeja um relatório e coordena múltiplos trabalhadores para escrever seções em paralelo.
- **Abordagem técnica**: obtém a estrutura do relatório via `with_structured_output`, cria workers com `Send` para cada seção e usa o Gemini para redigir conteúdo; o nó `synthesizer` concatena as seções em um relatório Markdown.

## multi_agentes_paralelo
- **Objetivo funcional**: gerar simultaneamente piada, história e poema sobre um tema e apresentar tudo em um texto combinado.
- **Abordagem técnica**: dispara três nós independentes a partir do `START`, cada um invocando o Gemini com instruções diferentes; o nó `aggregator` consolida as três saídas em uma única string.

## multi_agentes_roteador
- **Objetivo funcional**: roteador de personas que define se a resposta deve ter tom informal ou formal com base na idade informada pelo usuário.
- **Abordagem técnica**: o nó `router` analisa a idade na primeira mensagem, decide entre `informal_agent` e `formal_agent`, e cada persona é um pipeline `ChatPromptTemplate` + Gemini adaptando estilo; o grafo usa `InMemorySaver` para manter o contexto da conversa.

## multi_agentes_sequencial
- **Objetivo funcional**: executar um pipeline em duas fases para gerar uma descrição de persona e depois convertê-la para JSON estruturado.
- **Abordagem técnica**: o primeiro nó pede ao Gemini um texto com atributos da persona e o segundo solicita a conversão para JSON, retornando o resultado final como mensagem ao usuário.

## pdf_to_md
- **Objetivo funcional**: converter o PDF fixo `openshift_container_platform-4.9-distributed_tracing-en-us.pdf` para um arquivo Markdown local.
- **Abordagem técnica**: script independente que usa `docling.document_converter.DocumentConverter` para ler o PDF, exporta o conteúdo em Markdown e grava o resultado em `pdf_to_md/`, com verificações básicas de existência do arquivo.

## agente_reflexao_basica
- **Objetivo funcional**: entregar uma resposta refinada para a pergunta fixa “O que é importante para um programador aprender”, registrando cada crítica e rascunho gerados durante o processo.
- **Abordagem técnica**: `StateGraph` com nós `generate` e `reflect`, contador de iterações no estado e checkpoint em memória; prompts dedicados instruem o Gemini (`gemini-2.5-flash`) a gerar rascunhos e críticas em JSON com pelo menos quatro prioridades de aprendizagem.

## agente_codigo
- **Objetivo funcional**: gerar um script didático sobre estruturas de dados, executá-lo em memória para validar o resultado e iterar até obter sucesso ou atingir cinco tentativas.
- **Abordagem técnica**: o agente monta um `StateGraph` com nós de geração, execução, decisão e reflexão; usa `gemini-2.5-flash` apenas nos nós criativos, executa o código com `exec` capturando stdout/stderr e mantém todo o processo em memória, imprimindo o código final no console.

## agente_reflexao_web
- **Objetivo funcional**: responder "Como funciona o Google Agent Development Kit?" entregando um texto final em português apoiado por evidências coletadas na web.
- **Abordagem técnica**: combina três nós (`gerar_resposta`, `decidir_fluxo`, `refletir_com_evidencias`) em um `StateGraph`. O nó de reflexão consulta o Tavily para buscar fontes, enquanto o Gemini produz rascunhos e críticas sequenciais. Cada iteração reaproveita o histórico em memória (`InMemorySaver`) e, ao final, as citações são substituídas pelos próprios URLs relevantes.

## agente_aprovacao
- **Objetivo funcional**: controlar a execução de ferramentas externas exigindo aprovação humana, validando a entrada do usuário e garantindo resposta mesmo quando a pesquisa for negada.
- **Abordagem técnica**: implementa todo o fluxo em `agente_aprovacao/main.py` com um `StateGraph` que valida a solicitação, usa `interrupt` para coletar correções e decisões humanas, consulta Tavily somente após autorização via tool dedicada e gera a resposta final com Gemini (`gemini-2.5-flash`). Expressões matemáticas simples são resolvidas localmente sem acionar ferramentas externas, e a execução encerra após a segunda passagem pelo nó de geração.
