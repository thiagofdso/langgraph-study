# Feature Specification: Refatorar agente_mcp

**Feature Branch**: `001-refactor-agente-mcp`  
**Created**: 2025-11-18  
**Status**: Draft  
**Input**: User description: "Refatore o projeto agente_mcp seguindo boas práticas de python e de organização de projetos langgraph."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Operar agente multi-servidor via CLI única (Priority: P1)

Uma pessoa desenvolvedora precisa executar o agente para verificar respostas combinando servidores de matemática e clima (e futuros servidores) usando um único comando que valida configuração, sobe dependências necessárias e imprime o diálogo completo.

**Why this priority**: Sem uma experiência de execução previsível, não há como validar se a refatoração preservou o comportamento funcional, bloqueando qualquer entrega.

**Independent Test**: Executar o comando oficial documentado após configurar credenciais e servidores simulados; o fluxo deve iniciar, orquestrar tool-calls e finalizar sem ajustes manuais.

**Acceptance Scenarios**:

1. **Given** uma estação com variáveis obrigatórias configuradas, **When** a CLI for invocada com perguntas padrão, **Then** o agente deve chamar os servidores registrados e imprimir cada resposta em ordem cronológica.
2. **Given** que um servidor esteja declarado como “auto-start”, **When** a CLI iniciar, **Then** o processo correspondente deve ser inicializado, monitorado e encerrado ao término da sessão sem intervenção manual.

---

### User Story 2 - Adicionar novo servidor MCP sem retrabalho estrutural (Priority: P2)

Uma pessoa mantenedora precisa conectar um novo servidor MCP (ex.: calculadora científica) declarando apenas parâmetros de transporte, comando/URL e descrições, sem copiar código existente ou editar o grafo.

**Why this priority**: Extensibilidade é o principal motivo para alinhar o projeto ao padrão LangGraph; se novos servidores exigirem refatorações adicionais, o objetivo não é atingido.

**Independent Test**: Criar um stub de servidor conforme o guia, registrá-lo via arquivo/config declarado e executar testes automatizados; o novo servidor deve aparecer como ferramenta disponível e responder a uma pergunta direcionada.

**Acceptance Scenarios**:

1. **Given** um arquivo de configuração contendo definições de servidores ativos, **When** uma nova entrada é adicionada, **Then** o agente deve listar e utilizar a ferramenta sem mudanças adicionais no código do grafo.
2. **Given** a remoção temporária de um servidor do arquivo de configuração, **When** a CLI é executada, **Then** o grafo não deve tentar invocá-lo nem falhar por ausência.

---

### Edge Cases

- Servidor MCP indisponível durante a sessão: a CLI deve registrar o erro, retornar mensagem amigável ao usuário e continuar com demais servidores.
- Variáveis do `.env` ausentes ou vazias: o agente deve abortar antes de iniciar o grafo e listar quais valores precisam ser definidos.
- Tool-call retornando payload inválido (JSON malformado, campos faltando): o grafo deve capturar o erro, gerar mensagem humanizada e registrar detalhes para diagnóstico.
- Conflito de nomes de ferramentas entre servidores: a configuração precisa recusar o arranque e instruir o mantenedor a ajustar os identificadores.
- Execução paralela com `thread_id` distintos: sessões simultâneas não podem compartilhar estado ou logs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O projeto deve ser reorganizado em módulos explícitos (`config`, `state`, `graph`, `cli`, `mcp_servers`, `tests`, `docs`) seguindo o padrão aplicado aos demais agentes descritos em `PROJETOS.md`.
- **FR-002**: A CLI oficial deve validar a configuração (env, disponibilidade de binários/URLs) antes de iniciar o grafo e interromper com mensagem clara quando um requisito não for atendido.
- **FR-003**: A CLI deve permitir executar uma sessão completa informando pergunta(s) via CLI ou argumento, imprimindo mensagens do usuário e do assistente em ordem cronológica.
- **FR-004**: O grafo deve separar responsabilidades em nós especializados (ex.: validar entrada, invocar LLM com ferramentas, planejar/execução de ferramentas, formatar resposta) permitindo reuso e testes de cada etapa.
- **FR-005**: Deve haver um mecanismo declarativo para cadastrar servidores MCP (arquivo de configuração ou objeto dedicado) contendo nome, transporte, parâmetros de inicialização e flags de auto-start/externo.
- **FR-006**: O código deve capturar e registrar exceções provenientes dos servidores MCP ou do LLM, retornando mensagens inteligíveis ao usuário final sem stack traces crus.
- **FR-007**: A documentação do projeto (README e comentários essenciais) deve explicar a nova estrutura, requisitos de execução, como adicionar/retirar servidores e como rodar testes.
- **FR-008**: Logs gerados durante a execução devem seguir formato consistente (timestamp + nível + contexto) e registrar principais eventos: validação, inicialização de servidores, tool-calls, resultados e falhas.

### Key Entities *(include if feature involves data)*

- **Sessão do Agente**: Representa o ciclo de perguntas e respostas; atributos incluem `thread_id`, lista ordenada de mensagens e metadados como duração e status final. Não armazena detalhes do provedor.
- **Perfil de Servidor MCP**: Conjunto de parâmetros que descrevem um servidor disponível (nome, tipo de transporte, endpoint/comando, política de inicialização, credenciais requeridas). Utilizado para construir o cliente multi-servidor.
- **Configuração de Execução**: Estrutura que agrega variáveis de ambiente, caminho de logs, opções de CLI (pergunta interativa vs. argumento) e limites operacionais (tempo máximo por tool-call).

## Assumptions

- O provedor de LLM permanece sendo Gemini 2.5 (conforme demais agentes) e já possui chave provisionada no `.env`.
- Servidores MCP locais continuarão simples (math, weather) apenas para demonstração; ambientes reais podem trocá-los sem afetar o fluxo especificado.
- Usuários finais são pessoas desenvolvedoras internas com acesso ao repositório e possibilidade de executar processos locais.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Qualquer pessoa desenvolvedora consegue executar o agente do zero (configurar credenciais, iniciar servidores necessários e rodar CLI) em até 10 minutos seguindo o README atualizado.
- **SC-002**: Adicionar ou remover um servidor MCP documentado deve requerer no máximo a edição de uma única fonte de configuração, e a suíte de regressão deve concluir em menos de 5 minutos com dependências simuladas.
- **SC-003**: Durante uma sessão CLI padrão, 100% dos tool-calls devem gerar logs estruturados contendo timestamp, nome da ferramenta e status (sucesso/falha), permitindo rastreabilidade posterior.
