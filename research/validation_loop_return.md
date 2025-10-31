# Retornar ao Loop após Falha de Validação

## Consulta
- Pesquisa web: `"langgraph validation loop interrupt resume"` (31 de outubro de 2025)

## Principais achados
1. A documentação oficial de human-in-the-loop mostra que interrupções (`interrupt`) pausam o grafo, retornam controle ao operador humano e exigem um checkpointer para retomar a execução com `Command(resume=...)`. Isso permite validar entradas e reencaminhar para o mesmo nó após correções humanas. citeturn0search0
2. A mesma referência ilustra múltiplas interrupções sequenciais para validar dados antes de prosseguir, inclusive casos em que a visão humana ajusta entradas e o grafo continua do ponto em que parou. citeturn0search2
3. O guia discute como acionar comandos de retomada após a validação, garantindo que o fluxo retorne ao nó condicional pretendido em vez de encerrar a execução. citeturn0search3

## Aplicação ao agente de aprovação
- Utilizar `interrupt` no nó de aprovação humana para pausar a execução sempre que a validação falhar, enviando ao operador contexto sobre os erros detectados.
- Após o operador ajustar ou confirmar os dados, retomar o grafo com `Command(resume=...)` direcionando de volta ao nó inicial para nova validação até que os critérios sejam atendidos.
