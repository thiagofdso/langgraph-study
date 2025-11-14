# Research Log: Reestruturar Agente Perguntas

## Decision: Manter Graph API com StateGraph sequencial
- **Rationale**: O agente atual já opera com um nó único e interrupção humana; a arquitetura espelhada em `agente_simples` usa StateGraph e atende aos requisitos de HITL, checkpoints (`InMemorySaver`) e visualização futura no Studio.
- **Alternatives considered**: Functional API (@entrypoint) descartada por exigir reescrita do fluxo e dificultar reuso de padrões existentes; `create_agent` não se aplica por não precisarmos do middleware system nem de abstração adicional.

## Decision: Estrutura modular alinhada ao padrão `agente_simples`
- **Rationale**: `PROJETOS.md` documenta que agentes de estudo devem separar `config`, `state`, `graph`, `cli`, `utils` e `tests`. O `langgraph-tasks.md` especifica a mesma estrutura, garantindo consistência e facilitando manutenção.
- **Alternatives considered**: Manter `main.py` monolítico foi rejeitado por violar FR-001 e impedir docstrings/observabilidade; criar subpacotes adicionais (e.g. `components/`) é desnecessário para o escopo atual.

## Decision: Logging estruturado com diretório dedicado
- **Rationale**: A especificação exige logs persistentes e `agente_simples` já oferece padrão reutilizável via `utils.logging`. Replicar o formato facilita troubleshooting e mantém mensagens em PT-BR.
- **Alternatives considered**: Uso de `print` ou logging básico sem formatação foi descartado por não atender FR-005.

## Decision: Testes automatizados via pytest com mocks para HITL
- **Rationale**: Suíte dedicada é mandatória (FR-007) e pytest já é padrão do repositório. Mocks permitem validar `interrupt` sem input manual.
- **Alternatives considered**: Testes manuais apenas rejeitados por não oferecerem cobertura regressiva.

## Decision: `.env.example` e documentação operacional
- **Rationale**: FR-006 e FR-008 pedem orientação clara de configuração e procedimentos, replicando abordagem de `agente_simples`.
- **Alternatives considered**: Manter instruções apenas no README foi considerado insuficiente para detalhar fluxos HITL e troubleshooting; docs separados proporcionam referência rápida.
