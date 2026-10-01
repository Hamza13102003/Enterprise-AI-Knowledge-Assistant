import asyncio
import json
import time
from pathlib import Path
from uuid import UUID

from app.embeddings.ollama import OllamaEmbeddingService
from app.llm.ollama import OllamaLLMService
from app.rag.context import RAGContextBuilder
from app.rag.prompt import RAGPromptBuilder
from app.rag.retriever import RAGRetriever
from app.rag.service import RAGService
from app.vector_store.qdrant import QdrantService
from evaluation.dataset import (
    EVALUATION_DATASET,
    EvaluationCase,
)
from evaluation.metrics import (
    calculate_average_retrieval_score,
    calculate_keyword_score,
    calculate_retrieval_relevance,
    calculate_unique_document_ratio,
)
from evaluation.results import EvaluationResult

REPORTS_DIRECTORY = Path(__file__).parent / "reports"
LATEST_REPORT_PATH = REPORTS_DIRECTORY / "latest_report.json"

MIN_OVERALL_PASS_RATE = 90.0
MIN_ANSWERABLE_PASS_RATE = 85.0
MIN_UNANSWERABLE_REFUSAL_PASS_RATE = 95.0


def create_rag_service() -> RAGService:
    """
    Create the same RAG service used by the application.
    """

    embedding_service = OllamaEmbeddingService()
    vector_store = QdrantService()

    retriever = RAGRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    context_builder = RAGContextBuilder()
    prompt_builder = RAGPromptBuilder()
    llm_service = OllamaLLMService()

    return RAGService(
        retriever=retriever,
        context_builder=context_builder,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )


def is_refusal_answer(answer: str) -> bool:
    """
    Determine whether the generated answer correctly indicates
    that the requested information is unavailable.
    """

    normalized = answer.lower().strip()

    refusal_phrases = (
        "the information is not available",
        "not available in the provided documents",
        "not provided in the documents",
        "not mentioned in the provided documents",
        "not specified in the provided documents",
        "does not contain information",
        "cannot be determined from the provided documents",
    )

    return any(
        phrase in normalized
        for phrase in refusal_phrases
    )


async def evaluate_case(
    service: RAGService,
    case: EvaluationCase,
    *,
    user_id: UUID,
) -> EvaluationResult:
    """
    Evaluate one RAG question.
    """

    start_time = time.perf_counter()

    response = await service.answer(
        case.question,
        user_id=user_id,
    )

    latency_seconds = time.perf_counter() - start_time

    keyword_score = calculate_keyword_score(
        response.answer,
        case.expected_keywords,
    )

    retrieval_relevance = calculate_retrieval_relevance(
        response.sources,
        case.expected_keywords,
    )

    average_retrieval_score = calculate_average_retrieval_score(
        response.sources,
    )

    unique_document_ratio = calculate_unique_document_ratio(
        response.sources,
    )

    if case.answerable:
        passed = (
            keyword_score >= 0.66
            and len(response.sources) > 0
        )
    else:
        passed = is_refusal_answer(
            response.answer
        )

    return EvaluationResult(
        question=case.question,
        expected_answer=case.expected_answer,
        generated_answer=response.answer,
        retrieved_chunks=len(response.sources),
        keyword_score=keyword_score,
        retrieval_relevance=retrieval_relevance,
        average_retrieval_score=average_retrieval_score,
        unique_document_ratio=unique_document_ratio,
        latency_seconds=latency_seconds,
        passed=passed,
        answerable=case.answerable,
    )


def calculate_pass_rate(
    results: list[EvaluationResult],
) -> float:
    """
    Calculate the percentage of passed evaluation cases.
    """

    if not results:
        return 0.0

    passed = sum(
        result.passed
        for result in results
    )

    return (passed / len(results)) * 100


def calculate_average(
    values: list[float],
) -> float:
    """
    Calculate an average safely.
    """

    if not values:
        return 0.0

    return sum(values) / len(values)


def build_summary(
    results: list[EvaluationResult],
) -> dict[str, int | float]:
    """
    Build aggregate metrics for the evaluation run.
    """

    answerable_results = [
        result
        for result in results
        if result.answerable
    ]

    unanswerable_results = [
        result
        for result in results
        if not result.answerable
    ]

    total = len(results)
    passed = sum(
        result.passed
        for result in results
    )

    return {
        "total_cases": total,
        "passed": passed,
        "failed": total - passed,
        "overall_pass_rate": calculate_pass_rate(
            results
        ),
        "answerable_pass_rate": calculate_pass_rate(
            answerable_results
        ),
        "unanswerable_refusal_pass_rate": calculate_pass_rate(
            unanswerable_results
        ),
        "average_keyword_score": calculate_average(
            [
                result.keyword_score
                for result in results
            ]
        ),
        "average_retrieval_relevance": calculate_average(
            [
                result.retrieval_relevance
                for result in results
            ]
        ),
        "average_retrieval_score": calculate_average(
            [
                result.average_retrieval_score
                for result in results
            ]
        ),
        "average_unique_document_ratio": calculate_average(
            [
                result.unique_document_ratio
                for result in results
            ]
        ),
        "average_latency_seconds": calculate_average(
            [
                result.latency_seconds
                for result in results
            ]
        ),
    }


def evaluate_regression_gate(
    summary: dict[str, int | float],
) -> bool:
    """
    Check whether the evaluation results meet the minimum
    acceptable quality thresholds.
    """

    overall_pass_rate = float(
        summary["overall_pass_rate"]
    )

    answerable_pass_rate = float(
        summary["answerable_pass_rate"]
    )

    unanswerable_refusal_pass_rate = float(
        summary["unanswerable_refusal_pass_rate"]
    )

    return (
        overall_pass_rate >= MIN_OVERALL_PASS_RATE
        and answerable_pass_rate >= MIN_ANSWERABLE_PASS_RATE
        and (
            unanswerable_refusal_pass_rate
            >= MIN_UNANSWERABLE_REFUSAL_PASS_RATE
        )
    )


def save_report(
    results: list[EvaluationResult],
    summary: dict[str, int | float],
    regression_gate_passed: bool,
) -> None:
    """
    Save the complete evaluation results to a JSON report.
    """

    REPORTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "quality_thresholds": {
            "minimum_overall_pass_rate": MIN_OVERALL_PASS_RATE,
            "minimum_answerable_pass_rate": MIN_ANSWERABLE_PASS_RATE,
            "minimum_unanswerable_refusal_pass_rate": (
                MIN_UNANSWERABLE_REFUSAL_PASS_RATE
            ),
        },
        "regression_gate_passed": regression_gate_passed,
        "summary": summary,
        "results": [
            result.to_dict()
            for result in results
        ],
    }

    with LATEST_REPORT_PATH.open(
        "w",
        encoding="utf-8",
    ) as report_file:
        json.dump(
            report,
            report_file,
            indent=2,
            ensure_ascii=False,
        )


def print_regression_gate(
    summary: dict[str, int | float],
    regression_gate_passed: bool,
) -> None:
    """
    Print the RAG evaluation regression gate results.
    """

    print()
    print("=" * 80)
    print("RAG REGRESSION GATE")
    print("=" * 80)

    overall_pass_rate = float(
        summary["overall_pass_rate"]
    )

    answerable_pass_rate = float(
        summary["answerable_pass_rate"]
    )

    unanswerable_refusal_pass_rate = float(
        summary["unanswerable_refusal_pass_rate"]
    )

    print(
        "Overall pass rate: "
        f"{overall_pass_rate:.2f}% "
        f"(minimum: {MIN_OVERALL_PASS_RATE:.2f}%)"
    )

    print(
        "Answerable pass rate: "
        f"{answerable_pass_rate:.2f}% "
        f"(minimum: {MIN_ANSWERABLE_PASS_RATE:.2f}%)"
    )

    print(
        "Unanswerable/refusal pass rate: "
        f"{unanswerable_refusal_pass_rate:.2f}% "
        f"(minimum: "
        f"{MIN_UNANSWERABLE_REFUSAL_PASS_RATE:.2f}%)"
    )

    print()

    if regression_gate_passed:
        print("REGRESSION GATE: PASSED")
    else:
        print("REGRESSION GATE: FAILED")


async def main() -> None:
    """
    Run the complete RAG evaluation dataset.
    """

    user_id = UUID(
        "79441b04-cffa-4598-90a1-af9c97532a61"
    )

    service = create_rag_service()

    results: list[EvaluationResult] = []

    for case in EVALUATION_DATASET:
        result = await evaluate_case(
            service,
            case,
            user_id=user_id,
        )

        results.append(result)

        print()
        print("=" * 80)
        print(f"QUESTION: {result.question}")
        print("=" * 80)

        print(
            f"Expected: "
            f"{result.expected_answer}"
        )

        print(
            f"Generated: "
            f"{result.generated_answer}"
        )

        print(
            f"Retrieved chunks: "
            f"{result.retrieved_chunks}"
        )

        print(
            f"Keyword score: "
            f"{result.keyword_score:.2f}"
        )

        print(
            f"Retrieval relevance: "
            f"{result.retrieval_relevance:.2f}"
        )

        print(
            f"Average retrieval score: "
            f"{result.average_retrieval_score:.3f}"
        )

        print(
            f"Unique document ratio: "
            f"{result.unique_document_ratio:.2f}"
        )

        print(
            f"Latency: "
            f"{result.latency_seconds:.3f}s"
        )

        print(
            f"Status: "
            f"{'PASS' if result.passed else 'FAIL'}"
        )

        print(
            f"Question type: "
            f"{'ANSWERABLE' if result.answerable else 'UNANSWERABLE'}"
        )

    summary = build_summary(
        results
    )

    regression_gate_passed = evaluate_regression_gate(
        summary
    )

    save_report(
        results,
        summary,
        regression_gate_passed,
    )

    print()
    print("=" * 80)
    print("RAG EVALUATION SUMMARY")
    print("=" * 80)

    print(
        f"Total cases: "
        f"{summary['total_cases']}"
    )

    print(
        f"Passed: "
        f"{summary['passed']}"
    )

    print(
        f"Failed: "
        f"{summary['failed']}"
    )

    print(
        f"Overall pass rate: "
        f"{summary['overall_pass_rate']:.2f}%"
    )

    print(
        f"Answerable pass rate: "
        f"{summary['answerable_pass_rate']:.2f}%"
    )

    print(
        "Unanswerable/refusal pass rate: "
        f"{summary['unanswerable_refusal_pass_rate']:.2f}%"
    )

    print(
        "Average keyword score: "
        f"{summary['average_keyword_score']:.3f}"
    )

    print(
        "Average retrieval relevance: "
        f"{summary['average_retrieval_relevance']:.3f}"
    )

    print(
        "Average retrieval score: "
        f"{summary['average_retrieval_score']:.3f}"
    )

    print(
        "Average unique document ratio: "
        f"{summary['average_unique_document_ratio']:.3f}"
    )

    print(
        "Average latency: "
        f"{summary['average_latency_seconds']:.3f}s"
    )

    print_regression_gate(
        summary,
        regression_gate_passed,
    )

    print()
    print(
        "Evaluation report saved to: "
        f"{LATEST_REPORT_PATH}"
    )

    if not regression_gate_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())