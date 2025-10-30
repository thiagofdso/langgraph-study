"""Prompt utilities and embedded FAQ for the agente_perguntas project."""

from __future__ import annotations

import re
from typing import Iterable

FAQ_ENTRIES = [
    {
        "question": "Como altero minha senha?",
        "answer": (
            "Para alterar sua senha, acesse o portal do cliente, vá em Configurações » "
            "Segurança e siga as instruções de redefinição."
        ),
        "tags": ["senha", "seguranca"],
    },
    {
        "question": "Quais formas de pagamento vocês aceitam?",
        "answer": (
            "Aceitamos cartões de crédito Visa, MasterCard e Elo, além de PIX e boleto "
            "bancário para assinaturas anuais."
        ),
        "tags": ["pagamento", "assinatura"],
    },
    {
        "question": "Como posso acompanhar o status do meu pedido?",
        "answer": (
            "No painel principal, clique em 'Meus pedidos' e selecione o pedido desejado "
            "para visualizar os detalhes e estimativas de entrega."
        ),
        "tags": ["pedido", "status"],
    },
    {
        "question": "Posso cancelar a minha assinatura a qualquer momento?",
        "answer": (
            "Sim. Basta abrir o painel de assinaturas, escolher a assinatura ativa e "
            "clicar em 'Cancelar'. O acesso permanece até o fim do ciclo atual."
        ),
        "tags": ["cancelamento", "assinatura"],
    },
    {
        "question": "Onde encontro as notas fiscais das minhas compras?",
        "answer": (
            "As notas fiscais ficam disponíveis no menu 'Faturamento'. Você pode "
            "baixar cada documento em PDF."
        ),
        "tags": ["nota fiscal", "faturamento"],
    },
]

DEMO_QUESTIONS = [
    "Como altero minha senha?",
    "Quais formas de pagamento vocês aceitam?",
    "Vocês oferecem suporte 24 horas?",
]



TOKEN_PATTERN = re.compile(r'[\wÀ-ÿ]+')


def _tokenize(text: str) -> set[str]:
    """Return a normalized token set for similarity comparisons."""
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def score_similarity(user_question: str, candidate_question: str) -> float:
    """Compute token overlap ratio between user question and FAQ question."""
    user_tokens = _tokenize(user_question)
    candidate_tokens = _tokenize(candidate_question)
    if not user_tokens or not candidate_tokens:
        return 0.0
    intersection = user_tokens & candidate_tokens
    return len(intersection) / max(len(user_tokens), len(candidate_tokens))


def rank_faq_by_similarity(user_question: str) -> list[tuple[dict[str, str | list[str]], float]]:
    """Return FAQ entries paired with similarity score, sorted descending."""
    scored = []
    for entry in FAQ_ENTRIES:
        scored.append((entry, score_similarity(user_question, entry['question'])))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored

def build_system_prompt(confidence_threshold: float) -> str:
    """Return the system prompt with embedded FAQ and operating instructions."""
    faq_lines = []
    for entry in FAQ_ENTRIES:
        faq_lines.append(f"### {entry['question']}")
        faq_lines.append(entry["answer"])
        faq_lines.append("Tags: " + ", ".join(entry["tags"]))
        faq_lines.append("")

    faq_markdown = "\n".join(faq_lines).strip()
    return (
        "Você é um atendente virtual da Central Ajuda Fácil."
        "\n\n"
        "Regras:\n"
        "1. Utilize apenas o FAQ a seguir.\n"
        "2. Se a pergunta do usuário corresponder claramente a uma entrada do FAQ,"
        " responda com a resposta exata e informe a pontuação de confiança.\n"
        "3. Caso a similaridade fique abaixo de {threshold:.0%}, informe que a dúvida"
        " será encaminhada para um especialista humano.\n"
        "4. Sempre classifique o atendimento como 'respondido automaticamente' ou "
        "'encaminhar para humano'.\n"
        "5. Não invente informações.".format(threshold=confidence_threshold)
        + "\n\nFAQ:\n" + faq_markdown
    )


def list_faq_questions() -> list[str]:
    """Return only the FAQ questions for heuristic scoring."""
    return [entry["question"] for entry in FAQ_ENTRIES]


def get_faq_entries() -> list[dict[str, str | list[str]]]:
    """Expose FAQ entries for downstream processing (kept in sync with the prompt)."""
    return FAQ_ENTRIES
