import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/repositories", label: "Repositories" },
  { href: "/dashboard/pull-requests", label: "Pull Requests" },
  { href: "/dashboard/security", label: "Security" },
  { href: "/dashboard/tests", label: "Tests" },
  { href: "/dashboard/settings", label: "Settings" }
];

export function DashboardNav() {
  return (
    <aside className="w-full border-b border-gh-border bg-gh-card px-4 py-4 md:h-screen md:w-64 md:border-b-0 md:border-r md:px-5 md:py-6">
      <Link href="/" className="mb-6 inline-flex items-center gap-2 font-semibold text-gh-heading">
        <span className="inline-flex h-8 w-8 items-center justify-center rounded bg-gh-green text-sm text-white">RG</span>
        RepoGuardian
      </Link>
      <nav className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="rounded-md border border-transparent px-3 py-2 text-sm text-gh-text transition hover:border-gh-border hover:bg-gh-bg"
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
