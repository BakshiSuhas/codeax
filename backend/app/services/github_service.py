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
    """Stub service that returns deterministic demo data."""

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

    async def list_repositories(self) -> list[RepositoryModel]:
        return [
            RepositoryModel(
                owner="octo-org",
                name="repoguardian-ai",
                full_name="octo-org/repoguardian-ai",
                description="AI review and security assistant",
                stars=314,
                language="TypeScript",
                health=RepositoryHealth(code_quality=84, security=88, tests=76, overall=83),
            ),
            RepositoryModel(
                owner="octo-org",
                name="platform-api",
                full_name="octo-org/platform-api",
                description="Core backend services",
                stars=198,
                language="Python",
                health=RepositoryHealth(code_quality=81, security=79, tests=73, overall=78),
            ),
        ]

    async def list_pull_requests(self, owner: str, repo: str) -> list[PullRequestModel]:
        repository_name = f"{owner}/{repo}"
        return [
            PullRequestModel(
                number=128,
                repository=repository_name,
                title="Harden webhook signature validation",
                author="nikhilk",
                status="open",
                additions=210,
                deletions=67,
                files_changed=9,
                updated_at=datetime.utcnow(),
            ),
            PullRequestModel(
                number=124,
                repository=repository_name,
                title="Improve dashboard loading skeleton",
                author="octocat",
                status="merged",
                additions=132,
                deletions=41,
                files_changed=6,
                updated_at=datetime.utcnow(),
            ),
        ]
