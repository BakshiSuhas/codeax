from fastapi import APIRouter, HTTPException

from app.models import AnalysisResult
from app.services import AnalysisService, PullRequestContext

router = APIRouter()


@router.post("/{owner}/{repo}/{pr_number}", response_model=AnalysisResult)
async def analyze_pr(owner: str, repo: str, pr_number: int) -> AnalysisResult:
    context = PullRequestContext(
        repository=f"{owner}/{repo}",
        number=pr_number,
        title="Manual analysis trigger",
        body="",
        author="system",
        changed_files=[],
        additions=0,
        deletions=0,
    )
    return await AnalysisService().run_pull_request_analysis(context)


@router.get("/{owner}/{repo}/{pr_number}", response_model=AnalysisResult)
async def get_pr_analysis(owner: str, repo: str, pr_number: int) -> AnalysisResult:
    report = await AnalysisService().get_pull_request_analysis(owner, repo, pr_number)
    if not report:
        raise HTTPException(status_code=404, detail="Analysis report not found")
    return report


@router.get("/{owner}/{repo}", response_model=list[AnalysisResult])
async def list_repo_analyses(owner: str, repo: str) -> list[AnalysisResult]:
    return await AnalysisService().list_repository_analyses(owner, repo)
