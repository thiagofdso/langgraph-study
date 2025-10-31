# Implementation Tasks: Reflexion Web Evidence Agent

**Branch**: `016-add-reflexion-web`  
**Spec**: [specs/016-add-reflexion-web/spec.md](specs/016-add-reflexion-web/spec.md)  
**Plan**: [specs/016-add-reflexion-web/plan.md](specs/016-add-reflexion-web/plan.md)

## Phase 1 — Setup
- [X] T001 Criar estrutura inicial `agente_reflexao_web/` com `__init__.py` e `main.py` vazio
- [X] T002 Copiar `.env` de `agente_web/.env` para `agente_reflexao_web/.env` sem alterações
- [X] T003 Registrar dependências do novo agente na lista de projetos em `./AGENTS.md`

## Phase 2 — Fundamentos Compartilhados
- [X] T004 Definir `AgentState` com `add_messages`, contador de iterações, armazenamento de reflexões e evidências em `agente_reflexao_web/main.py`
- [X] T005 Configurar `InMemorySaver` e `config` com `thread_id` fixo para memória entre nós em `agente_reflexao_web/main.py`
- [X] T006 Implementar utilitário para normalizar resultados Tavily em estrutura `Evidence` com IDs e timestamps em `agente_reflexao_web/main.py`
- [X] T007 Implementar helper para formatar citações numeradas e seção de referências em `agente_reflexao_web/main.py`

## Phase 3 — User Story 1 (Priority P1)  
**Objetivo**: Entregar resposta revisada com evidências confiáveis em português usando três nós (geração, decisão, reflexão).  
**Independent Test**: Executar `python agente_reflexao_web/main.py` e verificar resposta final contendo ≥2 citações numeradas alinhadas às evidências pesquisadas pelo nó de reflexão.

- [X] T008 [US1] Implementar nó `gerar_resposta` que produz rascunho inicial sem ferramentas, incorpora feedbacks anteriores, incrementa contador e registra mensagem em `agente_reflexao_web/main.py`
- [X] T009 [US1] Implementar nó `decidir_fluxo` que verifica limite de iterações (máx. 3), avalia se há feedback pendente e encerra ou direciona ao nó de reflexão em `agente_reflexao_web/main.py`
- [X] T010 [US1] Implementar nó `refletir_com_evidencias` que executa Tavily, armazena evidências e gera revisão com referências obrigatórias em `agente_reflexao_web/main.py`
- [X] T011 [US1] Conectar grafo `gerar_resposta -> decidir_fluxo -> refletir_com_evidencias -> gerar_resposta` garantindo que apenas esses três nós existam em `agente_reflexao_web/main.py`
- [X] T012 [US1] Ajustar prompts para que `gerar_resposta` utilize críticas e evidências mais recentes ao reformular a resposta em `agente_reflexao_web/main.py`
- [X] T013 [US1] Produzir resposta final com citações numeradas e seção de referências ao concluir o grafo em `agente_reflexao_web/main.py`

## Phase 4 — User Story 2 (Priority P1)  
**Objetivo**: Disponibilizar trilha de auditoria das iterações e críticas.  
**Independent Test**: Executar `python agente_reflexao_web/main.py` e revisar log/histórico contendo rascunhos, críticas com evidências e resposta final.

- [X] T014 [US2] Modelar `IterationRecord` vinculando rascunho, reflexão, evidências usadas e número da iteração em `agente_reflexao_web/main.py`
- [X] T015 [US2] Persistir detalhes das críticas e evidências por iteração no histórico em `agente_reflexao_web/main.py`
- [X] T016 [US2] Emitir relatório legível (stdout ou arquivo) com todas as iterações e fontes correspondentes após execução em `agente_reflexao_web/main.py`
- [X] T017 [US2] Garantir que resposta final destaque quais evidências suportaram ajustes críticos citados no histórico em `agente_reflexao_web/main.py`

## Phase 5 — Polish & Cross-Cutting
- [X] T018 Revisar tratamento de avisos (poucas evidências, falhas de busca) alinhado aos edge cases em `agente_reflexao_web/main.py`
- [X] T019 Atualizar `agente_reflexao_web/README.md` com instruções de execução e interpretação do histórico
- [X] T020 Executar teste manual final (`python agente_reflexao_web/main.py`) e anexar saída relevante ao README ou relatório apropriado

## Dependencies
1. Phase 1 deve ser concluída antes da Phase 2.  
2. Phase 2 é pré-requisito para US1 e US2.  
3. US1 precisa ser concluída antes de US2 (histórico depende do fluxo principal).  
4. Phase 5 ocorre apenas após todas as histórias.

## Parallel Execution Opportunities
- T004–T007 podem avançar em paralelo após a estrutura inicial existir.  
- Dentro da US1, T010 (reflexão) e ajustes de prompts (T012) podem ser trabalhados em paralelo quando utilitários estiverem prontos.  
- T014–T016 podem ser executadas em paralelo assim que US1 estiver funcional.

## Independent Test Criteria
- **US1**: Rodar `python agente_reflexao_web/main.py` → saída final com ≥2 citações numeradas coerentes com as evidências reunidas pelo nó de reflexão.  
- **US2**: Rodar `python agente_reflexao_web/main.py` → relatório/histórico contendo rascunhos, críticas fundamentadas e links para as fontes utilizadas.

## MVP Scope
- MVP corresponde à entrega completa da User Story 1 (Phase 3), pois fornece resposta final fundamentada com fluxo Reflexion limitado a três nós.

## Implementation Strategy
1. Preparar infraestrutura do agente (Phases 1 e 2).  
2. Entregar MVP com três nós (Phase 3).  
3. Estender com auditoria detalhada (Phase 4).  
4. Finalizar com polish e documentação (Phase 5).
