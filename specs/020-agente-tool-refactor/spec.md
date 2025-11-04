# Feature Specification: Refatorar agente_tool

**Feature Branch**: `020-agente-tool-refactor`  
**Created**: 2025-11-04  
**Status**: Draft  
**Input**: User description: "Quero que o projeto agente_tool seja refatorado usando boas praticas de python e e organizacao de projetos langgraph conforme o arquivo langgraph-tasks sem perder a essencia original do projeto."

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

### User Story 1 - Estrutura modular consistente (Priority: P1)

Como desenvolvedor que mantém múltiplos agentes LangGraph, quero que `agente_tool` siga a mesma estrutura modular e padrões de nomenclatura dos demais projetos para conseguir navegar e evoluir o código rapidamente.

**Why this priority**: Sem uma estrutura alinhada, o time perde tempo entendendo layouts diferentes e aumenta o risco de regressões ao reutilizar componentes.

**Independent Test**: Abrir o projeto `agente_tool`, localizar arquivos `graph.py`, `state.py`, `config.py`, `utils/nodes.py`, `utils/tools.py` e confirmar que expõem as mesmas fábricas e funções documentadas em `graph-nodes-patterns.md`.

**Acceptance Scenarios**:

1. **Given** o repositório atualizado, **When** o desenvolvedor importa `agente_tool.graph.create_app`, **Then** recebe uma instância compilada equivalente aos outros agentes.
2. **Given** a necessidade de analisar nodes, **When** o desenvolvedor consulta `graph-nodes-patterns.md`, **Then** encontra entradas para cada node usado por `agente_tool` sem lacunas.

---

### User Story 2 - Fluxo funcional preservado (Priority: P2)

Como analista funcional, quero confirmar que o agente continua respondendo perguntas matemáticas e delegando ao cálculo quando necessário, garantindo que a refatoração não alterou o comportamento esperado.

**Why this priority**: A essência do projeto é oferecer respostas precisas com suporte à ferramenta calculadora; perder essa capacidade invalida a refatoração.

**Independent Test**: Executar o fluxo demonstrativo com a pergunta “quanto é 300 dividido por 4?” e verificar que a resposta final mantém o formato “Resposta do agente: 75”.

**Acceptance Scenarios**:

1. **Given** uma entrada que exige uso de ferramenta, **When** o agente processa a mensagem, **Then** a execução inclui a ferramenta calculadora e retorna o resultado correto.
2. **Given** uma entrada inválida, **When** o agente valida a pergunta, **Then** responde com mensagem de erro orientando o usuário a fornecer mais detalhes.

---

### User Story 3 - Observabilidade e qualidade asseguradas (Priority: P3)

Como líder técnico, quero ver documentação, logs e testes automatizados que demonstrem o fluxo do `agente_tool`, para confiar na manutenção contínua e facilitar auditorias futuras.

**Why this priority**: Documentação e testes reduzem risco operacional e aceleram onboarding de novos integrantes.

**Independent Test**: Revisar `agente_tool/docs/` para encontrar baseline e arquitetura atualizada, executar a suíte de testes dedicados e confirmar que logs registram as etapas principais.

**Acceptance Scenarios**:

1. **Given** o repositório refatorado, **When** a suíte de testes do `agente_tool` é executada, **Then** todos os testes passam e cobrem validação, uso da ferramenta e formatação da resposta.
2. **Given** o pipeline de observabilidade, **When** o agente roda com logging em modo informativo, **Then** cada etapa (`validate_input`, `plan_tool_usage`, `execute_tools`, `invoke_model`, `format_response`) registra mensagens claras de início e término.

### Edge Cases

- Variável de ambiente `GEMINI_API_KEY` ausente ou inválida ao inicializar o agente.
- Expressão enviada à calculadora com sintaxe incorreta ou tentativa de injeção de código.
- Usuário envia pergunta muito curta ou sem contexto suficiente para decidir pelo uso da ferramenta.
- Falha temporária da API do modelo durante a invocação principal.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-020**: O projeto `agente_tool` MUST adotar estrutura modular equivalente a `agente_simples` e `agente_memoria`, disponibilizando arquivos dedicados para estado, configuração, nodes, ferramentas, grafo e CLI.
- **FR-021**: O agente MUST expor nodes nomeados conforme `graph-nodes-patterns.md`, reutilizando padrões existentes e registrando novas responsabilidades relacionadas a ferramentas no catálogo.
- **FR-022**: O fluxo MUST preservar o comportamento original de responder perguntas matemáticas, incluindo delegação segura para a calculadora e formatação final da resposta.
- **FR-023**: O catálogo `graph-nodes-patterns.md` MUST ser atualizado para refletir quaisquer novos nodes ou responsabilidades introduzidas pelo `agente_tool`.
- **FR-024**: O projeto MUST fornecer documentação operacional (baseline e arquitetura) e testes automatizados cobrindo validação de entrada, execução da ferramenta e resposta final.
- **FR-025**: O agente MUST registrar logs informativos nas etapas-chave do fluxo para suportar depuração e auditoria.

### Key Entities *(include if feature involves data)*

- **Fluxo do agente**: Representa o workflow que valida perguntas, decide uso de ferramentas, aciona o modelo e formata respostas. Requer rastrear mensagens, status e metadados de ferramentas.
- **Ferramenta calculadora**: Função especializada em avaliar expressões matemáticas, devendo registrar nome da ferramenta, argumentos recebidos e resultado devolvido para auditoria.
- **Catálogo de nodes**: Documento compartilhado que lista padrões de nomenclatura e responsabilidades de nodes LangGraph reutilizados entre projetos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Revisão cruzada confirma que 100% dos nodes usados por `agente_tool` estão documentados no `graph-nodes-patterns.md` com responsabilidades atualizadas.
- **SC-002**: Execução do cenário demonstrativo “quanto é 300 dividido por 4?” retorna resposta correta e com o mesmo formato observado antes da refatoração.
- **SC-003**: Suite de testes automatizados dedicada ao `agente_tool` atinge cobertura mínima de todas as funções determinísticas e roda sem falhas em ambiente de integração contínua.
- **SC-004**: Desenvolvedor recém-chegado consegue configurar variáveis, executar o agente via CLI e compreender o fluxo em menos de 10 minutos a partir da documentação fornecida (validado em sessão piloto).
