# Feature Specification: Iterative Reflection Agent Guidance

**Feature Branch**: `014-add-reflection-agent`  
**Created**: October 30, 2025  
**Status**: Draft  
**Input**: User description: "Crie na pasta agente_reflexao_basica um agente que gera uma resposta, depois usa um nó separado de reflexão para criticar e melhorar a resposta inicial. O ciclo se repete por um número fixo de iterações.[1][2] O agente deve responder a pergunta : O que é importante para um programador aprender. O proximo requisito é o 014."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Refined Guidance Delivery (Priority: P1)

An instructional designer executa `python agente_reflexao_basica/main.py` e recebe um texto final que melhora o rascunho inicial para a pergunta fixa “O que é importante para um programador aprender”, incorporando comentários de reflexão automática.

**Why this priority**: Entrega o valor principal da feature com um único comando e permite avaliação imediata do conteúdo gerado.

**Independent Test**: Rodar o script e confirmar que o texto final menciona pelo menos quatro prioridades distintas e é diferente do primeiro rascunho.

**Acceptance Scenarios**:

1. **Given** o agente é iniciado, **When** gera o primeiro rascunho, **Then** o conteúdo é impresso antes da etapa de reflexão.
2. **Given** todas as reflexões são processadas, **When** o rascunho final é exibido, **Then** as recomendações mais recentes aparecem no texto final.

---

### User Story 2 - Critique Transparency (Priority: P2)

Um revisor acompanha cada reflexão no console, entendendo como o agente critica rascunhos anteriores e o racional para o resultado final.

**Why this priority**: Garante rastreabilidade sem depender de arquivos extras e permite revisar rapidamente o histórico da execução.

**Independent Test**: Executar o script e verificar que cada reflexão é impressa em order cronológica antes do rascunho subsequente.

**Acceptance Scenarios**:

1. **Given** uma reflexão é gerada, **When** o console imprime o bloco “Reflexões”, **Then** a crítica aparece com separação clara antes da próxima iteração.

---

### User Story 3 - Iteration Control (Priority: P3)

Um membro de operações ajusta o limite máximo de reflexões embutido no código para equilibrar tempo de execução e profundidade da revisão.

**Why this priority**: Mantém previsibilidade sem introduzir parâmetros externos ou arquivos de configuração adicionais.

**Independent Test**: Alterar o limite no arquivo único `main.py`, executar o agente e confirmar que o número de reflexões não ultrapassa o valor configurado.

**Acceptance Scenarios**:

1. **Given** o limite é definido para duas reflexões, **When** o agente roda, **Then** apenas dois blocos de “Reflexão” são impressos antes da resposta final.

---

### Edge Cases

- Falha no carregamento da chave GEMINI_API_KEY impede a execução.
- Modelo retorna reflexão vazia ou sem melhorias sugeridas.
- Limite de reflexões configurado inadvertidamente para menos de duas interações (rascunho inicial + final).
- Execução interrompida antes de concluir a sequência de reflexões.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE gerar um rascunho inicial para a pergunta fixa antes de qualquer reflexão.
- **FR-002**: O sistema DEVE gerar uma reflexão em formato de texto estruturado (forças e melhorias) após cada rascunho.
- **FR-003**: O rascunho imediatamente seguinte DEVE incorporar o conteúdo da reflexão mais recente.
- **FR-004**: O fluxo DEVE encerrar automaticamente quando o número total de mensagens exceder o limite definido em código.
- **FR-005**: A execução DEVE imprimir no console cada reflexão, cada rascunho na ordem cronológica e, por fim, a resposta final destacada.

### Key Entities *(include if feature involves data)*

- **Mensagem**: Lista de objetos `BaseMessage` manipulada pelo LangGraph, contendo pergunta, rascunhos e reflexões.
- **Limite de Mensagens**: Valor numérico no código que controla a quantidade máxima de mensagens antes de finalizar o fluxo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 95% das execuções observadas, a resposta final cita pelo menos quatro prioridades distintas.
- **SC-002**: O número de reflexões impressas nunca excede o limite configurado de mensagens (≤ 6 + pergunta).
- **SC-003**: Em avaliações internas, 90% dos revisores relatam que a resposta final é melhor estruturada que o rascunho inicial.
- **SC-004**: O tempo de execução médio permanece abaixo de 60 segundos com o limite padrão de reflexões.

## Assumptions

- O limite padrão de mensagens garante até três rascunhos (inicial + dois refinamentos); alterações são feitas editando a constante em `main.py`.
- A pergunta permanece fixa em todas as execuções, logo validação foca apenas na qualidade da resposta.
- Revisores utilizam o console como principal fonte de auditoria, sem geração de arquivos suplementares.
