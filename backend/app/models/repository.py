from pydantic import BaseModel, Field


class RepositoryHealth(BaseModel):
    code_quality: int = Field(ge=0, le=100)
    security: int = Field(ge=0, le=100)
    tests: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)


class RepositoryModel(BaseModel):
    owner: str
    name: str
    full_name: str
    description: str | None = None
    stars: int = 0
    language: str | None = None
    health: RepositoryHealth
