"use client";

import { useEffect, useState } from "react";

import { SectionCard } from "@/components/common/section-card";
import { fetchJson } from "@/lib/api";

type Repo = {
  owner: string;
  name: string;
  full_name: string;
  description?: string | null;
  stars: number;
  language?: string | null;
  health: {
    overall: number;
  };
};

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<Repo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    setLoading(true);
    setError("");
    fetchJson<Repo[]>("/api/repositories/")
      .then((data) => setRepos(data))
      .catch(() => setError("Unable to load repositories from backend. Check GitHub token and backend status."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-4">
      <SectionCard title="Repositories">
        {loading ? (
          <p className="text-sm text-gh-text">Loading repositories...</p>
        ) : error ? (
          <p className="text-sm text-red-400">{error}</p>
        ) : repos.length === 0 ? (
          <p className="text-sm text-gh-text">No repositories found for the connected GitHub account.</p>
        ) : (
          <ul className="space-y-3">
            {repos.map((repo) => (
              <li key={repo.full_name} className="rounded-lg border border-gh-border bg-gh-bg px-4 py-3">
                <p className="font-medium text-gh-heading">{repo.full_name}</p>
                <p className="text-xs text-gh-text">
                  {repo.language ?? "Unknown language"} · {repo.stars} stars
                </p>
                {repo.description ? <p className="mt-1 text-xs text-gh-text">{repo.description}</p> : null}
                <p className="mt-2 text-xs text-gh-text">
                  Health score (overall): {repo.health?.overall ?? 0}%
                </p>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
      <SectionCard title="Repository Metrics Tracking">
        <p className="text-sm">
          Codeax keeps a health history whenever analyses run, so you can track code quality, security, tests, and
          technical debt over time.
        </p>
      </SectionCard>
      <SectionCard title="AI Repository Knowledge Map">
        <p className="text-sm">
          Coordinator analysis builds a knowledge map of changed modules and routes decisions to specialized agents for
          security, code quality, and tests.
        </p>
      </SectionCard>
    </div>
  );
}
