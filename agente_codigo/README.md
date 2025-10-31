# Agente de Geração de Código em Memória

Este agente utiliza LangGraph para montar um loop iterativo com quatro nós principais: geração, execução, decisão e reflexão. Todo o ciclo roda em memória, imprimindo o progresso e o código final no console.

## Requisitos
- Python 3.12 no virtualenv do repositório.
- Dependências já instaladas (langgraph, langchain-core, langchain-google-genai, python-dotenv).
- Variável `GEMINI_API_KEY` configurada em `agente_codigo/.env`.

## Como executar
```bash
source venv/bin/activate
python agente_codigo/main.py
```

Para capturar stdout e stderr em arquivo enquanto acompanha no console:
```bash
python agente_codigo/main.py 2>&1 | tee run.log
```

## Fluxo do agente
1. **Geração**: invoca `gemini-2.5-flash`, recebe o histórico de mensagens e um feedback opcional de reflexão. Cada iteração incrementa `iteration_count`.
2. **Execução**: roda o código retornado com `exec` em memória, capturando stdout/stderr/tracebacks.
3. **Decisão**: encerra com sucesso quando `return_code == 0`, envia para reflexão em caso de erro ou finaliza ao atingir `MAX_ITERATIONS = 5`.
4. **Reflexão**: usa o LLM para sintetizar correções e alimenta a próxima geração.

Ao término, o console exibe um resumo com status, número de iterações e o código final.

## Exemplo de saída final
```
===== Resumo Final =====
Status: success
Iterações executadas: 2

--- Código final ---
# importações e implementações...
def run_demo():
    ...

if __name__ == "__main__":
    run_demo()
--- Fim do código final ---
```

## Ajustando o prompt inicial
- O prompt padrão está em `INITIAL_PROMPT` dentro de `agente_codigo/main.py`.
- Para testar outras tarefas, edite a string mantendo o formato de múltiplas linhas e salve. A alteração passa a valer na próxima execução.

## Observações
- Nenhum arquivo é criado durante o loop; todo conteúdo permanece em memória.
- Erros e feedbacks são impressos diretamente no console para facilitar depuração rápida.
