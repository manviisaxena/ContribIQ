import asyncio
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from sqlalchemy.dialects import postgresql


@pytest.fixture
def scoring(monkeypatch):
    from backend.core import config

    monkeypatch.setattr(config, "get_settings", lambda: SimpleNamespace(
        DATABASE_URL="postgresql+asyncpg://test:test@localhost/test",
        VALKEY_URL="redis://localhost:6379/0",
    ))
    return importlib.import_module("backend.worker.tasks.score_issues")


@pytest.mark.parametrize("issues", [
    [],
    [{"number": 1, "title": "Fix a.py", "body": "10 lines", "url": None,
      "labels": [], "files_affected": ["a.py"]}],
])
def test_scoring_refreshes_cache_and_removes_closed_issues(scoring, monkeypatch, issues):
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.get_file_content.return_value = "import os\n"
    session = AsyncMock()
    session.__aenter__.return_value = session
    monkeypatch.setattr(scoring, "GitHubClient", lambda **kwargs: client)
    monkeypatch.setattr(scoring, "fetch_open_issues", AsyncMock(return_value=issues))
    monkeypatch.setattr(scoring, "AsyncSessionLocal", lambda: session)

    result = asyncio.run(scoring.score_issues("owner", "repo"))
    assert result["scored"] == len(issues)
    statements = [call.args[0] for call in session.execute.call_args_list]
    delete = statements[-1].compile(dialect=postgresql.dialect())
    assert str(delete).startswith("DELETE FROM issues")
    assert "owner/repo" in delete.params.values()
    assert [issue["number"] for issue in issues] in delete.params.values()
    if issues:
        upsert = statements[0].compile(dialect=postgresql.dialect())
        assert "scored_at = now()" in str(upsert)
        assert 1 <= upsert.params["difficulty_m0"] <= 5
    session.commit.assert_awaited_once()


def test_source_fetch_failure_does_not_produce_successful_scores(scoring, monkeypatch):
    client = AsyncMock()
    client.__aenter__.return_value = client
    client.get_file_content.side_effect = httpx.ReadTimeout("timeout")
    database = AsyncMock()
    monkeypatch.setattr(scoring, "GitHubClient", lambda **kwargs: client)
    monkeypatch.setattr(scoring, "fetch_open_issues", AsyncMock(return_value=[
        {"number": 1, "files_affected": ["a.py"]}
    ]))
    monkeypatch.setattr(scoring, "AsyncSessionLocal", database)
    with pytest.raises(httpx.ReadTimeout):
        asyncio.run(scoring.score_issues("owner", "repo"))
    database.assert_not_called()


def test_source_sampling_ignores_unsupported_files_and_uses_byte_limit(scoring, caplog):
    client = SimpleNamespace(get_file_content=AsyncMock(return_value="é" * 150_000))
    sources = asyncio.run(scoring._load_sources(
        client, "owner", "repo", ["README.md", "a.py"], {"README.md", "a.py"}
    ))
    assert sources == {}
    client.get_file_content.assert_awaited_once_with("owner", "repo", "a.py")
    assert "size limit" in caplog.text
