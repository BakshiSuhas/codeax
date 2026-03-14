import type { ReactNode } from "react";

import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { DashboardNav } from "@/components/dashboard/dashboard-nav";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen md:flex">
      <DashboardNav />
      <div className="flex-1">
        <DashboardHeader />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
