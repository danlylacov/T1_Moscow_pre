import type { ReactNode } from "react";
import { MarketingNavbar } from "./_components/navbar";
import { MarketingFooter } from "./_components/footer";

export default function MarketingLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-50">
      <MarketingNavbar />
      <main className="flex-1">{children}</main>
      <MarketingFooter />
    </div>
  );
}


