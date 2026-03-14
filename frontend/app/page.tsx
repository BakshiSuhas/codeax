import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-10 md:px-16 md:py-16">
      <section className="mx-auto max-w-5xl rounded-2xl border border-gh-border bg-gh-card/90 p-8 shadow-2xl md:p-12">
        <p className="text-gh-green text-sm font-semibold tracking-wide">Codeax</p>
        <h1 className="mt-3 max-w-3xl text-4xl font-bold text-gh-heading md:text-6xl">
          Autonomous GitHub review, security scanning, and test guidance for your codebase.
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-gh-text">
          Analyze pull requests, identify risks, and surface actionable improvements from a single dashboard.
        </p>
        <div className="mt-8 flex flex-wrap gap-4">
          <Link className="rounded-lg bg-gh-green px-5 py-3 font-semibold text-white" href="/dashboard">
            Open Dashboard
          </Link>
          <a className="rounded-lg border border-gh-border px-5 py-3 font-semibold" href="http://localhost:8000/docs">
            API Docs
          </a>
        </div>
      </section>
      <section className="mx-auto mt-8 grid max-w-5xl gap-4 md:grid-cols-3">
        <article className="rounded-xl border border-gh-border bg-gh-card p-5">
          <h2 className="text-base font-semibold text-gh-heading">Code Review Agent</h2>
          <p className="mt-2 text-sm text-gh-text">Highlights quality risks and readability improvements in changed files.</p>
        </article>
        <article className="rounded-xl border border-gh-border bg-gh-card p-5">
          <h2 className="text-base font-semibold text-gh-heading">Security Agent</h2>
          <p className="mt-2 text-sm text-gh-text">Flags exposed secrets and insecure patterns before merge.</p>
        </article>
        <article className="rounded-xl border border-gh-border bg-gh-card p-5">
          <h2 className="text-base font-semibold text-gh-heading">Test Agent</h2>
          <p className="mt-2 text-sm text-gh-text">Suggests test cases for newly introduced logic paths.</p>
        </article>
      </section>
      <section className="mx-auto mt-8 max-w-5xl rounded-xl border border-gh-border bg-gh-card p-5">
        <h2 className="text-lg font-semibold text-gh-heading">Workflow</h2>
        <p className="mt-2 text-sm text-gh-text">
          Webhook event to coordinator agent to specialized agents to aggregated output to dashboard and PR summary.
        </p>
      </section>
      <section className="mx-auto mt-8 max-w-5xl rounded-xl border border-gh-border bg-gh-card p-5">
        <h2 className="text-lg font-semibold text-gh-heading">Pricing</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border border-gh-border bg-gh-bg p-4 text-sm">Starter - 3 repos - Free</div>
          <div className="rounded-lg border border-gh-green bg-gh-bg p-4 text-sm">Pro - Unlimited repos - $29/month</div>
          <div className="rounded-lg border border-gh-border bg-gh-bg p-4 text-sm">Enterprise - Custom workflows</div>
        </div>
      </section>
    </main>
  );
}
