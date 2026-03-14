import hashlib
import hmac
import time
import jwt
from datetime import datetime
from typing import Any

import httpx

from app.config import settings
from app.database.state import save_pull_request_snapshot
from app.services.agent_engine import PullRequestContext

from app.models import PullRequestModel, RepositoryHealth, RepositoryModel


class GitHubService:
    """GitHub integration service for live data."""

    async def _get_app_jwt(self) -> str:
        if not settings.github_private_key_path or not settings.github_app_id:
            return ""
        with open(settings.github_private_key_path, "r") as key_file:
            private_key = key_file.read()
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + (10 * 60),
            "iss": settings.github_app_id,
        }
        return jwt.encode(payload, private_key, algorithm="RS256")

    async def _get_installation_token(self, owner: str, repo: str) -> str:
        if settings.github_token: # Fallback to static token if provided
            return settings.github_token
            
        app_jwt = await self._get_app_jwt()
        if not app_jwt:
            return ""
            
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient(timeout=15) as client:
            # First get the installation ID for the repo
            resp = await client.get(
                f"{settings.github_api_base_url}/repos/{owner}/{repo}/installation",
                headers=headers
            )
            if resp.status_code != 200:
                print(f"Could not get installation for {owner}/{repo}: {resp.text}")
                return ""
                
            installation_id = resp.json().get("id")
            
            # Now get the token for that installation
            token_resp = await client.post(
                f"{settings.github_api_base_url}/app/installations/{installation_id}/access_tokens",
                headers=headers
            )
            token_resp.raise_for_status()
            return token_resp.json().get("token", "")

    def is_valid_webhook_signature(self, payload_body: bytes, signature_header: str | None) -> bool:
        if not settings.github_webhook_secret:
            return True
        if not signature_header:
            return False
        digest = hmac.new(settings.github_webhook_secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
        expected = f"sha256={digest}"
        return hmac.compare_digest(expected, signature_header)

    async def build_context_from_webhook_payload(self, payload: dict[str, Any]) -> PullRequestContext | None:
        pr = payload.get("pull_request")
        repo = payload.get("repository")
        if not pr or not repo:
            return None

        changed_files: list[dict[str, str]] = []
        for file in pr.get("_files", []):
            changed_files.append(
                {
                    "filename": file.get("filename", ""),
                    "patch": file.get("patch", ""),
                }
            )

        repository_name = repo.get("full_name", f"{repo.get('owner', {}).get('login', 'unknown')}/{repo.get('name', 'repo')}")
        snapshot = {
            "number": pr.get("number", 0),
            "repository": repository_name,
            "title": pr.get("title", ""),
            "author": pr.get("user", {}).get("login", "unknown"),
            "status": "open" if pr.get("state") == "open" else "closed",
            "additions": pr.get("additions", 0),
            "deletions": pr.get("deletions", 0),
            "files_changed": pr.get("changed_files", len(changed_files)),
            "updated_at": datetime.utcnow().isoformat(),
        }
        await save_pull_request_snapshot(repository_name, snapshot["number"], snapshot)

        return PullRequestContext(
            repository=repository_name,
            number=pr.get("number", 0),
            title=pr.get("title", ""),
            body=pr.get("body", ""),
            author=pr.get("user", {}).get("login", "unknown"),
            changed_files=changed_files,
            additions=pr.get("additions", 0),
            deletions=pr.get("deletions", 0),
        )

    async def post_pull_request_comment(self, repository: str, pr_number: int, comment_body: str) -> bool:
        if not repository or "/" not in repository:
            return False

        owner, repo = repository.split("/", 1)
        token = await self._get_installation_token(owner, repo)
        
        if not token:
            print("No GitHub token available. Skipping comment.")
            return False

        url = f"{settings.github_api_base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        payload = {"body": comment_body}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.status_code in [200, 201]

    async def _get_auth_headers(self, owner: str | None = None, repo: str | None = None) -> dict[str, str]:
        """
        Prefer a static GitHub token when provided; otherwise fall back to GitHub App installation tokens.
        """
        token = settings.github_token
        if not token and owner and repo:
            token = await self._get_installation_token(owner, repo)

        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def list_repositories(self) -> list[RepositoryModel]:
        """
        Return live repositories for the authenticated user/org when possible.
        Falls back gracefully to an empty list if GitHub is unreachable.
        """
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # Use the "current user repos" endpoint; respects the provided token scopes.
                resp = await client.get(
                    f"{settings.github_api_base_url}/user/repos",
                    headers=await self._get_auth_headers(),
                    params={"per_page": 50, "sort": "pushed"},
                )
                if resp.status_code != 200:
                    print(f"GitHub list_repositories error: {resp.status_code} {resp.text}")
                    return []

                repos: list[RepositoryModel] = []
                for item in resp.json():
                    owner_login = item.get("owner", {}).get("login", "")
                    name = item.get("name", "")
                    full_name = item.get("full_name", f"{owner_login}/{name}")
                    description = item.get("description")
                    stars = item.get("stargazers_count", 0)
                    language = item.get("language")
                    # Health is derived from analysis history; start neutral for new repos.
                    health = RepositoryHealth(code_quality=80, security=80, tests=70, overall=78)
                    repos.append(
                        RepositoryModel(
                            owner=owner_login,
                            name=name,
                            full_name=full_name,
                            description=description,
                            stars=stars,
                            language=language,
                            health=health,
                        )
                    )
                return repos
        except Exception as exc:  # pragma: no cover - best‑effort logging
            print(f"GitHub list_repositories exception: {exc}")
            return []

    async def list_pull_requests(self, owner: str, repo: str) -> list[PullRequestModel]:
        """
        Return live pull requests for the given repository from GitHub.
        """
        repository_name = f"{owner}/{repo}"
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    f"{settings.github_api_base_url}/repos/{owner}/{repo}/pulls",
                    headers=await self._get_auth_headers(owner, repo),
                    params={"state": "all", "per_page": 50},
                )
                if resp.status_code != 200:
                    print(f"GitHub list_pull_requests error: {resp.status_code} {resp.text}")
                    return []

                items = resp.json()
                pull_requests: list[PullRequestModel] = []
                for pr in items:
                    status = "open"
                    if pr.get("draft"):
                        status = "draft"
                    elif pr.get("merged_at"):
                        status = "merged"
                    elif pr.get("state") == "closed":
                        status = "closed"

                    # GitHub includes additions/deletions/changed_files on single-PR endpoint; guard with defaults here.
                    pull_requests.append(
                        PullRequestModel(
                            number=pr.get("number", 0),
                            repository=repository_name,
                            title=pr.get("title", ""),
                            author=pr.get("user", {}).get("login", "unknown"),
                            status=status,
                            additions=pr.get("additions", 0),
                            deletions=pr.get("deletions", 0),
                            files_changed=pr.get("changed_files", 0),
                            updated_at=pr.get("updated_at", datetime.utcnow()),
                        )
                    )
                return pull_requests
        except Exception as exc:  # pragma: no cover - best‑effort logging
            print(f"GitHub list_pull_requests exception: {exc}")
            return []
