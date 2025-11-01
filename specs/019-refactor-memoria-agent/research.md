# Research Findings: Refactor Memory Agent

## Decision 1: Adotar estrutura modular espelhando `agente_simples`
- **Rationale**: O `agente_simples` já comprovou organização estável com separação clara de `config`, `state`, `graph`, `cli` e `utils`. Reaproveitar esse padrão garante consistência com o catálogo `PROJETOS.md`, simplifica manutenção e atende à diretriz do documento de tarefas.
- **Alternatives considered**: Manter toda a lógica em `main.py` (rejeitado por dificultar testes) ou migrar para Functional API (adiado porque o grafo atual já cobre o fluxo e condiz com o requisito de memória). 

## Decision 2: Permanecer com `StateGraph` + `InMemorySaver`
- **Rationale**: O checkpointer em memória já satisfaz os requisitos de continuidade por thread e mantém o projeto leve para demonstrações locais. A documentação especifica apenas que o armazenamento “pode permanecer em estrutura volátil”, então não há necessidade imediata de camadas persistentes.
- **Alternatives considered**: Substituir por SQLite/PostgreSQL (adiado por aumentar esforço e não trazer valor imediato) ou migrar para `store` com embeddings (fora do escopo atual).

## Decision 3: Implementar pré-checagem de configuração e logging estruturado
- **Rationale**: O `agente_simples` traz um fluxo comprovado de preflight via `preflight_config_check()` e logging com arquivos e console. Replicar esse padrão oferece diagnósticos claros, atendendo às histórias de usuário P2/P3 e FR-005.
- **Alternatives considered**: Exibir erros genéricos diretamente na CLI (rejeitado por não cumprir requisitos) ou adotar lib externa de logging (desnecessário; o utilitário interno já atende).

## Decision 4: Validar entradas e comandos de CLI com Pydantic
- **Rationale**: Utilizar um modelo Pydantic (como `DialogueInput` em `agente_simples`) garante normalização de mensagens, comprimento mínimo e mensagens amigáveis, suportando FR-001 e FR-004.
- **Alternatives considered**: Validação manual em funções (mais propenso a regressões) ou depender totalmente do LLM (não cumpre requisitos de previsibilidade).

## Decision 5: Construir suíte de testes separada por nodes e fluxo
- **Rationale**: Seguir o padrão de testes do `agente_simples` (unit + integração) permite validar memória, erros de configuração e resets antes de entrega, alinhando FR-007/SC-004 e a Constituição (Princípios II e III).
- **Alternatives considered**: Limitar-se a testes manuais (rejeitado por falta de rastreabilidade) ou tentar testes e2e completos com LLM real (instável e lento para CI).
