"""Rule-based summarization for pasted class instructions.

The goal is not to replace careful reading. It creates a calmer first pass:
what the assignment appears to ask for, what must be included, and what to
check before submitting.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from textwrap import shorten


REQUIREMENT_MARKERS = (
    "must",
    "required",
    "requirement",
    "requirements",
    "include",
    "submit",
    "submission",
    "deliverable",
    "deliverables",
    "write",
    "create",
    "complete",
    "provide",
    "cite",
    "citation",
    "references",
    "apa",
    "mla",
    "minimum",
    "maximum",
    "at least",
    "no more than",
    "pages",
    "words",
    "format",
    "due",
    "deadline",
    "upload",
    "attach",
    "discussion",
    "reply",
    "responses",
    "rubric",
    "grade",
    "points",
)

DATE_PATTERNS = (
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:,\s*\d{4})?\b",
    r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b",
    r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
    r"\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b",
    r"\b(?:11:59|midnight|noon)\s*(?:PM|AM|pm|am)?\b",
)


@dataclass(frozen=True)
class SummaryResult:
    title: str
    overview: list[str]
    requirements: list[str]
    dates: list[str]
    submission: list[str]
    citations_formatting: list[str]
    grading: list[str]
    questions: list[str]

    def to_markdown(self) -> str:
        sections = [
            ("Assignment", [self.title]),
            ("Quick Summary", self.overview),
            ("Requirements Checklist", [f"[ ] {item}" for item in self.requirements]),
            ("Due Dates / Timing", self.dates),
            ("Submission Details", self.submission),
            ("Citation / Formatting Rules", self.citations_formatting),
            ("Grading / Rubric Clues", self.grading),
            ("Questions To Confirm", self.questions),
        ]

        lines: list[str] = []
        for heading, items in sections:
            if not items:
                continue
            lines.append(f"## {heading}")
            for item in items:
                prefix = "- " if heading != "Assignment" else ""
                lines.append(f"{prefix}{item}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"


def summarize_instructions(raw_text: str) -> SummaryResult:
    text = normalize_text(raw_text)
    if not text:
        return SummaryResult(
            title="No instructions pasted yet",
            overview=["Paste assignment instructions on the left, then click Condense."],
            requirements=[],
            dates=[],
            submission=[],
            citations_formatting=[],
            grading=[],
            questions=[],
        )

    lines = extract_lines(text)
    sentences = split_sentences(text)
    title = infer_title(lines)

    requirement_candidates = collect_requirement_lines(lines, sentences)
    dates = find_matching_items(lines, sentences, DATE_PATTERNS)
    submission = filter_by_keywords(
        requirement_candidates,
        ("submit", "submission", "upload", "attach", "file", "docx", "pdf", "reply"),
    )
    citations = filter_by_keywords(
        requirement_candidates,
        ("cite", "citation", "reference", "apa", "mla", "format", "font", "spacing", "page", "word"),
    )
    grading = filter_by_keywords(lines + sentences, ("rubric", "points", "grade", "graded", "score", "criteria"))

    requirements = dedupe_preserve_order(
        item
        for item in requirement_candidates
        if item.lower() != title.lower()
    )
    requirements = requirements[:18]

    overview = build_overview(sentences, requirements, title)
    questions = build_questions(text, dates, submission, citations)

    return SummaryResult(
        title=title,
        overview=overview,
        requirements=requirements or ["Review the original instructions and identify the concrete deliverables."],
        dates=dates[:8],
        submission=submission[:8],
        citations_formatting=citations[:8],
        grading=dedupe_preserve_order(grading)[:8],
        questions=questions,
    )


def normalize_text(raw_text: str) -> str:
    cleaned = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_lines(text: str) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = normalize_bullet(raw_line.strip())
        if line:
            lines.append(line)
    return dedupe_preserve_order(lines)


def normalize_bullet(line: str) -> str:
    line = re.sub(r"^[\s>*\u2022\u2013\u2014-]+", "", line)
    line = re.sub(r"^\(?[A-Za-z0-9]{1,3}[\).]\s+", "", line)
    return line.strip()


def split_sentences(text: str) -> list[str]:
    compact = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", compact)
    return dedupe_preserve_order(part.strip() for part in parts if len(part.strip()) > 20)


def infer_title(lines: list[str]) -> str:
    for line in lines[:8]:
        lowered = line.lower()
        if len(line) <= 90 and not lowered.startswith(("overview", "instructions", "description")):
            if any(word in lowered for word in ("assignment", "discussion", "project", "paper", "case", "worksheet", "module", "week")):
                return line
    return "Class Assignment"


def collect_requirement_lines(lines: list[str], sentences: list[str]) -> list[str]:
    pool = []
    for item in lines + sentences:
        lowered = item.lower()
        has_marker = any(marker in lowered for marker in REQUIREMENT_MARKERS)
        looks_like_instruction = bool(
            re.match(r"^(write|create|submit|include|complete|provide|describe|explain|analyze|compare|identify)\b", lowered)
        )
        has_quantity = bool(re.search(r"\b\d+\s*(?:pages?|words?|sources?|references?|replies|responses?|paragraphs?|slides?)\b", lowered))
        if has_marker or looks_like_instruction or has_quantity:
            pool.append(clean_item(item))
    return dedupe_preserve_order(pool)


def find_matching_items(lines: list[str], sentences: list[str], patterns: tuple[str, ...]) -> list[str]:
    combined = lines + sentences
    matches = []
    for item in combined:
        if any(re.search(pattern, item, flags=re.IGNORECASE) for pattern in patterns):
            matches.append(clean_item(item))
    return dedupe_preserve_order(matches)


def filter_by_keywords(items: list[str], keywords: tuple[str, ...]) -> list[str]:
    return dedupe_preserve_order(
        clean_item(item)
        for item in items
        if any(keyword in item.lower() for keyword in keywords)
    )


def build_overview(sentences: list[str], requirements: list[str], title: str) -> list[str]:
    useful = [
        clean_item(sentence)
        for sentence in sentences
        if 45 <= len(sentence) <= 260
        and not any(skip in sentence.lower() for skip in ("copyright", "privacy", "cookie"))
    ]

    overview = useful[:3]
    if not overview and requirements:
        overview = [f"This appears to be about {title}. Main action: {requirements[0]}"]

    return [shorten(item, width=240, placeholder="...") for item in overview[:3]]


def build_questions(text: str, dates: list[str], submission: list[str], citations: list[str]) -> list[str]:
    questions = []
    lowered = text.lower()
    if not dates and any(word in lowered for word in ("due", "deadline", "submit")):
        questions.append("Confirm the exact due date and time.")
    if not submission:
        questions.append("Confirm where and how the assignment should be submitted.")
    if "source" in lowered and not citations:
        questions.append("Confirm the required citation style and number of sources.")
    if not any(word in lowered for word in ("rubric", "points", "grade", "criteria")):
        questions.append("Check the course rubric for grading details.")
    return questions[:5]


def clean_item(item: str) -> str:
    item = normalize_bullet(item)
    item = re.sub(r"\s+", " ", item)
    return item.strip(" -")


def dedupe_preserve_order(items) -> list[str]:
    seen = set()
    result = []
    for item in items:
        cleaned = clean_item(str(item))
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result
