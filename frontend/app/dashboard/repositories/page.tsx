import { SectionCard } from "@/components/common/section-card";
import { fetchJson } from "@/lib/api";
import { repositories } from "@/lib/data";

type RepositoryResponse = {
  full_name: string;
  language: string | null;
  stars: number;
  health: {
    overall: number;
  };
};

export default async function RepositoriesPage() {
  let items = repositories;
  try {
    const liveRepositories = await fetchJson<RepositoryResponse[]>("/api/repositories/");
    if (liveRepositories.length > 0) {
      items = liveRepositories.map((repo) => ({
        fullName: repo.full_name,
        language: repo.language || "Unknown",
        stars: repo.stars,
        health: repo.health.overall,
      }));
    }
  } catch {
    // Fall back to static data if backend is unavailable.
  }

  return (
    <div className="space-y-4">
      <SectionCard title="Repositories">
        <ul className="space-y-3">
          {items.map((repo) => (
            <li key={repo.fullName} className="rounded-lg border border-gh-border bg-gh-bg px-4 py-3">
              <p className="font-medium text-gh-heading">{repo.fullName}</p>
              <p className="text-sm">{repo.language} · {repo.stars} stars · Health {repo.health}%</p>
            </li>
          ))}
        </ul>
      </SectionCard>
      <SectionCard title="Repository Metrics Tracking">
        <p className="text-sm">Use backend endpoints for repository insights and health history to track trends over time.</p>
      </SectionCard>
      <SectionCard title="AI Repository Knowledge Map">
        <p className="text-sm">Coordinator analysis stores contextual understanding of changed modules and routes decisions to specialized agents.</p>
      </SectionCard>
    </div>
  );
}
