# Feature Specification: Refactor Memory Agent

**Feature Branch**: `019-refactor-memoria-agent`  
**Created**: November 1, 2025  
**Status**: Draft  
**Input**: User description: "Quero que seja refatorado o codigo do projeto agente_memoria, seguindo boas praticas de python e usando o agente_simples como inspiração."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversa com memória persistente (Priority: P1)

Um operador inicia o agente de memória pelo terminal, conduz uma conversa multi-turno em português e recebe respostas que levam em conta o histórico do mesmo thread.

**Why this priority**: A principal proposta do agente é demonstrar retenção de contexto entre perguntas; sem isso, o agente perde sua utilidade diferenciadora.

**Independent Test**: Executar o agente em um thread nomeado, enviar duas perguntas sequenciais relacionadas e confirmar que a segunda resposta reutiliza corretamente a informação anterior.

**Acceptance Scenarios**:

1. **Given** um thread recém-iniciado, **When** o operador envia uma pergunta e logo em seguida outra que depende da primeira, **Then** a segunda resposta cita o conteúdo informado na primeira interação.
2. **Given** um thread existente com histórico salvo, **When** o operador encerra a execução e inicia novamente o agente apontando o mesmo identificador de thread, **Then** a resposta inicial da nova sessão acessa o histórico anterior sem nova configuração manual.

---

### User Story 2 - Diagnóstico guiado de configuração (Priority: P2)

Uma pessoa mantenedora prepara o ambiente, recebe feedback imediato sobre credenciais ou parâmetros ausentes e encontra instruções claras para corrigir a configuração antes da execução.

**Why this priority**: Facilitar a preparação reduz tempo de suporte e evita falhas antes de demonstrar a memória do agente.

**Independent Test**: Remover temporariamente a credencial obrigatória, iniciar o agente e verificar que a mensagem de bloqueio descreve exatamente o problema e como resolvê-lo.

**Acceptance Scenarios**:

1. **Given** a variável de credencial não configurada, **When** o mantenedor tenta iniciar o agente, **Then** o processo é interrompido com mensagem em português descrevendo o item faltante e como fornecê-lo.
2. **Given** um parâmetro opcional fora da faixa recomendada, **When** o agente é inicializado, **Then** o usuário recebe um aviso sem impedir a execução, incluindo sugestão de ajuste.

---

### User Story 3 - Operação observável e sustentável (Priority: P3)

Como líder técnico, quero estrutura de código, logs e verificações leves para que novas pessoas na equipe consigam manter o agente sem depender de quem o implementou.

**Why this priority**: O agente de memória serve de referência para outros projetos; padrões consistentes aceleram futuras refatorações e auditorias.

**Independent Test**: Seguir a documentação de manutenção, executar o fluxo de testes sumarizado e confirmar que logs trazem informações suficientes para auditar a última conversa.

**Acceptance Scenarios**:

1. **Given** um novo mantenedor seguindo o guia, **When** ele organiza o ambiente e executa os testes rápidos, **Then** o agente roda de ponta a ponta sem ajustes manuais adicionais.
2. **Given** a necessidade de revisar a última execução, **When** a pessoa consulta a saída de logs documentada, **Then** encontra registros com horário, thread utilizado, perguntas e status final.

---

### Edge Cases

- Input vazio ou com menos de cinco caracteres fornecido pelo operador na CLI.
- Thread inexistente ou identificador duplicado informado explicitamente pelo usuário.
- Falha de rede ou indisponibilidade temporária do provedor durante uma conversa ativa.
- Solicitação para reiniciar um thread que já atingiu o limite de histórico suportado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A solução MUST permitir que operadores conduzam conversas multi-turno em português via interface de linha de comando, selecionando ou aceitando um identificador de thread para continuidade do histórico.
- **FR-002**: O agente MUST validar credenciais e parâmetros essenciais antes da primeira interação e exibir mensagens orientativas em caso de falhas, sem expor rastros técnicos.
- **FR-003**: O histórico de cada thread MUST ser armazenado e reutilizado automaticamente em perguntas subsequentes, garantindo que respostas considerem o contexto anterior sem intervenção manual.
- **FR-004**: Usuários MUST conseguir iniciar novos threads ou redefinir o histórico atual por meio de uma ação explícita documentada, evitando vazamento de contexto entre conversas independentes.
- **FR-005**: O fluxo MUST registrar, em arquivos e console, eventos chave de cada execução (thread, perguntas, status, duração) usando convenções de logging alinhadas ao agente simples.
- **FR-006**: A base de código MUST ser reorganizada em componentes claros para configuração, construção do fluxo de conversa, utilidades e CLI, refletindo os padrões de boas práticas apresentados no agente simples.
- **FR-007**: O projeto MUST incluir verificações automatizadas ou scripts reprodutíveis que confirmem memória persistente, tratamento de configuração inválida e manejo de erros do provedor antes de qualquer entrega.
- **FR-008**: A documentação MUST descrever instalação, configuração, uso com memória, procedimentos de reset e troubleshooting, destacando diferenças-chave em relação ao agente simples.

### Key Entities *(include if feature involves data)*

- **Thread de Conversa**: Representa uma sequência de interações associada a um identificador único; inclui histórico de mensagens, carimbo de tempo da última atualização e status (ativo, reiniciado).
- **Interação Registrada**: Cada pergunta ou resposta armazenada no histórico; atributos incluem papel (usuário/agente), conteúdo normalizado, ordem na conversa e possíveis metadados (duração, tipo de erro).
- **Perfil de Configuração**: Conjunto de credenciais e ajustes de execução fornecidos via variáveis de ambiente ou arquivos de configuração, incluindo regras de validação e limites suportados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em testes internos, 100% das duplas de perguntas dependentes no mesmo thread retornam respostas consistentes com o histórico em até 12 segundos por interação.
- **SC-002**: Durante o onboarding, novos operadores que sigam a documentação concluem setup e executam uma conversa com memória em menos de 10 minutos.
- **SC-003**: Cada categoria de falha configurada (credencial ausente, parâmetro inválido, indisponibilidade do provedor) apresenta mensagem acionável na primeira tentativa de execução e bloqueia o fluxo até correção.
- **SC-004**: A verificação automatizada ou checklist documentada cobre pelo menos três cenários críticos (conversa bem-sucedida, reset de thread, falha de configuração) e roda integralmente em menos de 5 minutos.

## Assumptions

- A execução continuará acontecendo em ambiente local via CLI com acesso à internet para o provedor de linguagem.
- O armazenamento de memória pode permanecer em estrutura volátil, desde que ofereça continuidade entre execuções identificadas pelo mesmo thread.
- Português brasileiro permanece como idioma principal para prompts, mensagens de erro e documentação voltada a operadores.
