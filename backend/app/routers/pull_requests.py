from fastapi import APIRouter

from app.database.state import list_pull_request_snapshots
from app.models import PullRequestModel
from app.services import GitHubService

router = APIRouter()


@router.get("/{owner}/{repo}", response_model=list[PullRequestModel])
async def list_pull_requests(owner: str, repo: str) -> list[PullRequestModel]:
    repository = f"{owner}/{repo}"
    snapshots = await list_pull_request_snapshots(repository)
    if snapshots:
        return [PullRequestModel(**snapshot) for snapshot in snapshots]
    return await GitHubService().list_pull_requests(owner, repo)
