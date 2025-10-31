# Agente com Aprovação Humana

O agente localizado em `agente_aprovacao/main.py` executa um fluxo LangGraph que valida os dados fornecidos, solicita aprovação humana antes de utilizar a ferramenta de pesquisa Tavily e gera respostas alternativas quando a autorização é negada.

## Fluxo resumido

1. **Validação** – a entrada do usuário é analisada; em caso de erro, o fluxo pausa e coleta correções sem encerrar a sessão.
2. **Aprovação humana** – quando a entrada é válida, o agente apresenta um resumo da ação proposta (consulta Tavily) e aguarda decisão do operador.
3. **Pesquisa (opcional)** – se autorizada, a ferramenta Tavily é executada e seus resultados são armazenados no estado.
4. **Resposta final** – o nó `gerar_resposta` gera a mensagem definitiva, informando se a pesquisa foi utilizada e listando observações relevantes. Se a entrada corresponder a uma expressão aritmética simples, o agente responde internamente sem solicitar aprovação. A execução encerra após esta segunda passagem pelo nó.

## Como executar

```bash
python agente_aprovacao/main.py
```

Durante a execução, o console solicitará:
- Nova entrada sempre que a validação falhar (até três tentativas).
- Uma decisão explícita (sim/não) quando a pesquisa precisar de aprovação.

## Cenários cobertos

- **Aprovação concedida** – a pesquisa externa é executada e a resposta final incorpora os resultados.
- **Entrada inválida** – o operador recebe instruções para corrigir os dados; o fluxo só prossegue após submissão válida.
- **Aprovação negada** – o agente retorna ao nó inicial, produz resposta sem Tavily e encerra informando que não usou ferramentas externas.
- **Expressão matemática** – operações como `1+1` são avaliadas internamente, sem consulta à Tavily ou aprovação humana.

Consulte `specs/017-approval-agent-flow/quickstart.md` para detalhes de teste manual e resultados esperados.
