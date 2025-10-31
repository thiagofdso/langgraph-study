# Phase 0 Research – Simplified Code Generation Loop

## Decision 1: Seguir o padrão do LangGraph Code Assistant
- **Rationale**: O tutorial oficial mostra como conectar nós de geração, execução e decisão em um `StateGraph`, exatamente o fluxo desejado. Reutilizar essa topologia reduz código customizado e facilita futura manutenção.
- **Alternatives considered**:
  - Implementar loop manual com `while`: perderíamos visibilidade e ferramentas de tracing do LangGraph.
  - Usar `MessageGraph`: limitaria o uso de campos adicionais (contador, código, erros) sem estruturas auxiliares.

## Decision 2: Manter código e histórico em memória
- **Rationale**: A nova especificação exige não gerar arquivos; portanto, o estado guardará a string de código atual, saída de execução e feedback da reflexão. Isso simplifica testes e evita limpar diretórios entre execuções.
- **Alternatives considered**:
  - Persistir arquivos temporários: aumentaria risco de lixo residual e contraria a orientação de manter tudo em memória.
  - Usar base de dados ou cache externo: complexidade desnecessária para um ciclo curto.

## Decision 3: Executar código via `exec` encapsulado
- **Rationale**: Como o código já está em memória, executar com `exec` em um namespace controlado fornece feedback imediato sem criar subprocessos. Capturar stdout/stderr com `io.StringIO` é suficiente para relatar erros ao nó de decisão.
- **Alternatives considered**:
  - `subprocess.run`: implicaria escrever script em disco ou passar via stdin, além de dificultar coleta incremental de saída.
  - Interpretadores externos (Pyodide/Docker): excedem o escopo desse agente local.

## Decision 4: Uso seletivo do LLM
- **Rationale**: Somente geração e reflexão dependem de criatividade do modelo; execução e decisão devem permanecer determinísticas para previsibilidade. Isso reduz custo e mantém controle sobre o fluxo.
- **Alternatives considered**:
  - LLM em todas as etapas: subiria custo e risco de respostas inconsistentes.
  - Automatizar reflexão com heurísticas: menos flexível para casos de erro variados reportados pela execução.

## Decision 5: Feedback em console ao invés de log persistente
- **Rationale**: Com tudo em memória, imprimir status por iteração fornece transparência suficiente conforme o objetivo de teste. Logs em arquivo seriam redundantes e violariam a restrição de não gravar no disco.
- **Alternatives considered**:
  - JSONL em disco: útil para auditoria, porém proibido nesta fase.
  - Telemetria externa: desnecessária para prototipagem local.
