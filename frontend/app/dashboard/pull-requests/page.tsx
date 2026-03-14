"use client";

import { useEffect, useMemo, useState } from "react";

import { SectionCard } from "@/components/common/section-card";
import { fetchJson, type AnalysisResult } from "@/lib/api";
import { pullRequests } from "@/lib/data";

type PullRequestSummary = {
  number: number;
  title: string;
  author: string;
  status: string;
};

const DEFAULT_OWNER = "octo-org";
const DEFAULT_REPO = "codeax";

export default function PullRequestsPage() {
  const [items, setItems] = useState<PullRequestSummary[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    fetchJson<PullRequestSummary[]>(`/api/pull-requests/${DEFAULT_OWNER}/${DEFAULT_REPO}`)
      .then((data) => {
        setItems(data);
        if (data.length > 0) {
          setSelected(data[0].number);
        }
      })
      .catch(() => {
        setItems(pullRequests);
      });
  }, []);

  useEffect(() => {
    if (!selected) return;
    setError("");
    fetchJson<AnalysisResult>(`/api/analysis/${DEFAULT_OWNER}/${DEFAULT_REPO}/${selected}`)
      .then((data) => setAnalysis(data))
      .catch(() => {
        setAnalysis(null);
        setError("No analysis report yet. Trigger it via webhook or POST /api/analysis/{owner}/{repo}/{pr_number}.");
      });
  }, [selected]);

  const selectedTitle = useMemo(() => items.find((item) => item.number === selected)?.title || "", [items, selected]);

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <SectionCard title="Pull Requests">
        <ul className="space-y-3">
          {items.map((pr) => (
            <li key={pr.number}>
              <button
                type="button"
                onClick={() => setSelected(pr.number)}
                className={`w-full rounded-lg border px-4 py-3 text-left ${selected === pr.number ? "border-gh-green bg-gh-bg" : "border-gh-border bg-gh-bg"}`}
              >
                <p className="font-medium text-gh-heading">#{pr.number} {pr.title}</p>
                <p className="text-sm">{pr.author} · {pr.status}</p>
              </button>
            </li>
          ))}
        </ul>
      </SectionCard>

      <div className="space-y-4 lg:col-span-2">
        <SectionCard title="PR Analysis View">
          <p className="text-sm">Selected PR: {selected ? `#${selected} ${selectedTitle}` : "None"}</p>
          {error ? <p className="mt-2 text-sm text-amber-300">{error}</p> : null}
          {analysis ? (
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <div className="rounded border border-gh-border bg-gh-bg p-3 text-sm">Type: {analysis.pr_type}</div>
              <div className="rounded border border-gh-border bg-gh-bg p-3 text-sm">Health Score: {analysis.health.overall}%</div>
              <div className="rounded border border-gh-border bg-gh-bg p-3 text-sm">Security Score: {analysis.health.security}%</div>
              <div className="rounded border border-gh-border bg-gh-bg p-3 text-sm">Code Quality: {analysis.health.code_quality}%</div>
            </div>
          ) : null}
        </SectionCard>

        {analysis ? (
          <SectionCard title="AI Findings">
            <ul className="list-disc space-y-2 pl-5 text-sm">
              {analysis.findings.map((finding) => (
                <li key={`${finding.category}-${finding.title}`}>
                  [{finding.severity}] {finding.title}: {finding.details}
                </li>
              ))}
            </ul>
          </SectionCard>
        ) : null}

        {analysis ? (
          <SectionCard title="Generated Tests">
            <ul className="list-disc space-y-2 pl-5 text-sm">
              {analysis.generated_tests.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </SectionCard>
        ) : null}
      </div>
    </div>
  );
}
