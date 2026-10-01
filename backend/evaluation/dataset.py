from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCase:
    """
    Represents one RAG evaluation case.
    """

    question: str
    expected_answer: str
    expected_keywords: tuple[str, ...]
    answerable: bool


EVALUATION_DATASET: tuple[EvaluationCase, ...] = (
    EvaluationCase(
        question="How long can medical leave without pay be granted?",
        expected_answer=("Medical leave without pay may be granted for no more than 12 months."),
        expected_keywords=("12 months",),
        answerable=True,
    ),
    EvaluationCase(
        question="What must an employee do before taking personal leave without pay?",
        expected_answer=(
            "The employee must provide a written request to the Benefits office "
            "and exhaust accrued annual leave."
        ),
        expected_keywords=(
            "written request",
            "Benefits office",
            "annual leave",
            "exhausted",
        ),
        answerable=True,
    ),
    EvaluationCase(
        question="What happens when an employee exhausts both sick leave and annual leave?",
        expected_answer=(
            "The employee is changed to hourly upon returning to work until "
            "10 days of sick leave and 10 days of annual leave have accrued."
        ),
        expected_keywords=(
            "hourly",
            "10 days",
            "sick",
            "annual leave",
        ),
        answerable=True,
    ),
    EvaluationCase(
        question="How long can personal leave of absence without pay last?",
        expected_answer=(
            "Personal leave without pay may be granted for no more than 12 consecutive months."
        ),
        expected_keywords=("12 consecutive months",),
        answerable=True,
    ),
    EvaluationCase(
        question="Who may require written approval for personal leave without pay?",
        expected_answer=("The President or the President's designee may require written approval."),
        expected_keywords=(
            "President",
            "designee",
            "written approval",
        ),
        answerable=True,
    ),
    EvaluationCase(
        question="Does the medical leave policy include FMLA leave?",
        expected_answer=(
            "Yes. The FMLA 12-week leave is included within medical leave without pay."
        ),
        expected_keywords=(
            "FMLA",
            "12-week",
            "included",
        ),
        answerable=True,
    ),
    EvaluationCase(
        question=(
            "Who is responsible for paying the employee portion of "
            "health insurance during medical leave?"
        ),
        expected_answer=(
            "The employee is responsible for paying their portion of "
            "health insurance and other benefits during the leave."
        ),
        expected_keywords=(
            "employee",
            "pay",
            "health insurance",
        ),
        answerable=True,
    ),
    EvaluationCase(
        question=(
            "What happens to an employee's employment status after both "
            "sick and annual leave are exhausted?"
        ),
        expected_answer=(
            "The employee is changed to hourly upon returning to work until "
            "10 days of sick leave and 10 days of annual leave have accrued."
        ),
        expected_keywords=(
            "hourly",
            "10 days",
            "sick",
            "annual leave",
        ),
        answerable=True,
    ),
    EvaluationCase(
        question=("Which office must receive a written request for personal leave without pay?"),
        expected_answer=("The written request must be provided to the Benefits office."),
        expected_keywords=(
            "Benefits office",
            "written request",
        ),
        answerable=True,
    ),
    EvaluationCase(
        question=("What condition must be met before personal leave without pay can be granted?"),
        expected_answer=("All accrued annual leave must be exhausted."),
        expected_keywords=(
            "accrued annual leave",
            "exhausted",
        ),
        answerable=True,
    ),
    EvaluationCase(
        question="How many vacation days does an employee receive each year?",
        expected_answer=("The information is not available in the provided documents."),
        expected_keywords=(
            "not available",
            "provided documents",
        ),
        answerable=False,
    ),
    EvaluationCase(
        question="What is the company's maternity leave policy?",
        expected_answer=("The information is not available in the provided documents."),
        expected_keywords=(
            "not available",
            "provided documents",
        ),
        answerable=False,
    ),
    EvaluationCase(
        question="What is the retirement age for employees?",
        expected_answer=("The information is not available in the provided documents."),
        expected_keywords=(
            "not available",
            "provided documents",
        ),
        answerable=False,
    ),
    EvaluationCase(
        question="How much does the company contribute to health insurance?",
        expected_answer=("The information is not available in the provided documents."),
        expected_keywords=(
            "not available",
            "provided documents",
        ),
        answerable=False,
    ),
)
