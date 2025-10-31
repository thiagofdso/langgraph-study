# Implementation Plan: Agente com Aprovação Humana

**Branch**: `017-approval-agent-flow` | **Date**: October 31, 2025 | **Spec**: [specs/017-approval-agent-flow/spec.md](specs/017-approval-agent-flow/spec.md)  
**Input**: Feature specification from `/specs/017-approval-agent-flow/spec.md`

**Note**: This plan é parte do fluxo specification-driven gerenciado pelo `.specify`. Consulte `.specify/templates/plan-template.md` para detalhes do processo.

## Summary

Vamos criar o projeto `agente_aprovacao` com um workflow LangGraph que: (1) valida a entrada do usuário e, em caso de falha, pausa via `interrupt` para coletar correções e retornar ao nó inicial; (2) exige aprovação humana antes de acionar a ferramenta de pesquisa reutilizada de `agente_web`; (3) ao receber aprovação, consulta a internet e gera uma resposta final; (4) se a aprovação for negada, volta diretamente para gerar uma resposta interna; (5) encerra a execução após a segunda passagem pelo nó `gerar_resposta`, informando se a ferramenta foi usada. O padrão de aprovação seguirá o exemplo de `agente_perguntas/main.py`, combinando `InMemorySaver`, `interrupt` e retomada com `Command(resume=...)`, conforme a documentação de human-in-the-loop do LangGraph. citeturn0search0turn0search2turn0search3

## Technical Context

**Language/Version**: Python 3.12.3  
**Primary Dependencies**: langgraph, langchain-core, google-generativeai (`ChatGoogleGenerativeAI`), langchain-tavily (`TavilySearch`), python-dotenv  
**Storage**: InMemorySaver (memória volátil para checkpoints)  
**Testing**: Apenas validação manual executando `python agente_aprovacao/main.py` (sem testes unitários ou de integração)  
**Target Platform**: Script CLI executado em ambiente Linux com acesso à internet  
**Project Type**: Agente single-run orquestrado por LangGraph  
**Performance Goals**: Responder em uma única execução linear, com no máximo duas chamadas ao nó `gerar_resposta` e uma consulta Tavily por execução autorizada  
**Constraints**: Sem parâmetros adicionais na CLI, nenhum loop interativo contínuo, reutilizar `.env` copiado de `agente_web`, registar decisão humana antes de qualquer ferramenta, resposta final sempre encerra o fluxo  
**Scale/Scope**: Uma sessão por execução; validação pode solicitar correções até o limite configurado (ex.: 3 tentativas) antes de cancelar

## Constitution Check

- **Principle I — Main File for Testing**: `agente_aprovacao/main.py` será o ponto de entrada usado para demonstração manual → **PASS**  
- **Principle IV — Standard LLM Model**: Usaremos `gemini-2.5-flash` ao gerar respostas internas → **PASS**  
- **Principle V — Standard Agent Framework**: Workflow implementado com LangGraph `StateGraph` e `InMemorySaver` → **PASS**  
- **Principle VII — Documentation & Comments**: Comentários pontuais explicarão lógica de interrupções/condicionais → **PASS**  
- **Principle XVII — Clarifying Technical Scope**: Plano define nós (`gerar_resposta`, `aprovacao_humana`, `busca_internet`) e comportamento condicional sem ambiguidades → **PASS**

## Project Structure

### Documentation (this feature)

```text
specs/017-approval-agent-flow/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── spec.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
agente_aprovacao/          # Novo agente com workflow de aprovação humana
agente_perguntas/          # Referência para padrão de aprovação via interrupt
agente_web/                # Fonte da ferramenta Tavily e .env de referência
external_docs/             # Documentação LangGraph (ex.: human-in-the-loop)
research/                  # Registros de pesquisas (ex.: validation_loop_return.md)
specs/                     # Especificações e planos das features
```

**Structure Decision**: Criar diretório `agente_aprovacao/` com `main.py`, módulo auxiliar (ex.: `workflow.py`), e sub-recursos necessários. Copiar `.env` de `agente_web` sem alterações. Reutilizar padrões de entrada/saida vistos em `agente_perguntas` para aprovação e em `agente_web` para busca, mantendo dependências compartilhadas no `requirements.txt` existente.

## Implementation Steps

1. **Setup do projeto**
   - Criar pasta `agente_aprovacao/` com `__init__.py`, `main.py`, `workflow.py`, e copiar `.env` de `agente_web`.
   - Definir `AgentState` (`TypedDict`) conforme data model, incluindo campos para controle de tentativas e estágios.
   - Inicializar `StateGraph` com `InMemorySaver`.

2. **Nó `gerar_resposta` (fase inicial e final)**
   - Implementar validação de entrada: normalizar pergunta, verificar campos obrigatórios, gerar mensagens de erro.
   - Em caso de falha, usar `interrupt` para solicitar correções e, ao retomar, incrementar `validation_attempts`; cancelar após exceder limite, produzindo resposta final sem ferramenta.
   - Quando válido e `response_stage == "initial"`, preparar síntese preliminar e sinalizar rota para aprovação humana; quando `response_stage == "final"`, montar resposta final (incluindo nota se ferramenta não foi usada) e direcionar para `END`.

3. **Nó `aprovacao_humana`**
   - Construir payload resumindo a ação proposta (consulta web) e os resultados da validação.
   - Invocar `interrupt` para obter decisão (`approved`, `reason`); registrar timestamp e atualizar estado.
   - Configurar condicional: `True` → `busca_internet`; `False` → `gerar_resposta` (final).

4. **Nó `busca_internet`**
   - Reaproveitar `TavilySearch` configurado em `agente_web` (mesmos parâmetros e uso do `.env`).
   - Executar busca quando aprovado, armazenando até 5 resultados e anexando notas se vazio ou falhar.

5. **Condicionais e fluxo**
   - Definir condicional a partir de `gerar_resposta`: primeira passagem encaminha para `aprovacao_humana`; segunda passagem encerra (`END`).
   - Garantir que negações ou cancelamentos atualizem `response_stage` para `"final"` antes de retornar.
   - Limitar tentativas de validação; em excedente, produzir resposta final avisando cancelamento.

6. **CLI e testes manuais**
   - Em `main.py`, carregar `.env`, instanciar workflow e executar `graph.invoke` ou `graph.stream` com `thread_id` fixo.
   - Incluir prompts no console para coleta de correções/aprovações, espelhando `agente_perguntas`.
   - Validar manualmente com `python agente_aprovacao/main.py`, cobrindo cenários: aprovação, negação e falha de validação.

## Complexity Tracking

Nenhuma exceção aos princípios constitucionais prevista no momento.
