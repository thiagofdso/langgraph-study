# Research Notes: Refactor Simple Agent

## Decision: Estrutura Modular de Pacote
- **Rationale**: A adoção da estrutura básica de projetos LangGraph (seção 0.5.1 do template avançado) reforça separação de responsabilidades e segue padrões já aplicados em `agente_tool` e `agente_web`, que organizaram nodes/utilidades em submódulos facilitando manutenção.
- **Alternatives considered**: Manter `main.py` monolítico foi rejeitado por dificultar extensões futuras (ex.: múltiplos nodes, middleware). Estrutura média/monorepo excede o escopo atual do agente simples.

## Decision: State com TypedDict + Pydantic de Entrada
- **Rationale**: Combina `TypedDict` com reducer `add_messages` (padrão `agente_memoria`) para preservar histórico, enquanto Pydantic valida inputs do CLI antes de acionar o LLM, garantindo mensagens amigáveis em caso de erro.
- **Alternatives considered**: Usar apenas Pydantic para todo o estado adicionaria overhead e serialização desnecessária; manter apenas o TypedDict sem validação não atende às boas práticas de qualidade descritas na spec.

## Decision: Configuração Centralizada via AppConfig
- **Rationale**: Centralizar variáveis de ambiente e criação de dependências (LLM, checkpointer) em `config.py` segue recomendações do template e permite trocar provedores ou checkpointers sem alterar nodes, além de alinhar com o padrão em `agente_web`.
- **Alternatives considered**: Instanciar o LLM diretamente nos nodes foi descartado por causar repetição e dificultar ajustes; um arquivo `.yaml` externo não se justifica para o tamanho atual do projeto.

## Decision: Logging Estruturado + Pastas de Logs
- **Rationale**: Criar `utils/logging.py` com logger configurado garante rastreabilidade de execuções, alinhado ao requisito de auditoria e ao que já acontece em `agente_web` (registro em arquivo). Logs facilitam diagnóstico quando o modelo falha.
- **Alternatives considered**: Apenas `print` no CLI não permite arquivos históricos; integrar diretamente com LangSmith hoje seria excessivo, mas o design mantém caminho aberto para futura integração.

## Decision: Estratégia de Testes com pytest
- **Rationale**: Implementar testes unitários para nodes e Pydantic, além de testes de integração com mocks do LLM, está alinhado à Constituição (princípio III) garantindo foco nos componentes determinísticos.
- **Alternatives considered**: Testar apenas manualmente violaria o princípio de qualidade, enquanto tentar validar respostas reais do LLM seria instável e fora do escopo conforme orientação de evitar testes não determinísticos.
