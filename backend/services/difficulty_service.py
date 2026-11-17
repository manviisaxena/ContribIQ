from __future__ import annotations

import logging
import re
from statistics import mean
from typing import Any

import tree_sitter_python
from radon.complexity import cc_visit
from tree_sitter import Language, Parser

NEUTRAL = 3
logger = logging.getLogger(__name__)

_PY_PARSER = Parser(Language(tree_sitter_python.language()))
_IMPORT_NODES = {"import_statement", "import_from_statement", "future_import_statement"}

_HARD_KEYWORDS = (
    "auth", "oauth", "crypto", "encrypt", "security", "permission", "concurrency",
    "race condition", "deadlock", "performance", "memory leak", "scalab", "async",
    "migration", "protocol", "compiler", "parser", "kernel",
)
_EASY_KEYWORDS = ("typo", "docs", "documentation", "readme", "spelling", "comment", "rename")

_LINES = re.compile(r"(\d+)\s+lines?\b", re.IGNORECASE)


def _bucket(value: float, thresholds: tuple[float, ...]) -> int:
    for score, limit in enumerate(thresholds, start=1):
        if value <= limit:
            return score
    return len(thresholds) + 1


def score_files_affected(files: list[str]) -> int:
    if not files:
        return NEUTRAL
    return _bucket(len(files), (1, 2, 4, 7))


def average_complexity(sources: dict[str, str]) -> float | None:
    values: list[float] = []
    for path, code in sources.items():
        if not path.endswith(".py"):
            continue
        try:
            blocks = cc_visit(code)
        except (SyntaxError, ValueError) as exc:
            logger.warning("Cannot measure Python complexity for %s: %s", path, exc)
            continue
        if blocks:
            values.append(mean(block.complexity for block in blocks))
        else:
            values.append(1)
    return mean(values) if values else None


def score_complexity(sources: dict[str, str]) -> int:
    avg = average_complexity(sources)
    if avg is None:
        return NEUTRAL
    return _bucket(avg, (3, 5, 10, 20))


def count_imports(code: str) -> int:
    tree = _PY_PARSER.parse(code.encode("utf-8"))
    count = 0
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type in _IMPORT_NODES:
            count += 1
            continue
        stack.extend(node.children)
    return count


def score_dependencies(sources: dict[str, str]) -> int:
    counts = [count_imports(code) for path, code in sources.items() if path.endswith(".py")]
    if not counts:
        return NEUTRAL
    return _bucket(mean(counts), (3, 8, 15, 25))


def score_domain_knowledge(title: str, body: str, labels: list[str]) -> int:
    text = f"{title}\n{body}\n{' '.join(labels)}".lower()
    hard = sum(1 for keyword in _HARD_KEYWORDS if keyword in text)
    easy = sum(1 for keyword in _EASY_KEYWORDS if keyword in text)
    return max(1, min(5, 2 + hard - easy))


def estimate_lines(title: str, body: str) -> int:
    explicit = [int(n) for n in _LINES.findall(f"{title}\n{body}")]
    if explicit:
        return max(explicit)
    return max(5, len(body) // 4)


def score_estimated_lines(lines: int) -> int:
    return _bucket(lines, (10, 40, 150, 400))


def estimate_hours(lines: int, files: int) -> float:
    return round(max(0.5, lines / 25 + max(files, 1) * 0.5), 1)


def score_issue(issue: dict[str, Any], sources: dict[str, str]) -> dict[str, Any]:
    """Score an issue 1–5 (higher is harder) as the mean of five factors."""
    title, body = issue.get("title", ""), issue.get("body", "")
    files = issue.get("files_affected", [])
    lines = estimate_lines(title, body)

    factors = {
        "files_affected": score_files_affected(files),
        "complexity": score_complexity(sources),
        "dependencies": score_dependencies(sources),
        "domain_knowledge": score_domain_knowledge(title, body, issue.get("labels", [])),
        "estimated_lines": score_estimated_lines(lines),
    }
    return {
        "difficulty": round(mean(factors.values()), 2),
        "difficulty_factors": factors,
        "estimated_hours": estimate_hours(lines, len(files)),
    }
