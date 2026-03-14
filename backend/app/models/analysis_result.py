from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AgentOutput(BaseModel):
    name: str
    status: str
    summary: str


class Issue(BaseModel):
    severity: Literal["critical", "high", "medium", "low", "info"]
    category: str
    title: str
    details: str


class HealthBreakdown(BaseModel):
    code_quality: int = Field(ge=0, le=100)
    security: int = Field(ge=0, le=100)
    tests: int = Field(ge=0, le=100)
    technical_debt: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)


class AnalysisResult(BaseModel):
    repository: str
    pr_number: int
    pr_type: str
    score: int = Field(ge=0, le=100)
    coordinator_reasoning: str
    findings: list[Issue] = Field(default_factory=list)
    generated_tests: list[str] = Field(default_factory=list)
    auto_fix_suggestions: list[str] = Field(default_factory=list)
    documentation_recommendations: list[str] = Field(default_factory=list)
    dependency_risks: list[str] = Field(default_factory=list)
    recommendation: str
    health: HealthBreakdown
    generated_at: datetime
    agent_outputs: list[AgentOutput] = Field(default_factory=list)
