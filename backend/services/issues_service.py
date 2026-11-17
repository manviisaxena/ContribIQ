from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.services.github_client import GitHubClient

_FILE_PATH = re.compile(
    r"(?<![\w/.-])((?:[\w.-]+/)*[\w.-]+\.(?:py|js|jsx|ts|tsx|go|rs|java|kt|rb|php|c|cc|cpp|h|hpp|cs|swift|md|json|ya?ml|toml))\b"
)
_URL = re.compile(r"https?://\S+")


def extract_file_paths(text: str | None) -> list[str]:
    """Return unique file paths mentioned in free text, in order of appearance."""
    if not text:
        return []
    text = _URL.sub(" ", text)
    seen: dict[str, None] = {}
    for match in _FILE_PATH.finditer(text):
        seen.setdefault(match.group(1), None)
    return list(seen)


def normalize_issue(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": raw["number"],
        "title": raw.get("title") or "",
        "body": raw.get("body") or "",
        "url": raw.get("html_url"),
        "labels": [
            (label["name"] if isinstance(label, dict) else str(label))
            for label in raw.get("labels", [])
        ],
        "files_affected": extract_file_paths(f"{raw.get('title') or ''}\n{raw.get('body') or ''}"),
    }


async def fetch_open_issues(
    client: GitHubClient, owner: str, name: str
) -> list[dict[str, Any]]:
    """Fetch open issues, excluding pull requests (GitHub lists PRs as issues)."""
    raw_issues = await client.get_issues(owner, name, state="open")
    return [
        normalize_issue(raw)
        for raw in raw_issues
        if "pull_request" not in raw and raw.get("state", "open") == "open"
    ]
