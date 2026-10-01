from collections.abc import Iterable

from app.schemas.rag import RetrievedChunk


def calculate_keyword_score(
    answer: str,
    expected_keywords: Iterable[str],
) -> float:
    """
    Calculate how many expected keywords appear in the generated answer.
    """
    keywords = tuple(expected_keywords)

    if not keywords:
        return 1.0

    normalized_answer = answer.lower()

    matched = sum(1 for keyword in keywords if keyword.lower() in normalized_answer)

    return matched / len(keywords)


def calculate_retrieval_relevance(
    chunks: list[RetrievedChunk],
    expected_keywords: Iterable[str],
) -> float:
    """
    Calculate the proportion of retrieved chunks containing
    at least one expected keyword.
    """
    if not chunks:
        return 0.0

    keywords = tuple(keyword.lower() for keyword in expected_keywords)

    if not keywords:
        return 1.0

    relevant_chunks = 0

    for chunk in chunks:
        content = chunk.content.lower()

        if any(keyword in content for keyword in keywords):
            relevant_chunks += 1

    return relevant_chunks / len(chunks)


def calculate_average_retrieval_score(
    chunks: list[RetrievedChunk],
) -> float:
    """
    Calculate the average similarity score of retrieved chunks.
    """
    if not chunks:
        return 0.0

    return sum(chunk.score for chunk in chunks) / len(chunks)


def calculate_unique_document_ratio(
    chunks: list[RetrievedChunk],
) -> float:
    """
    Calculate the ratio of unique documents among retrieved chunks.
    """
    if not chunks:
        return 0.0

    unique_documents = {chunk.document_id for chunk in chunks}

    return len(unique_documents) / len(chunks)
