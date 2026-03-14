from __future__ import annotations

from datetime import datetime
from typing import Any

from app.database import client

def _get_db():
    if client.client is None:
        raise RuntimeError("Database not initialized")
    return client.client.get_default_database()

async def save_analysis_report(repository: str, pr_number: int, report: dict[str, Any]) -> None:
    db = _get_db()
    query = {"repository": repository, "pr_number": pr_number}
    report["repository"] = repository
    report["pr_number"] = pr_number
    await db["analysis_reports"].replace_one(query, report, upsert=True)

async def get_analysis_report(repository: str, pr_number: int) -> dict[str, Any] | None:
    db = _get_db()
    report = await db["analysis_reports"].find_one({"repository": repository, "pr_number": pr_number})
    if report:
        report.pop("_id", None)
    return report

async def list_repository_reports(repository: str) -> list[dict[str, Any]]:
    db = _get_db()
    cursor = db["analysis_reports"].find({"repository": repository}).sort("generated_at", -1)
    results = await cursor.to_list(length=100)
    for r in results:
        r.pop("_id", None)
    return results

async def save_pull_request_snapshot(repository: str, pr_number: int, snapshot: dict[str, Any]) -> None:
    db = _get_db()
    query = {"repository": repository, "pr_number": pr_number}
    snapshot["repository"] = repository
    snapshot["pr_number"] = pr_number
    if "updated_at" not in snapshot:
         snapshot["updated_at"] = datetime.utcnow().isoformat()
    await db["pull_request_snapshots"].replace_one(query, snapshot, upsert=True)

async def list_pull_request_snapshots(repository: str) -> list[dict[str, Any]]:
    db = _get_db()
    cursor = db["pull_request_snapshots"].find({"repository": repository}).sort("updated_at", -1)
    results = await cursor.to_list(length=100)
    for r in results:
        r.pop("_id", None)
    return results

async def append_health_history(repository: str, health_snapshot: dict[str, Any]) -> None:
    db = _get_db()
    health_snapshot["repository"] = repository
    if "timestamp" not in health_snapshot:
        health_snapshot["timestamp"] = datetime.utcnow().isoformat()
    await db["health_history"].insert_one(health_snapshot)

async def get_health_history(repository: str) -> list[dict[str, Any]]:
    db = _get_db()
    cursor = db["health_history"].find({"repository": repository}).sort("timestamp", 1)
    results = await cursor.to_list(length=1000)
    for r in results:
        r.pop("_id", None)
    return results
