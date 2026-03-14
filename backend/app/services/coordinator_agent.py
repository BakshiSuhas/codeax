from __future__ import annotations

from datetime import datetime

from app.models import AgentOutput, AnalysisResult, HealthBreakdown, Issue
from app.services.agent_engine import AgentEngine, PullRequestContext


class CoordinatorAgent:
    """AI Engineering Lead that selects and orchestrates specialist agents."""

    def __init__(self, engine: AgentEngine | None = None):
        self.engine = engine or AgentEngine()

    async def analyze(self, context: PullRequestContext) -> AnalysisResult:
        pr_type = self.engine.classify_pr_type(context)
        selected_agents = self.engine.choose_agents(context, pr_type)

        findings: list[Issue] = []
        generated_tests: list[str] = []
        docs_recommendations: list[str] = []
        dependency_risks: list[str] = []
        outputs: list[AgentOutput] = []

        code_review_findings = self.engine.run_code_review(context)
        findings.extend(Issue(**item) for item in code_review_findings)
        outputs.append(
            AgentOutput(
                name="code_review",
                status="completed",
                summary=f"{len(code_review_findings)} code review findings.",
            )
        )

        if "security" in selected_agents:
            security_findings = self.engine.run_security(context)
            findings.extend(Issue(**item) for item in security_findings)
            outputs.append(
                AgentOutput(
                    name="security",
                    status="completed",
                    summary=f"{len(security_findings)} security findings detected.",
                )
            )

        if "test_generator" in selected_agents:
            generated_tests = self.engine.run_test_generator(context)
            outputs.append(
                AgentOutput(
                    name="test_generator",
                    status="completed",
                    summary=f"{len(generated_tests)} generated test suggestions.",
                )
            )

        if "documentation_assistant" in selected_agents:
            docs_recommendations = self.engine.run_documentation_assistant(context)
            outputs.append(
                AgentOutput(
                    name="documentation_assistant",
                    status="completed",
                    summary="Documentation diff recommendations generated.",
                )
            )

        if "dependency_monitor" in selected_agents:
            dependency_risks = self.engine.run_dependency_monitor(context)
            outputs.append(
                AgentOutput(
                    name="dependency_monitor",
                    status="completed",
                    summary="Dependency risk scan completed.",
                )
            )

        fix_suggestions = self.engine.auto_fix_suggestions([item.model_dump() for item in findings])

        critical_count = len([f for f in findings if f.severity in ["critical", "high"]])
        medium_count = len([f for f in findings if f.severity == "medium"])
        quality_score = max(40, 95 - (medium_count * 8) - (critical_count * 18))
        security_score = max(35, 96 - (critical_count * 22) - (medium_count * 6))
        tests_score = 88 if generated_tests else 62
        technical_debt = max(20, 92 - quality_score)
        overall = max(0, min(100, round((quality_score + security_score + tests_score + (100 - technical_debt)) / 4)))

        recommendation = "No blocker issues. Proceed with merge after normal checks."
        if critical_count > 0:
            recommendation = "Block merge until high-severity issues are resolved."
        elif medium_count > 0:
            recommendation = "Address medium-risk findings before merge to improve stability."

        reasoning = (
            f"PR classified as {pr_type}. Selected agents: {', '.join(selected_agents)}. "
            f"Context: +{context.additions}/-{context.deletions} across {len(context.changed_files)} files."
        )

        return AnalysisResult(
            repository=context.repository,
            pr_number=context.number,
            pr_type=pr_type,
            score=overall,
            coordinator_reasoning=reasoning,
            findings=findings,
            generated_tests=generated_tests,
            auto_fix_suggestions=fix_suggestions,
            documentation_recommendations=docs_recommendations,
            dependency_risks=dependency_risks,
            recommendation=recommendation,
            health=HealthBreakdown(
                code_quality=quality_score,
                security=security_score,
                tests=tests_score,
                technical_debt=technical_debt,
                overall=overall,
            ),
            generated_at=datetime.utcnow(),
            agent_outputs=outputs,
        )
