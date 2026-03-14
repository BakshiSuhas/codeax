"use client";

import { useEffect, useMemo, useState } from "react";

import { SectionCard } from "@/components/common/section-card";
import { MetricCard } from "@/components/ui/metric-card";
import { fetchJson } from "@/lib/api";

type Repo = {
  full_name: string;
  language?: string | null;
  stars: number;
  health: {
    overall: number;
  };
};

type DashboardMetric = {
  label: string;
  value: string;
  delta: string;
  trend: "up" | "down";
};

export default function DashboardPage() {
  const [repos, setRepos] = useState<Repo[]>([]);
  const [loadingRepos, setLoadingRepos] = useState(true);
  const [reposError, setReposError] = useState<string>("");

  useEffect(() => {
    setLoadingRepos(true);
    setReposError("");
    fetchJson<Repo[]>("/api/repositories/")
      .then((data) => setRepos(data))
      .catch(() => setReposError("Unable to load repositories from backend."))
      .finally(() => setLoadingRepos(false));
  }, []);

  const metrics: DashboardMetric[] = useMemo(() => {
    if (!repos.length) {
      return [
        {
          label: "Connected Repositories",
          value: "0",
          delta: "Connect your GitHub token to see data",
          trend: "down"
        }
      ];
    }
    return [
      {
        label: "Connected Repositories",
        value: String(repos.length),
        delta: "Based on live GitHub data",
        trend: "up"
      },
      {
        label: "Average Health",
        value: `${Math.round(
          repos.reduce((acc, r) => acc + (r.health?.overall ?? 0), 0) / (repos.length || 1)
        )}%`,
        delta: "From recent analyses",
        trend: "up"
      }
    ];
  }, [repos]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gh-heading">Overview</h2>
        <p className="text-sm text-gh-text">Live repository insights and AI analysis summaries.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} delta={metric.delta} trend={metric.trend} />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <SectionCard title="Top Repositories">
          {loadingRepos ? (
            <p className="text-sm text-gh-text">Loading live repositories...</p>
          ) : reposError ? (
            <p className="text-sm text-red-400">{reposError}</p>
          ) : repos.length === 0 ? (
            <p className="text-sm text-gh-text">No repositories found for the connected GitHub user.</p>
          ) : (
            <ul className="space-y-2">
              {repos.slice(0, 5).map((repo) => (
                <li key={repo.full_name} className="flex items-center justify-between rounded-md border border-gh-border bg-gh-bg px-3 py-2 text-sm">
                  <span>{repo.full_name}</span>
                  <span className="text-xs text-gh-text">
                    {repo.language ?? "Unknown"} · ⭐ {repo.stars} · {repo.health?.overall ?? 0}%
                  </span>
                </li>
              ))}
            </ul>
          )}
        </SectionCard>
        <SectionCard title="Recent Pull Requests">
          <p className="text-sm text-gh-text">
            Open the Pull Requests section to view live PRs and detailed AI analysis for each.
          </p>
        </SectionCard>
      </div>
    </div>
  );
}
