import asyncio

import httpx
import pytest

from backend.services.github_client import GitHubClient, GitHubRateLimitError


def test_issues_follow_pagination_and_keep_open_filter():
    requests = []

    def handle(request):
        requests.append(request)
        assert request.url.params["state"] == "open"
        assert request.headers["Authorization"] == "Bearer test-token"
        if request.url.params["page"] == "1":
            return httpx.Response(200, json=[{"number": 1}], headers={
                "Link": '<https://api.github.com/repos/o/r/issues?page=2>; rel="next"'
            })
        return httpx.Response(200, json=[{"number": 2}])

    async def run():
        async with GitHubClient("test-token") as client:
            await client._http.aclose()
            client._http = httpx.AsyncClient(transport=httpx.MockTransport(handle))
            return await client.get_issues("o", "r")

    assert asyncio.run(run()) == [{"number": 1}, {"number": 2}]
    assert len(requests) == 2


@pytest.mark.parametrize("status,headers,expected", [
    (403, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "123"}, GitHubRateLimitError),
    (403, {"Retry-After": "60"}, GitHubRateLimitError),
    (429, {}, GitHubRateLimitError),
    (403, {}, httpx.HTTPStatusError),
    (500, {}, httpx.HTTPStatusError),
])
def test_api_failures_propagate_with_rate_limit_metadata(status, headers, expected):
    async def run():
        async with GitHubClient() as client:
            await client._http.aclose()
            client._http = httpx.AsyncClient(transport=httpx.MockTransport(
                lambda request: httpx.Response(status, headers=headers)
            ))
            await client.get_issues("o", "r")

    with pytest.raises(expected) as exc:
        asyncio.run(run())
    if expected is GitHubRateLimitError:
        assert exc.value.reset_at == headers.get("X-RateLimit-Reset")
        assert exc.value.retry_after == headers.get("Retry-After")


def test_last_successful_request_is_not_discarded_when_quota_reaches_zero():
    async def run():
        async with GitHubClient() as client:
            await client._http.aclose()
            client._http = httpx.AsyncClient(transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=[], headers={"X-RateLimit-Remaining": "0"})
            ))
            return await client.get_issues("o", "r")

    assert asyncio.run(run()) == []


def test_source_request_encodes_path_and_ref_and_handles_missing_files():
    def handle(request):
        assert request.url.path == "/repos/o/r/contents/src/a#b.py"
        assert request.url.params["ref"] == "feature/test"
        assert request.headers["Accept"] == "application/vnd.github.raw+json"
        return httpx.Response(200, text="import os\n")

    async def run():
        async with GitHubClient() as client:
            await client._http.aclose()
            client._http = httpx.AsyncClient(transport=httpx.MockTransport(handle))
            content = await client.get_file_content("o", "r", "src/a#b.py", ref="feature/test")
            await client._http.aclose()
            client._http = httpx.AsyncClient(transport=httpx.MockTransport(
                lambda request: httpx.Response(404)
            ))
            missing = await client.get_file_content("o", "r", "missing.py")
            return content, missing

    assert asyncio.run(run()) == ("import os\n", None)
