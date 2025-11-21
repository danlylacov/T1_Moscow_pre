"use client";

import Link from "next/link";

export function MarketingFooter() {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/90">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 py-4 text-xs text-slate-500 md:flex-row md:items-center md:justify-between">
        <p>© {new Date().getFullYear()} Self-Deploy. All rights reserved.</p>
        <div className="flex flex-wrap items-center gap-4">
          <Link href="#docs" className="hover:text-slate-200">
            Docs
          </Link>
          <Link href="#pricing" className="hover:text-slate-200">
            Pricing
          </Link>
          <Link href="https://github.com" className="hover:text-slate-200">
            GitHub
          </Link>
          <Link href="#support" className="hover:text-slate-200">
            Support
          </Link>
        </div>
      </div>
    </footer>
  );
}


