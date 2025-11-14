# Feature Specification: Reestruturar Agente Perguntas

**Feature Branch**: `001-refactor-agente-perguntas`  
**Created**: 2025-11-05  
**Status**: Draft  
**Input**: User description: "Quero que o projeto agente_perguntas seja reestruturado seguindo boas práticas de organização de projetos langgraph conforme exemplo do projeto agente_simples."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Operador executa fluxo padronizado (Priority: P1)

Um operador técnico precisa rodar o agente `agente_perguntas` a partir do terminal e receber respostas consistentes do FAQ sem depender de scripts ad hoc.

**Why this priority**: Sem um fluxo de execução padronizado, o agente deixa de entregar valor imediato e não é possível validar se a refatoração preservou a experiência anterior.

**Independent Test**: Executar `python -m agente_perguntas` em um ambiente configurado, enviar uma pergunta coberta pelo FAQ e validar que a resposta é apresentada e registrada nos logs.

**Acceptance Scenarios**:

1. **Given** um ambiente com variáveis configuradas e dependências instaladas, **When** o operador executa `python -m agente_perguntas` e envia uma pergunta contemplada no FAQ, **Then** o agente responde automaticamente, grava o evento no log e encerra sem erros.
2. **Given** o mesmo ambiente, **When** o operador envia uma pergunta fora do FAQ e fornece mensagem/notas no prompt interativo, **Then** o agente integra a resposta manual ao relatório final e sinaliza o status como "encaminhar para humano".

---

### User Story 2 - Pessoa desenvolvedora configura o projeto (Priority: P2)

Uma pessoa desenvolvedora precisa preparar o projeto em uma máquina nova seguindo documentação clara, incluindo variáveis de ambiente, estrutura de arquivos e instruções de execução.

**Why this priority**: A clareza na configuração reduz tempo de onboarding e garante que a reorganização realmente siga o padrão de `agente_simples`.

**Independent Test**: Seguir o README atualizado a partir de um clone limpo e confirmar que o agente roda end-to-end usando as instruções fornecidas.

**Acceptance Scenarios**:

1. **Given** um clone fresco do repositório, **When** a desenvolvedora copia `.env.example`, preenche a chave e executa os comandos listados no README, **Then** o agente roda com sucesso e gera o mesmo fluxo demonstrativo documentado.

---

### User Story 3 - QA valida a refatoração com testes (Priority: P3)

Uma pessoa de QA precisa rodar uma suíte de testes automatizados dedicada ao agente para garantir que os componentes reorganizados funcionam como esperado.

**Why this priority**: Testes asseguram que a refatoração não introduza regressões e que os contratos do agente permaneçam estáveis.

**Independent Test**: Executar `pytest agente_perguntas/tests -v` e confirmar que os testes cobrindo CLI, nós do grafo e manipulação de FAQ passam.

**Acceptance Scenarios**:

1. **Given** o projeto reorganizado com dependências instaladas, **When** a pessoa de QA roda `pytest agente_perguntas/tests`, **Then** todos os testes são aprovados e validam os comportamentos críticos descritos nas histórias P1 e P2.

---

### Edge Cases

- Pergunta recebida com texto vazio ou apenas espaços deve gerar mensagem orientativa ao operador sem quebrar o fluxo.
- Execução sem `GEMINI_API_KEY` (ou variável equivalente) configurada deve interromper o processo com instruções claras de correção.
- Indisponibilidade temporária do provedor de IA deve ser detectada e registrada, retornando orientação para reprocessar ou escalar manualmente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O projeto deve ser reorganizado em um pacote com módulos separados para entrada principal (`__main__`/CLI), configuração, estado, grafo e utilitários (incluindo prompts e funções de similaridade), espelhando o padrão documentado em `agente_simples`.
- **FR-002**: A linha de comando deve permitir executar tanto o fluxo demonstrativo quanto perguntas avulsas, exibindo resultados no terminal e registrando um resumo final por interação.
- **FR-003**: O agente deve validar a configuração antes de iniciar o grafo, incluindo verificação de variáveis obrigatórias, caminho de logs e parâmetros de modelo, retornando mensagens de correção quando algo faltar.
- **FR-004**: O fluxo de atendimento humano deve permanecer disponível; quando uma pergunta não for reconhecida, o CLI deve coletar mensagem e notas do especialista e anexá-las ao estado final do grafo.
- **FR-005**: Devem existir logs estruturados em diretório dedicado do agente, com registros para início/fim de execução, perguntas processadas e escalonamentos.
- **FR-006**: Deve haver um arquivo `.env.example` cobrindo todas as variáveis usadas e o README deve instruir a clonagem, configuração, execução e interpretação dos logs.
- **FR-007**: Uma suíte de testes `agente_perguntas/tests` deve cobrir o grafo, os nodes críticos, o CLI e o tratamento de perguntas desconhecidas, com asserts sobre logs ou mensagens relevantes.
- **FR-008**: Documentação operacional (por exemplo, `docs/` ou seção dedicada) deve detalhar o fluxo de escalonamento humano, critérios de confiança e procedimentos para atualizar o FAQ.

### Key Entities *(include if feature involves data)*

- **AgentConfiguration**: Representa as variáveis de ambiente e opções de execução (chave do modelo, idioma padrão, diretório de logs) expostas ao CLI e validadas na inicialização.
- **FAQEntry**: Estrutura conceitual contendo pergunta, resposta e metadados opcionais (tags, última atualização) utilizada para rankeamento e apresentação.
- **InteractionState**: Estado da sessão do grafo com campos para pergunta recebida, resposta entregue, nível de confiança, status (`respondido automaticamente` ou `encaminhar para humano`) e notas finais.

### Assumptions

- A mesma infraestrutura de modelos utilizada em `agente_simples` estará disponível para `agente_perguntas` (chave ativa e limites compatíveis).
- A equipe adota Python 3.12 e o ambiente virtual já usado no repositório principal.
- O conteúdo do FAQ permanece em memória (sem banco externo) durante esta fase de refatoração.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Novas pessoas na equipe conseguem seguir o README e executar o agente completo em até 10 minutos, sem suporte adicional.
- **SC-002**: A execução de `pytest agente_perguntas/tests` conclui com 100% de sucesso em menos de 90 segundos em ambiente padrão da equipe.
- **SC-003**: Para perguntas cobertas pelo FAQ, a resposta é exibida no terminal em até 5 segundos e o log registra a interação sem erros.
- **SC-004**: Em cenários de escalonamento humano, o resumo final apresenta mensagem e notas personalizadas em 100% dos testes manuais descritos nas histórias P1 e P2.
