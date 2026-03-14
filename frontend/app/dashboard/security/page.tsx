import { SectionCard } from "@/components/common/section-card";
import { securityFindings } from "@/lib/data";

export default function SecurityPage() {
  return (
    <div className="space-y-4">
      <SectionCard title="Security Review">
        <ul className="list-disc space-y-2 pl-5">
          {securityFindings.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </SectionCard>
      <SectionCard title="Dependency Risk Monitoring">
        <p className="text-sm">The backend scans changed dependency manifests and lockfiles for known risky versions and reports recommendations.</p>
      </SectionCard>
      <SectionCard title="AI Auto Fix Suggestions">
        <p className="text-sm">When injection or secret exposure patterns are detected, the system proposes secure code replacement snippets.</p>
      </SectionCard>
    </div>
  );
}
