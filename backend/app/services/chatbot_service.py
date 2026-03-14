from __future__ import annotations

from app.models import ChatResponse
from app.services.analysis_service import AnalysisService
from app.services.github_service import GitHubService


class ChatbotService:
    def __init__(self, analysis_service: AnalysisService | None = None, github_service: GitHubService | None = None):
        self.analysis_service = analysis_service or AnalysisService()
        self.github_service = github_service or GitHubService()

    async def respond(self, message: str, owner: str | None = None, repo: str | None = None) -> ChatResponse:
        prompt = message.strip().lower()
        if not owner or not repo:
            repositories = await self.github_service.list_repositories()
            if not repositories:
                return ChatResponse(
                    answer="I could not find repositories yet. Connect your GitHub token and try again.",
                    suggestions=[
                        "Set GITHUB_TOKEN in .env",
                        "Ask: show repositories",
                        "Ask: health summary for owner/repo",
                    ],
                )
            first_repo = repositories[0]
            owner = first_repo.owner
            repo = first_repo.name

        repository = f"{owner}/{repo}"
        pull_requests = await self.github_service.list_pull_requests(owner, repo)
        analyses = await self.analysis_service.list_repository_analyses(owner, repo)
        insights = await self.analysis_service.get_repository_insights(owner, repo)

        latest_analysis = analyses[0] if analyses else None
        open_prs = [pr for pr in pull_requests if pr.status == "open"]
        high_severity_findings = [
            finding
            for analysis in analyses
            for finding in analysis.findings
            if finding.severity in ["critical", "high"]
        ]

        if "repo" in prompt and "list" in prompt:
            answer = f"Repository in context: {repository}. I can help with PR status, security risks, tests, and recommendations."
        elif "health" in prompt or "score" in prompt:
            answer = (
                f"Health summary for {repository}: overall coverage estimate is {insights.test_coverage}%, "
                f"detected vulnerabilities: {insights.vulnerabilities}, code smells: {insights.code_smells}."
            )
        elif "security" in prompt or "vulnerab" in prompt:
            answer = (
                f"Security view for {repository}: {len(high_severity_findings)} high or critical findings across stored analyses. "
                f"Current vulnerability count is {insights.vulnerabilities}."
            )
        elif "test" in prompt:
            if latest_analysis and latest_analysis.generated_tests:
                tests_preview = "; ".join(latest_analysis.generated_tests[:3])
                answer = f"Suggested tests from the latest analysis: {tests_preview}."
            else:
                answer = "No generated tests are stored yet. Trigger analysis on a PR to generate test suggestions."
        elif "pull" in prompt or "pr" in prompt:
            if open_prs:
                top = ", ".join([f"#{pr.number} {pr.title}" for pr in open_prs[:3]])
                answer = f"Open pull requests for {repository}: {top}."
            else:
                answer = f"No open pull requests found for {repository}."
        else:
            if latest_analysis:
                answer = (
                    f"Latest recommendation for {repository}: {latest_analysis.recommendation}. "
                    "You can ask about health, security, pull requests, or generated tests."
                )
            else:
                answer = (
                    f"I am connected to {repository}, but no analysis reports are stored yet. "
                    "Ask me about pull requests or trigger /api/analysis first."
                )

        return ChatResponse(
            answer=answer,
            suggestions=[
                "Show health summary",
                "Any security issues?",
                "List open pull requests",
                "What tests should we add?",
            ],
            context={
                "repository": repository,
                "pull_request_count": len(pull_requests),
                "open_pull_request_count": len(open_prs),
                "analysis_reports": len(analyses),
                "vulnerabilities": insights.vulnerabilities,
            },
        )
