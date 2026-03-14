import { SectionCard } from "@/components/common/section-card";
import { testSuggestions } from "@/lib/data";

export default function TestsPage() {
  return (
    <div className="space-y-4">
      <SectionCard title="Generated Test Suggestions">
        <ul className="list-disc space-y-2 pl-5">
          {testSuggestions.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </SectionCard>
      <SectionCard title="Code Change Intelligence">
        <p className="text-sm">PRs are classified as feature, bug fix, refactor, or security update so tests and analysis paths are selected intelligently.</p>
      </SectionCard>
      <SectionCard title="Documentation Assistant">
        <p className="text-sm">When API/module changes are detected, the system suggests README and usage-doc updates.</p>
      </SectionCard>
    </div>
  );
}
