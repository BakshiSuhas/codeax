type MetricCardProps = {
  label: string;
  value: string;
  delta: string;
  trend: "up" | "down";
};

export function MetricCard({ label, value, delta, trend }: MetricCardProps) {
  const trendColor = trend === "up" ? "text-gh-green" : "text-amber-400";

  return (
    <article className="rounded-xl border border-gh-border bg-gh-card p-5">
      <p className="text-sm text-gh-text">{label}</p>
      <p className="mt-3 text-3xl font-semibold text-gh-heading">{value}</p>
      <p className={`mt-2 text-xs font-medium ${trendColor}`}>{delta}</p>
    </article>
  );
}
