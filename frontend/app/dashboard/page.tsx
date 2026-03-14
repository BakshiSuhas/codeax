import { SectionCard } from "@/components/common/section-card";
import { MetricCard } from "@/components/ui/metric-card";
import { dashboardMetrics, pullRequests, repositories } from "@/lib/data";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gh-heading">Overview</h2>
        <p className="text-sm text-gh-text">Live repository insights and AI analysis summaries.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {dashboardMetrics.map((metric) => (
          <MetricCard key={metric.label} label={metric.label} value={metric.value} delta={metric.delta} trend={metric.trend} />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <SectionCard title="Top Repositories">
          <ul className="space-y-2">
            {repositories.map((repo) => (
              <li key={repo.fullName} className="rounded-md border border-gh-border bg-gh-bg px-3 py-2 text-sm">
                {repo.fullName} - health {repo.health}%
              </li>
            ))}
          </ul>
        </SectionCard>
        <SectionCard title="Recent Pull Requests">
          <ul className="space-y-2">
            {pullRequests.map((pr) => (
              <li key={pr.number} className="rounded-md border border-gh-border bg-gh-bg px-3 py-2 text-sm">
                #{pr.number} {pr.title} ({pr.status})
              </li>
            ))}
          </ul>
        </SectionCard>
      </div>
    </div>
  );
}
