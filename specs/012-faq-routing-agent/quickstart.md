# Quickstart: FAQ Routing Agent

## Prerequisites
- Ative o ambiente virtual do repositório: `source venv/bin/activate` (Linux/macOS) ou `venv\Scripts\activate` (Windows).
- Copie `.env` de `agente_simples/.env` para `agente_perguntas/.env` e ajuste variáveis, se necessário (espera-se usar `GEMINI_API_KEY`).
- Instale dependências compartilhadas: `pip install -r requirements.txt`.

## Execução manual
1. No diretório raiz, execute:
   ```bash
   python agente_perguntas/main.py
   ```
2. O script executará automaticamente três perguntas de exemplo (duas respondidas, uma escalada). Quando a dúvida exigir encaminhamento, o console pedirá a mensagem e as notas do especialista (pressione Enter para usar o texto padrão).
3. Para experimentar manualmente após o fluxo automático, ajuste o código em `main.py` (se desejado) antes de rodar novamente.

## Simulação de inserção humana
- Quando uma dúvida não for respondida, o agente imprimirá os dados coletados para encaminhamento humano.
- Documentamos no README como registrar manualmente uma resposta humana (edição simples em linha de comando) para validar o fluxo sem implementar outro agente.

## Troubleshooting
- Se houver erro informando que o FAQ não foi carregado, confirme se `prompt.py` está no local esperado e se foi importado corretamente.
- Caso a chave da API não esteja definida, configure `GEMINI_API_KEY` no `.env` antes de executar.
