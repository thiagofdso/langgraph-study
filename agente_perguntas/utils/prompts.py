"""Prompt helpers and embedded FAQ content for agente_perguntas."""

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict


class FAQEntry(TypedDict):
    """Structure describing a single FAQ item used by the agent."""

    question: str
    answer: str
    tags: list[str]


def _normalize(text: str) -> str:
    """Collapse extra whitespace and trim edges to keep FAQ entries consistent."""
    return " ".join(text.strip().split())


FAQ_ENTRIES: List[FAQEntry] = [
    {
        "question": _normalize("Como altero minha senha?"),
        "answer": _normalize(
            "Para alterar sua senha, acesse o portal do cliente, vá em Configurações » Segurança e siga as instruções de redefinição."
        ),
        "tags": ["senha", "seguranca"],
    },
    {
        "question": _normalize("Quais formas de pagamento vocês aceitam?"),
        "answer": _normalize(
            "Aceitamos cartões de crédito Visa, MasterCard e Elo, além de PIX e boleto bancário para assinaturas anuais."
        ),
        "tags": ["pagamento", "assinatura"],
    },
    {
        "question": _normalize("Como posso acompanhar o status do meu pedido?"),
        "answer": _normalize(
            "No painel principal, clique em 'Meus pedidos' e selecione o pedido desejado para visualizar os detalhes e estimativas de entrega."
        ),
        "tags": ["pedido", "status"],
    },
    {
        "question": _normalize("Posso cancelar a minha assinatura a qualquer momento?"),
        "answer": _normalize(
            "Sim. Basta abrir o painel de assinaturas, escolher a assinatura ativa e clicar em 'Cancelar'. O acesso permanece até o fim do ciclo atual."
        ),
        "tags": ["cancelamento", "assinatura"],
    },
    {
        "question": _normalize("Onde encontro as notas fiscais das minhas compras?"),
        "answer": _normalize(
            "As notas fiscais ficam disponíveis no menu 'Faturamento'. Você pode baixar cada documento em PDF."
        ),
        "tags": ["nota fiscal", "faturamento"],
    },
]

DEMO_QUESTIONS = [
    _normalize("Como altero minha senha?"),
    _normalize("Quais formas de pagamento vocês aceitam?"),
    _normalize("Vocês oferecem suporte 24 horas?"),
]


def get_faq_entries() -> list[FAQEntry]:
    """Return a shallow copy of the FAQ entries to avoid accidental mutation."""
    return [FAQEntry(question=item["question"], answer=item["answer"], tags=list(item["tags"])) for item in FAQ_ENTRIES]


def build_system_prompt(confidence_threshold: float) -> str:
    """Generate the system prompt with the FAQ embedded as Markdown."""
    faq_lines: list[str] = []
    for entry in FAQ_ENTRIES:
        faq_lines.append(f"### {entry['question']}")
        faq_lines.append(entry["answer"])
        faq_lines.append("Tags: " + ", ".join(entry["tags"]))
        faq_lines.append("")

    faq_markdown = "\n".join(faq_lines).strip()
    return (
        "Você é um atendente virtual da Central Ajuda Fácil."
        "\n\nRegras:\n"
        "1. Utilize apenas o FAQ a seguir."
        "\n2. Se a pergunta do usuário corresponder claramente a uma entrada do FAQ, responda com a resposta exata e informe a pontuação de confiança."
        "\n3. Caso a similaridade fique abaixo de {threshold:.0%}, informe que a dúvida será encaminhada para um especialista humano."
        "\n4. Sempre classifique o atendimento como 'respondido automaticamente' ou 'encaminhar para humano'."
        "\n5. Não invente informações."
    ).format(threshold=confidence_threshold) + "\n\nFAQ:\n" + faq_markdown


def list_faq_questions() -> list[str]:
    """Convenience helper exposing only FAQ questions for similarity tests."""
    return [entry["question"] for entry in FAQ_ENTRIES]


__all__ = [
    "FAQEntry",
    "FAQ_ENTRIES",
    "DEMO_QUESTIONS",
    "build_system_prompt",
    "get_faq_entries",
    "list_faq_questions",
]
