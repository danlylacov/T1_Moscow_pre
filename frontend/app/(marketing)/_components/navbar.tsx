"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

export function MarketingNavbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900 text-xs font-mono font-semibold text-sky-400 shadow-[0_0_20px_rgba(56,189,248,0.3)]">
            SD
          </span>
          <span className="text-sm font-semibold tracking-tight">
            Self-Deploy
          </span>
        </Link>

        <nav className="flex items-center gap-6 text-xs text-slate-300">
          <div className="hidden items-center gap-5 md:flex">
            <Link
              href="#docs"
              className="hover:text-slate-50 transition-colors"
            >
              Docs
            </Link>
            <Link
              href="#pricing"
              className="hover:text-slate-50 transition-colors"
            >
              Pricing
            </Link>
            <Link
              href="https://github.com"
              className="hover:text-slate-50 transition-colors"
            >
              GitHub
            </Link>
          </div>
          <div className="flex items-center gap-2">
            <Link href="/login">
              <Button
                variant="outline"
                size="sm"
                className="border-slate-700 bg-slate-950 text-xs"
              >
                Sign in
              </Button>
            </Link>
            <Link href="/register">
              <Button
                size="sm"
                className="bg-sky-500 text-xs text-slate-950 hover:bg-sky-400"
              >
                Try demo
              </Button>
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}


