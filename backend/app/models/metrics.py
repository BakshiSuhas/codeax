from datetime import datetime

from pydantic import BaseModel, Field


class HealthSnapshot(BaseModel):
    timestamp: datetime
    code_quality: int = Field(ge=0, le=100)
    security: int = Field(ge=0, le=100)
    tests: int = Field(ge=0, le=100)
    technical_debt: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)


class RepositoryInsight(BaseModel):
    repository: str
    vulnerabilities: int
    code_smells: int
    test_coverage: int = Field(ge=0, le=100)
    health_history: list[HealthSnapshot] = Field(default_factory=list)
