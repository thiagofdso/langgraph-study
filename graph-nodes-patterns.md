# LangGraph Node Naming Patterns

Este documento consolida os nomes de nodes utilizados nos fluxos dos agentes atuais e descreve
suas responsabilidades. A meta é manter a nomenclatura consistente em futuros projetos.

## Padrões Compartilhados

| Nome do node | Responsabilidade | Implementações atuais |
| --- | --- | --- |
| `validate_input` | Validar a pergunta recebida, enriquecer `metadata` inicial e sinalizar o status de validação antes de outras etapas. | `agente_simples/graph.py#L15-L26`, `agente_memoria/graph.py#L21-L33` |
| `invoke_model` | Acionar o LLM configurado usando o histórico acumulado e capturar resposta ou falhas controladas; agentes podem injetar prompts auxiliares conforme a rodada. | `agente_simples/graph.py#L18-L28`, `agente_memoria/graph.py#L24-L33`, `agente_tool/graph.py#L34-L44` |
| `format_response` | Normalizar a saída final para o usuário, adicionando duração e ajustando status final. | `agente_simples/graph.py#L19-L29`, `agente_memoria/graph.py#L26-L33` |
| `prepare_image` | Validar a imagem recebida, criar fallback quando necessário e convertê-la para base64 antes da invocação do modelo. | `agente_imagem/graph.py`, `agente_imagem/utils/nodes.py` |

## Padrões Específicos por Agente

### agente_simples

| Nome do node | Função | Definição de utilitário |
| --- | --- | --- |
| `validate_input` | Cria metadata com a pergunta e o prompt do sistema, marcando o início da execução. | `agente_simples/utils/nodes.py#L20-L40` |
| `invoke_model` | Invoca o LLM com prompt estruturado e trata falhas de configuração ou execução. | `agente_simples/utils/nodes.py#L43-L79` |
| `format_response` | Ajusta a resposta final, avalia erros e calcula duração. | `agente_simples/utils/nodes.py#L82-L114` |

### agente_memoria

| Nome do node | Função | Definição de utilitário |
| --- | --- | --- |
| `validate_input` | Valida o texto da pergunta e adiciona timestamp para medir duração. | `agente_memoria/utils/nodes.py#L12-L35` |
| `load_history` | Recupera histórico da conversa usando o checkpointer configurado. | `agente_memoria/utils/nodes.py#L38-L47` |
| `invoke_model` | Invoca o LLM com o histórico completo, tratando exceções durante a chamada. | `agente_memoria/utils/nodes.py#L50-L69` |
| `update_memory` | Persiste o estado atualizado da conversa (delegado ao checkpointer). | `agente_memoria/utils/nodes.py#L72-L80` |
| `format_response` | Formata resposta final com duração e marca status concluído. | `agente_memoria/utils/nodes.py#L83-L96` |

### agente_tool

| Nome do node | Função | Definição de utilitário |
| --- | --- | --- |
| `validate_input` | Garante pergunta mínima, inicializa metadata com prompt do sistema e relógio de execução. | `agente_tool/utils/nodes.py#L97-L138` |
| `plan_tool_usage` | Agrupa todos os `tool_calls` emitidos pelo modelo em `ToolPlan` (nome, argumentos, call_id) para execução sequencial. | `agente_tool/utils/nodes.py#L141-L183` |
| `execute_tools` | Executa cada plano com a calculadora, gera `ToolMessage` pareada e registra resultados ou erros em `tool_calls`. | `agente_tool/utils/nodes.py#L185-L272` |
| `invoke_model` | Envia o histórico ao LLM: na primeira rodada inclui `system_prompt`; das rodadas seguintes em diante acrescenta `HumanMessage("Continue gerando sua resposta.")` antes de invocar. | `agente_tool/utils/nodes.py#L290-L360` |
| `format_response` | Formata a saída final, calcula duração e diferencia status de sucesso/erro. | `agente_tool/utils/nodes.py#L400-L439` |

### agente_imagem

| Nome do node | Função | Definição de utilitário |
| --- | --- | --- |
| `validate_input` | Escolhe a imagem alvo (usa sample se não for fornecida), inicializa metadata com `started_at` e caminho da imagem. | `agente_imagem/utils/nodes.py#L24-L47` |
| `prepare_image` | Verifica existência, valida formato e converte a imagem para base64, retornando erro amigável quando inválida. | `agente_imagem/utils/nodes.py#L50-L85` |
| `invoke_model` | Aciona o Gemini com prompt multimodal (texto + imagem base64) e captura a resposta textual estruturada. | `agente_imagem/utils/nodes.py#L88-L124` |
| `format_response` | Converte a resposta do LLM em markdown final, calcula duração e trata indicações de imagem inválida. | `agente_imagem/utils/nodes.py#L127-L159` |

### agente_banco_dados

| Nome do node | Função | Definição de utilitário |
| --- | --- | --- |
| `load_sales_metrics` | Consulta produtos e vendedores no SQLite, registrando quantos registros serão usados e qual o banco fonte. | `agente_banco_dados/utils/nodes.py` |
| `generate_insights` | Reúne métricas consolidadas, chama o Gemini para criar narrativa com três blocos e registra latência/erros da IA. | `agente_banco_dados/utils/nodes.py` |
| `render_sales_report` | Converte métricas em Markdown, anexa a seção de insights (ou fallback amigável) e adiciona metadata final. | `agente_banco_dados/utils/nodes.py` |
