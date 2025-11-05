# Feature Specification: Relatório de Vendas com Insights Gemini

**Feature Branch**: `001-gemini-sales-report`  
**Created**: 2025-11-05  
**Status**: Draft  
**Input**: User description: "Quero que altere o projeto agente_banco_dados para que o relatório de vendas seja gerado usando o gemini-2.5-flash, consulte o agente_simples para verificar como configurar a llm e como deve funcionar o nó da llm. No prompt quero que tenha instruções para gerar insights a partir dos dados da consulta no banco de dados."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receber diagnóstico guiado por IA (Priority: P1)

Um analista de vendas executa o agente para obter rapidamente um relatório narrativo que interprete os dados do banco SQLite local, destacando tendências, riscos e oportunidades comerciais.

**Why this priority**: A interpretação automatizada elimina leitura manual extensa e acelera decisões diárias do time comercial.

**Independent Test**: Executar o CLI do agente com a base inicializada, validar que o relatório entregue contém narrativa gerada por IA com referências explícitas aos números exibidos.

**Acceptance Scenarios**:

1. **Given** a base SQLite populada com dados de vendas e credenciais de IA válidas, **When** o analista executa o agente, **Then** o relatório exibe um resumo narrativo que menciona os principais produtos e vendedores junto a seus valores numéricos.
2. **Given** uma variação relevante nos totais (por exemplo, queda acentuada em um produto), **When** o relatório é gerado, **Then** a narrativa apresenta pelo menos duas recomendações ou alertas diretamente ligados ao comportamento observado.

---

### User Story 2 - Conferir dados de origem (Priority: P2)

Como gestora comercial, quero validar rapidamente de onde vieram os números utilizados pela IA para confiar nas recomendações.

**Why this priority**: Transparência sobre a origem e versão dos dados aumenta a confiança e reduz retrabalho com conferências paralelas.

**Independent Test**: Gerar o relatório e verificar se ele inclui tabelas ou listas estruturadas dos dados-base e identifica a fonte (banco local) e o horário de geração.

**Acceptance Scenarios**:

1. **Given** o agente foi executado com sucesso, **When** a gestora lê o relatório, **Then** ela encontra a indicação da fonte de dados e tabelas consolidadas dos principais produtos e vendedores.
2. **Given** o relatório foi gerado, **When** a gestora confere os números na base SQLite manualmente, **Then** os valores presentes nas tabelas do relatório coincidem com os dados brutos.

---

### User Story 3 - Entender limitações da IA (Priority: P3)

Como operadora de suporte, quero receber mensagens claras quando a geração por IA falhar para orientar o time sobre como resolver.

**Why this priority**: Orientação objetiva reduz tempo de indisponibilidade e evita tickets escalados sem necessidade.

**Independent Test**: Simular falha de credencial ou indisponibilidade do serviço de IA e confirmar que o agente exibe aviso compreensível com próximo passo indicado.

**Acceptance Scenarios**:

1. **Given** a chave de acesso à IA está ausente, **When** o agente é executado, **Then** o processo é interrompido com mensagem que explica a ausência da credencial e indica configurar o acesso antes de tentar novamente.
2. **Given** ocorre timeout ou erro de serviço durante a geração, **When** o agente executa o fluxo, **Then** o usuário recebe aviso amigável sugerindo nova tentativa após alguns instantes.

---

### Edge Cases

- Como o agente responde quando o banco contém menos registros que o mínimo esperado (por exemplo, apenas um vendedor ativo).
- Como o relatório se comporta quando os valores monetários ou quantitativos são zero ou negativos por ajustes manuais.
- O que é apresentado quando a IA retorna resposta vazia ou genérica sem insights úteis.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O agente deve consolidar métricas essenciais de vendas (produtos mais vendidos, vendedores com maior receita, totais) antes de chamar a inteligência artificial.
- **FR-002**: O contexto enviado à inteligência artificial deve incluir instruções explícitas para gerar insights, tendências, riscos e recomendações acionáveis baseadas nos dados consolidados.
- **FR-003**: O relatório entregue ao usuário deve conter uma seção narrativa produzida pela IA que apresente, no mínimo, três insights distintos apoiados por números específicos do contexto.
- **FR-004**: O relatório deve exibir as tabelas ou listas estruturadas das métricas utilizadas, permitindo conferência manual dos valores.
- **FR-005**: O relatório deve destacar a data e hora de geração em UTC e mencionar que os dados originam do banco SQLite local do agente.
- **FR-006**: Sempre que houver falha de autenticação, indisponibilidade ou timeout na chamada da inteligência artificial, o agente deve comunicar o erro de forma compreensível e orientar o próximo passo ao usuário.
- **FR-007**: O agente deve registrar em metadados acessíveis (ex.: logs ou retorno estruturado) o tempo total de geração e o volume de registros considerados, para auditoria e monitoramento interno.

### Key Entities

- **Métrica de Produto**: Representa cada produto com nome, quantidade total vendida e receita total utilizada na geração do relatório.
- **Métrica de Vendedor**: Representa cada vendedor com nome, região, quantidade vendida e receita total associada.
- **Insight de Vendas**: Mensagem narrativa produzida pela IA que descreve tendência, anomalia ou recomendação, sempre referenciando dados numéricos e entidades relevantes.

## Assumptions

- As credenciais e o modelo gemini-2.5-flash já estão homologados pela organização e disponíveis via variáveis de ambiente antes da execução do agente.
- Os usuários continuarão executando o agente via CLI, com a base SQLite sendo inicializada automaticamente a cada execução.
- O time de vendas aceita receber o relatório em português brasileiro, mantendo consistência com o restante dos agentes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em execuções com a base seed atual, o relatório apresenta pelo menos três insights distintos que citam valores concretos dos dados de vendas.
- **SC-002**: 95% das execuções com credenciais válidas finalizam a entrega do relatório em até 30 segundos.
- **SC-003**: Em avaliação com o time comercial, pelo menos 80% dos participantes afirmam que o relatório reduz o tempo de análise semanal em 20% ou mais.
- **SC-004**: Em testes que simulam ausência de credencial ou erro de serviço, o agente comunica mensagem de ação clara em até 5 segundos após a falha.
