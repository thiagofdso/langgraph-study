# Quickstart – Simplified Code Generation Loop

1. **Preparar ambiente**
   ```bash
   source venv/bin/activate
   cp agente_simples/.env agente_codigo/.env
   ```
   > Garanta que `GEMINI_API_KEY` esteja configurado para o modelo `gemini-2.5-flash`.

2. **Executar agente**
   ```bash
   python agente_codigo/main.py
   ```
   - A execução dispara o grafo LangGraph com os nós de geração, execução, decisão e reflexão.
   - O prompt inicial é carregado automaticamente do estado inicial e solicita o script didático em uma única string.

3. **Capturar e revisar a saída**
   ```bash
   python agente_codigo/main.py 2>&1 | tee run.log
   ```
   - O comando acima salva `stdout` e `stderr` no arquivo `run.log` enquanto exibe o fluxo no console.
   - Após a execução, inspecione o arquivo para analisar erros ou o código final com calma.

4. **Acompanhar o loop**
   - O console exibe, por iteração, o contador, status da execução (`success` ou erro) e mensagens de reflexão quando aplicável.
   - O nó de decisão encerra imediatamente quando a execução retorna `return_code == 0` ou quando o contador atinge 5 tentativas.
   - Ao final, o script gerado é impresso integralmente no console para validação manual.

5. **Customizações rápidas**
   - Ajuste `MAX_ITERATIONS` e temperaturas do modelo diretamente em `agente_codigo/main.py` antes de rodar novamente.
   - Substitua o prompt inicial alterando o estado inicial configurado na função `main()` (mantendo o formato de string única).

6. **Limpeza**
   - Nenhum arquivo é criado durante o processo; basta encerrar o programa para reiniciar com um novo histórico.
