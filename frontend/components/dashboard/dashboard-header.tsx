export function DashboardHeader() {
  return (
    <header className="border-b border-gh-border bg-gh-card px-6 py-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold text-gh-heading">RepoGuardian Dashboard</h1>
        <p className="text-sm text-gh-text">Track repository health, PR analysis, and security posture in one place.</p>
      </div>
    </header>
  );
}
