# Agente de Tarefas em 3 Rodadas

Projeto de estudo que demonstra um agente baseado em LangGraph executado no terminal para conduzir exatamente três interações consecutivas:

1. **Rodada 1** – coletar lista inicial de tarefas e exibi-las numeradas.
2. **Rodada 2** – permitir a seleção de uma tarefa para marcação como concluída.
3. **Rodada 3** – adicionar novas tarefas opcionais e apresentar um resumo final.

## Pré-requisitos
- Python 3.12.3 usando o virtualenv do repositório (`source venv/bin/activate`).
- Dependências instaladas com `pip install -r requirements.txt`.
- Arquivo `.env` nesta pasta com `GEMINI_API_KEY` e `GOOGLE_API_KEY` válidos (copie de `agente_simples/.env` e preencha suas chaves reais).

## Execução Rápida
```bash
PYTHONPATH=. python agente_tarefas/main.py
```

Durante a execução, o script vai:
- Esperar explicitamente pela entrada do usuário em cada rodada.
- Imprimir as falas como `Usuário:` e `Agente:` para facilitar a leitura.
- Perguntar como lidar com duplicatas adicionadas na terceira rodada.
- Encerrar automaticamente após o resumo da terceira rodada.

Para reiniciar, execute novamente o comando acima.
