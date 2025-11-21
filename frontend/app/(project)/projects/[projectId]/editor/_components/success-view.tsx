"use client";

import Link from "next/link";
import { CheckCircle, GitPullRequest, History } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface SuccessViewProps {
  projectId: string;
}

export function SuccessView({ projectId }: SuccessViewProps) {
  const dashboardHref = "/dashboard";

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-6 py-8">
      <Card className="w-full max-w-xl border-emerald-500/40 bg-slate-950/90">
        <CardHeader className="flex flex-col items-center space-y-4 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/15">
            <CheckCircle className="h-10 w-10 text-emerald-400" />
          </div>
          <div className="space-y-1">
            <CardTitle className="text-lg">
              Pipeline successfully pushed!
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">
              Your CI/CD configuration for project{" "}
              <span className="font-mono text-slate-200">
                {projectId}
              </span>{" "}
              has been published. The first pipeline run is starting in the
              background.
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-2 text-xs text-slate-300 sm:grid-cols-2">
            <button
              type="button"
              className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-left hover:border-sky-500/60 hover:bg-slate-900"
            >
              <span className="flex items-center gap-2">
                <GitPullRequest className="h-4 w-4 text-sky-400" />
                <span>View Merge Request #42</span>
              </span>
              <span className="text-[11px] text-slate-500">opens Git</span>
            </button>
            <button
              type="button"
              className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-left hover:border-emerald-500/60 hover:bg-slate-900"
            >
              <span className="flex items-center gap-2">
                <History className="h-4 w-4 text-emerald-400" />
                <span>View pipeline log</span>
              </span>
              <span className="text-[11px] text-slate-500">opens CI</span>
            </button>
          </div>

          <div className="flex items-center justify-between border-t border-slate-800 pt-4">
            <div className="text-[11px] text-slate-500">
              You can always revisit this editor from the project page to
              tweak your pipeline.
            </div>
            <Link href={dashboardHref}>
              <Button className="h-8 gap-1.5 px-3 text-xs">
                Back to dashboard
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


