# Research Summary – Refatorar agente_tool

## Decision 1: Estrutura modular alinhada a agentes existentes
- **Decision**: Replicar a estrutura de diretórios adotada em `agente_simples` e `agente_memoria`, criando `graph.py`, `state.py`, `config.py`, `cli.py`, pacote `utils/` e documentação dedicada.
- **Rationale**: Garante consistência operacional e permite reutilizar padrões de onboarding já validados pela equipe.
- **Alternatives Considered**:
  - Manter toda a lógica em `main.py` (rejeitado: torna manutenção e testes difíceis).
  - Estrutura minimalista apenas com `graph.py` e `nodes.py` (rejeitado: não cobre exigências de documentação, CLI e padrões de config).

## Decision 2: Checkpointer e configuração do LLM
- **Decision**: Utilizar `MemorySaver` como checkpointer padrão e centralizar criação do LLM Gemini em `config.py`, com carregamento de `.env` encapsulado.
- **Rationale**: Mantém compatibilidade com uso local e segue prática já aplicada em `agente_memoria`.
- **Alternatives Considered**:
  - Persistência em SQLite/PostgreSQL (rejeitado: escopo não requer armazenamento durável).
  - Instanciar LLM diretamente nos nodes (rejeitado: dificulta testes e reuso).

## Decision 3: Segurança na ferramenta calculadora
- **Decision**: Reimplementar a ferramenta em `utils/tools.py` com parsing via `ast.parse` e `eval` restringido, retornando mensagens de erro amigáveis.
- **Rationale**: Minimiza risco de execução arbitrária e atende edge cases descritos no plano.
- **Alternatives Considered**:
  - Preservar `eval` simples (rejeitado: inseguro).
  - Integrar biblioteca matemática externa (rejeitado: adiciona dependência desnecessária).

## Decision 4: Catálogo de nodes compartilhado
- **Decision**: Reutilizar nomes `validate_input`, `invoke_model`, `format_response` e introduzir `plan_tool_usage` e `execute_tools`, registrando-os em `graph-nodes-patterns.md`.
- **Rationale**: Cumpre o princípio XXIII e facilita padronização para futuros agentes com ferramentas.
- **Alternatives Considered**:
  - Criar nomenclaturas específicas do projeto (rejeitado: fere o objetivo de padrões globais).

## Decision 5: Observabilidade e testes
- **Decision**: Adicionar logging padronizado via `utils/logging.py` e implementar suíte pytest cobrindo validação, roteamento de ferramenta e integração do grafo.
- **Rationale**: Garante auditabilidade (User Story 3) e reduz regressões.
- **Alternatives Considered**:
  - Testes apenas manuais (rejeitado: não atende sucesso esperado).
  - Logging pontual em `print` (rejeitado: inconsistente com agentes de referência).
