# Guia de Operações e Solução de Problemas

Este guia fornece soluções para problemas comuns que você pode encontrar ao usar o Agente de Memória.

## Credenciais

**Problema**: O agente falha com um `ConfigurationError` relacionado a `GEMINI_API_KEY`.

**Solução**:
1. Certifique-se de ter um arquivo `.env` no diretório `agente_memoria`.
2. Caso contrário, copie o arquivo `.env.example` para `.env`:
   ```bash
   cp agente_memoria/.env.example agente_memoria/.env
   ```
3. Abra o arquivo `.env` e adicione sua chave de API do Gemini:
   ```
   GEMINI_API_KEY="sua-chave-de-api-aqui"
   ```

## Rede

**Problema**: O agente demora a responder ou excede o tempo limite.

**Solução**:
1. Verifique sua conexão com a internet.
2. A API do Gemini pode estar com alto tráfego. Tente novamente após alguns minutos.
3. Você pode aumentar o valor do tempo limite no arquivo `.env`:
   ```
   AGENT_TIMEOUT_SECONDS=60
   ```

## Latência

**Problema**: As respostas do agente são consistentemente lentas.

**Solução**:
1. Verifique o `duration_seconds` impresso após cada resposta para identificar se o problema está no modelo ou no processamento do agente.
2. Considere usar um modelo mais rápido, se disponível.

## Redefinindo a Memória

**Problema**: Você deseja iniciar uma nova conversa sem o contexto anterior.

**Solução**:
- Use o comando `/reset` na CLI para iniciar um novo tópico de conversa, limpando o histórico.
- Use o comando `/thread <novo-id-topico>` para mudar para um novo tópico de conversa.