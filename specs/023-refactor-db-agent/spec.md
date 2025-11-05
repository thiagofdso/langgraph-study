# Feature Specification: Refactor agente_banco_dados Structure

**Feature Branch**: `023-refactor-db-agent`  
**Created**: 2025-11-05  
**Status**: Draft  
**Input**: User description: "O proximo spec number é o 023, quero que seja refatorado o projeto agente_banco_dados seguindo boas praticas de langgraph, o objetivo é organizar o projeto em arquivos espeficicos semelhante ao agente_simples, não deve ser alterada funcionalidade, o objetivo é apenas estrutura o projeto usando boas praticas sem mudar a funcionalidade. Deve manter tambem o teste. Deve ter um def create_app() conforme o agente_simples para funcionar no langgraph cli."

**Note**: This specification is an integral part of the specification-driven development process, generated and managed using the `.specify` framework, ensuring clear requirements and alignment with project goals.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CLI workflow preserved (Priority: P1)

Como pessoa usuária que executa o agente via terminal, quero continuar seguindo o mesmo passo a passo (ativar venv e rodar o script principal) para gerar o relatório de vendas em Markdown sem notar diferenças funcionais após a refatoração.

**Why this priority**: Preservar o fluxo atual garante que a refatoração não introduza regressões para quem depende do relatório diário.

**Independent Test**: Executar o roteiro descrito no README do projeto e comparar o relatório obtido com a versão anterior utilizando o mesmo banco SQLite de exemplo.

**Acceptance Scenarios**:

1. **Given** o banco `agente_banco_dados/data/sales.db` recém-criado, **When** a pessoa executa o comando de linha de comando documentado, **Then** o terminal exibe o relatório com seções "Produtos mais vendidos" e "Melhores vendedores" contendo os mesmos títulos e contagens da versão anterior.
2. **Given** um ambiente limpo sem o arquivo `sales.db`, **When** o usuário roda a aplicação, **Then** o banco é recriado automaticamente, a saída contém a mensagem de inicialização e o relatório completo é impresso.

---

### User Story 2 - LangGraph CLI compatível (Priority: P2)

Como pessoa que utiliza o LangGraph CLI ou scripts automáticos, quero importar uma função `create_app()` do agente para obter o grafo compilado e executá-lo diretamente, sem depender do script `main.py`.

**Why this priority**: Permite integração com pipelines padronizados do LangGraph e espelha a experiência do `agente_simples`.

**Independent Test**: Importar `create_app()` em um shell Python e invocar o grafo retornado para gerar o mesmo relatório esperado usando o banco de exemplo.

**Acceptance Scenarios**:

1. **Given** o módulo público exportando `create_app()`, **When** um script chama essa função e executa `app.invoke({})`, **Then** o resultado contém o campo `report_markdown` com o mesmo conteúdo produzido pelo fluxo tradicional.

---

### User Story 3 - Projeto fácil de manter (Priority: P3)

Como mantenedora do repositório, quero que o agente esteja organizado em módulos especializados (configuração, estado, nós do grafo, CLI, testes) espelhando o padrão usado em `agente_simples`, para facilitar revisões, extensões futuras e reaproveitamento de utilitários.

**Why this priority**: Uma estrutura previsível reduz tempo de onboarding e riscos de regressão em evoluções subsequentes.

**Independent Test**: Revisar a nova estrutura de diretórios e verificar que cada responsabilidade está isolada, com documentação atualizada indicando os pontos de extensão.

**Acceptance Scenarios**:

1. **Given** o repositório refatorado, **When** a mantenedora compara o layout com `agente_simples`, **Then** identifica módulos equivalentes (por exemplo, grafo, CLI, configuração, utilidades) com responsabilidades descritas na documentação.

---

### Edge Cases

- Se o diretório `data/` estiver ausente, a refatoração deve recriá-lo automaticamente antes de acessar o banco, mantendo o comportamento atual.
- Se o banco SQLite já contiver dados anteriores, o fluxo precisa continuar idempotente: não deve duplicar registros nem falhar ao gerar o relatório.
- Caso `create_app()` seja importado em um ambiente sem stdout (ex.: execução agendada), o resultado deve ser consumível via retorno da função, sem dependência de prints adicionais.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O fluxo executado via CLI deve continuar inicializando o banco local, rodando o grafo e imprimindo o relatório em português exatamente como antes da refatoração.
- **FR-002**: O projeto deve expor uma função `create_app()` que retorna o grafo compilado e acessível sem efeitos colaterais imediatos além da inicialização necessária.
- **FR-003**: A estrutura de diretórios do agente deve separar claramente configuração, definição do grafo, nós/funções auxiliares, CLI e testes, alinhando nomes e responsabilidades aos padrões já adotados em `agente_simples`.
- **FR-004**: Todos os testes automatizados existentes relacionados ao agente devem permanecer passando; quaisquer ajustes necessários devem preservar asserções funcionais equivalentes às anteriores.
- **FR-005**: A documentação do agente (README e/ou novos apontamentos) precisa ser atualizada para refletir a nova organização, incluindo instruções para execução via script principal e via LangGraph CLI.
- **FR-006**: A refatoração deve manter compatibilidade com o ambiente configurado no repositório (Python 3.12, dependências existentes) sem exigir novos requisitos.

### Key Entities *(include if feature involves data)*

- **SalesReportState**: Representa os dados intermediários do fluxo (top produtos, top vendedores, relatório em Markdown) que circulam entre os nós do grafo.
- **SQLiteDataset**: Conjunto de tabelas (`products`, `sellers`, `sales`) armazenado em arquivo local que fornece as métricas consumidas pelo grafo e pelas consultas de relatório.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das execuções seguindo o passo a passo do README produzem relatório com as mesmas seções, títulos e contagens de registros verificados na versão pré-refatoração.
- **SC-002**: O ponto de entrada programático do grafo completa a geração do relatório em até 10 segundos usando o banco de exemplo, sem falhas de inicialização ou execução.
- **SC-003**: A suíte de testes automatizados relevante para o agente atinge taxa de sucesso de 100% em duas execuções consecutivas após a refatoração.
- **SC-004**: Revisão de código por pelo menos uma mantenedora confirma que a nova organização espelha as melhores práticas de `agente_simples`, sem apontar regressões funcionais.

## Assumptions

- O comportamento funcional atual (estrutura do relatório, dados de exemplo, mensagens de console) é considerado baseline e deve ser preservado.
- A refatoração pode reutilizar utilitários e convenções existentes em `agente_simples`, desde que não introduza dependências inéditas.
- A equipe continuará utilizando o ambiente virtual já presente no repositório para executar o agente e os testes.
