# Feature Specification: Reflexion Web Evidence Agent

**Feature Branch**: `016-add-reflexion-web`  
**Created**: October 31, 2025  
**Status**: Draft  
**Input**: User description: "Implemente na pasta agente_reflexao_web o padrão Reflexion completo onde o agente não só reflete, mas fundamenta suas críticas em dados externos (como resultados de ferramentas de busca) e gera citações explícitas. O agente deve responder a pergunta Como funciona o Google Agent Development Kit? O próximo requisito é o de número 016."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resposta com Evidências Confiáveis (Priority: P1)

Um analista executa o agente de reflexão web para responder “Como funciona o Google Agent Development Kit?” e recebe uma resposta final em português que descreve o kit (ex.: criação de agentes Gemini com orquestração multi-etapas, conectores com Google Workspace, governança no Agentspace e integrações empresariais via Application Integration) apoiada por citações numeradas ligadas a fontes recentes recuperadas em tempo real.

**Why this priority**: Garante que a equipe tenha um resumo acionável e auditável sobre o GADK, principal resultado de valor para stakeholders.

**Independent Test**: Rodar o agente e verificar que a resposta final lista pelo menos duas fontes distintas relevantes ao GADK, com descrições alinhadas aos conteúdos originais.

**Acceptance Scenarios**:

1. **Given** o usuário informa a pergunta em português, **When** o agente conclui o ciclo de reflexão, **Then** ele apresenta resposta final com bullets claros e citações numeradas vinculadas às fontes externas.
2. **Given** as fontes retornadas destacam recursos como console low-code, conectores com Drive/Docs/Sheets, implantação no Agent Engine e integrações empresariais com APIs, **When** a resposta final é emitida, **Then** o agente menciona essas capacidades de forma coerente e atribui cada afirmação a uma fonte específica.

---

### User Story 2 - Auditoria da Reflexão e Críticas (Priority: P1)

Uma pessoa de compliance revisa o histórico da sessão para entender como o agente avaliou a primeira resposta, quais críticas produziu e quais trechos das fontes embasam cada ajuste antes da resposta final.

**Why this priority**: Transparência do processo é indispensável para validar que o agente não fabricou informações.

**Independent Test**: Acessar o histórico detalhado gerado pelo agente e confirmar que cada crítica referencia a fonte correspondente e explica a correção aplicada.

**Acceptance Scenarios**:

1. **Given** o agente gera um rascunho inicial, **When** inicia a fase de reflexão, **Then** registra cada crítica apontando qual fonte inspira a correção e o impacto esperado.
2. **Given** a resposta final está pronta, **When** o auditor consulta o histórico, **Then** encontra pelo menos duas iterações documentadas (rascunho, crítica, resposta final) com ligações explícitas entre críticas e atualizações textuais.

### Edge Cases

- Busca retorna resultados duplicados ou muito similares; o agente deve consolidar e citar apenas fontes verdadeiramente distintas.
- Fonte retornada com idioma diferente do solicitado; o agente deve traduzir trechos essenciais mantendo a fidelidade ao original e indicar o idioma da fonte.
- Conteúdo atualizado recentemente em conflito com versões antigas; a reflexão deve destacar divergências e preferir a evidência mais recente.
- Ferramenta de busca responde com formatos inesperados (ex.: campos vazios ou sem URL); o agente deve descartar ou pedir nova consulta antes de citar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O agente DEVE executar um ciclo de reflexão completo com pelo menos duas iterações distintas: rascunho inicial da resposta e crítica estruturada que leve a uma versão final ajustada.
- **FR-002**: O agente DEVE consultar uma ferramenta de busca configurada no projeto, capturar metadados (título, resumo e URL) e armazê-los como evidências vinculadas à pergunta sobre o Google Agent Development Kit.
- **FR-003**: Cada crítica gerada pelo agente DEVE referenciar explicitamente qual evidência externa sustenta a correção sugerida e indicar que mudança será aplicada.
- **FR-004**: A resposta final DEVE apresentar as principais capacidades do Google Agent Development Kit (orquestração multi-etapas com Gemini, conectores com Google Workspace, governança no Agentspace, integrações empresariais via Application Integration e implantação no Agent Engine) e citar a fonte correspondente para cada afirmação.
- **FR-005**: A resposta final DEVE manter o idioma da pergunta original, incluir formatação legível (parágrafos e bullets) e uma seção de referências numeradas com URLs rastreáveis.
- **FR-006**: O agente DEVE disponibilizar um histórico de sessão que contenha entradas cronológicas (pergunta, rascunho, críticas, buscas executadas, resposta final) acessíveis após a execução.
- **FR-007**: Quando múltiplas fontes confiáveis estiverem disponíveis, o agente DEVE priorizar pelo menos duas fontes distintas e registrar a data de acesso para facilitar auditoria futura.

### Key Entities *(include if feature involves data)*

- **Sessão de Reflexão**: Representa uma execução completa do agente, incluindo pergunta recebida, iterações de resposta, críticas, ações de busca e resultado final.
- **Evidência Externa**: Conjunto de metadados recuperados de uma fonte (título, resumo, URL, data de acesso) associado a um trecho específico da resposta ou crítica.
- **Crítica Estruturada**: Comentário que avalia o rascunho, indica lacunas ou ajustes e referencia as evidências utilizadas para justificar a mudança.
- **Resposta Final**: Entrega consolidada ao usuário contendo explicação do GADK, estruturação amigável e lista de citações correspondentes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 95% das execuções monitoradas, a resposta final inclui pelo menos duas citações numeradas com links válidos que permanecem acessíveis e relevantes ao GADK.
- **SC-002**: Em 100% das execuções com fontes disponíveis, o histórico registra no mínimo uma crítica explícita que referencia diretamente uma evidência externa e descreve a alteração resultante.
- **SC-003**: Em testes de usabilidade, 90% dos avaliadores classificam a clareza das citações e da explicação final como ≥ 4 em escala de 1 a 5.

## Assumptions

- O ambiente de execução possui acesso autenticado às ferramentas de busca autorizadas pelo projeto e registra horários de consulta para auditoria.
- Os usuários esperam respostas em português para perguntas em português; termos técnicos em inglês podem ser mantidos quando não houver tradução consolidada.
- As fontes oficiais (blogs do Google, comunicados de imprensa, análises de mídia especializada) permanecem acessíveis para consulta pública.
