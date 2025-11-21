import type { ReactNode } from "react";
import { Sidebar } from "./_components/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-50">
      <Sidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 backdrop-blur">
          <div className="text-sm text-slate-400">
            <span className="font-medium text-slate-100">Dashboard</span>
            <span className="mx-2 text-slate-600">/</span>
            <span className="text-slate-400">Overview</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-end">
              <span className="text-sm font-medium text-slate-100">
                Jane Doe
              </span>
              <span className="text-xs text-slate-500">
                jane@self-deploy.io
              </span>
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-800 text-xs font-medium">
              JD
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto bg-slate-950 px-6 py-6">
          {children}
        </main>
      </div>
    </div>
  );
}


