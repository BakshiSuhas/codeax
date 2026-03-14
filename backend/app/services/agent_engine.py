from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PullRequestContext:
    repository: str
    number: int
    title: str
    body: str
    author: str
    changed_files: list[dict[str, str]]
    additions: int
    deletions: int


class AgentEngine:
    """Rule-based AI-like analyzers used when no external LLM is configured."""

    def classify_pr_type(self, ctx: PullRequestContext) -> str:
        title = ctx.title.lower()
        file_names = " ".join(file.get("filename", "").lower() for file in ctx.changed_files)
        if any(word in title for word in ["fix", "bug", "hotfix"]):
            return "bug_fix"
        if any(word in title for word in ["refactor", "cleanup", "chore"]):
            return "refactor"
        if any(word in title for word in ["security", "auth", "token"]):
            return "security_update"
        if any(word in file_names for word in ["auth", "login", "jwt", "oauth"]):
            return "security_update"
        return "feature"

    def choose_agents(self, ctx: PullRequestContext, pr_type: str) -> list[str]:
        agents = ["code_review"]
        changed = " ".join(file.get("filename", "").lower() for file in ctx.changed_files)
        if pr_type in ["feature", "bug_fix"] or ctx.additions > 80:
            agents.append("test_generator")
        if pr_type == "security_update" or any(x in changed for x in ["auth", "token", ".env", "secret"]):
            agents.append("security")
        if "docs" in changed:
            agents.append("documentation_assistant")
        if "package-lock" in changed or "requirements" in changed or "package.json" in changed:
            agents.append("dependency_monitor")
        return sorted(set(agents))

    def run_code_review(self, ctx: PullRequestContext) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        if ctx.additions > 250:
            findings.append({
                "severity": "medium",
                "category": "complexity",
                "title": "Large pull request may reduce review quality",
                "details": "Split this change into smaller pull requests where possible.",
            })
        for file in ctx.changed_files:
            patch = file.get("patch", "")
            if "except Exception" in patch and "raise" not in patch:
                findings.append({
                    "severity": "medium",
                    "category": "error_handling",
                    "title": f"Broad exception handling in {file.get('filename', 'file')}",
                    "details": "Catch explicit exceptions and preserve stack traces.",
                })
        if not findings:
            findings.append({
                "severity": "info",
                "category": "code_quality",
                "title": "No major code quality blockers detected",
                "details": "Keep functions small and explicit for maintainability.",
            })
        return findings

    def run_security(self, ctx: PullRequestContext) -> list[dict[str, str]]:
        findings: list[dict[str, str]] = []
        patterns = [
            ("high", "secrets", "Hardcoded key-like token", ["api_key", "secret", "ghp_", "AKIA"]),
            ("high", "injection", "Potential SQL string interpolation", ["SELECT", "WHERE", "f\"", "%s" ]),
        ]
        for file in ctx.changed_files:
            patch = file.get("patch", "")
            lowered = patch.lower()
            if any(token in lowered for token in ["api_key", "secret="]):
                findings.append({
                    "severity": "high",
                    "category": "secrets",
                    "title": f"Potential hardcoded secret in {file.get('filename', 'file')}",
                    "details": "Move credentials to environment variables or secret manager.",
                })
            if "select" in lowered and "+" in lowered and "where" in lowered:
                findings.append({
                    "severity": "high",
                    "category": "injection",
                    "title": f"Potential SQL injection risk in {file.get('filename', 'file')}",
                    "details": "Use parameterized SQL statements.",
                })
            if "password" in lowered and "log" in lowered:
                findings.append({
                    "severity": "medium",
                    "category": "sensitive_data",
                    "title": f"Sensitive data may be logged in {file.get('filename', 'file')}",
                    "details": "Avoid logging credentials or tokens.",
                })
        return findings

    def run_test_generator(self, ctx: PullRequestContext) -> list[str]:
        suggestions: list[str] = []
        for file in ctx.changed_files:
            filename = file.get("filename", "")
            if filename.endswith(".py"):
                suggestions.append(
                    "def test_new_behavior():\n    # TODO: cover success path\n    assert True"
                )
            if filename.endswith(".ts") or filename.endswith(".js"):
                suggestions.append(
                    "it('handles invalid input safely', () => {\n  expect(() => fn(undefined)).not.toThrow();\n});"
                )
            if len(suggestions) >= 2:
                break
        if not suggestions:
            suggestions.append("Add unit tests for modified modules and a regression test for the PR scenario.")
        return suggestions

    def run_documentation_assistant(self, ctx: PullRequestContext) -> list[str]:
        if any(file.get("filename", "").startswith("api/") for file in ctx.changed_files):
            return ["New API surface detected. Update README API section and examples."]
        return ["No documentation gaps detected from changed files."]

    def run_dependency_monitor(self, ctx: PullRequestContext) -> list[str]:
        if any("lodash" in file.get("patch", "") and "4.17.10" in file.get("patch", "") for file in ctx.changed_files):
            return ["Potential vulnerable lodash version detected. Upgrade to 4.17.21 or later."]
        return ["No high-risk dependency hints detected in changed lockfiles."]

    def auto_fix_suggestions(self, findings: list[dict[str, str]]) -> list[str]:
        suggestions: list[str] = []
        for finding in findings:
            category = finding.get("category", "")
            if category == "injection":
                suggestions.append("Use parameterized query style: cursor.execute('SELECT ... WHERE id = %s', (user_id,))")
            if category == "secrets":
                suggestions.append("Read secret values from environment variables and rotate exposed credentials.")
            if category == "error_handling":
                suggestions.append("Replace broad catches with explicit exception classes and re-raise context.")
        return suggestions
