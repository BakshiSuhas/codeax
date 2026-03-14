from datetime import datetime

from pydantic import BaseModel, Field


class PullRequestModel(BaseModel):
    number: int
    repository: str
    title: str
    author: str
    status: str = Field(pattern="^(open|closed|merged|draft)$")
    additions: int = 0
    deletions: int = 0
    files_changed: int = 0
    updated_at: datetime
