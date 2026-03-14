import type { ReactNode } from "react";

type SectionCardProps = {
  title: string;
  children: ReactNode;
};

export function SectionCard({ title, children }: SectionCardProps) {
  return (
    <section className="rounded-xl border border-gh-border bg-gh-card p-5">
      <h2 className="text-lg font-semibold text-gh-heading">{title}</h2>
      <div className="mt-4 text-gh-text">{children}</div>
    </section>
  );
}
