from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EvaluationResult:
    """
    Result of evaluating one RAG question.
    """

    question: str
    expected_answer: str
    generated_answer: str
    retrieved_chunks: int
    keyword_score: float
    retrieval_relevance: float
    average_retrieval_score: float
    unique_document_ratio: float
    latency_seconds: float
    passed: bool
    answerable: bool

    def to_dict(self) -> dict[str, object]:
        """
        Convert the evaluation result into a JSON-serializable dictionary.
        """

        return asdict(self)