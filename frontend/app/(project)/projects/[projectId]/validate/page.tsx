"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { ShieldAlert, CheckCircle2 } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ValidationReport } from "./_components/validation-report";
import { AIExplanation } from "./_components/ai-explanation";

export default function ValidatePage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params?.projectId ?? "unknown";
  const editorHref = `/projects/${projectId}/editor`;

  const handleApprove = () => {
    // Simulated direct commit / approval action.
    // In a real app this would trigger a mutation.
    console.log("Pipeline approved for project", projectId);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 py-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <Card className="border-slate-800 bg-slate-950/80">
          <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/10 text-amber-300">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <CardTitle className="text-base">
                  Security & validation review
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Before committing this pipeline, review security findings and
                  let AI translate the YAML into human-readable documentation.
                </CardDescription>
              </div>
            </div>
            <Badge variant="secondary" className="flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
              <span className="text-[11px]">Step 4 of 5 • Validate</span>
            </Badge>
          </CardHeader>
        </Card>

        <Tabs defaultValue="security" className="space-y-5">
          <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <div className="space-y-1">
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Review mode
              </p>
              <p className="text-xs text-slate-500">
                Switch between security checks and AI-assisted explanation.
              </p>
            </div>
            <TabsList>
              <TabsTrigger value="security">Security &amp; validation</TabsTrigger>
              <TabsTrigger value="explain">AI explanation</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="security">
            <ValidationReport />
          </TabsContent>

          <TabsContent value="explain">
            <AIExplanation />
          </TabsContent>
        </Tabs>

        <Card className="border-slate-800 bg-slate-950/90">
          <CardContent className="flex flex-col gap-3 pt-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-1 text-xs text-slate-400">
              <p className="font-medium text-slate-200">
                Ready to continue?
              </p>
              <p>
                Fix issues in the pipeline editor or approve this configuration
                to continue with your rollout flow.
              </p>
            </div>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <Link href={editorHref}>
                <Button className="gap-1.5">
                  <ShieldAlert className="h-4 w-4" />
                  Fix issues in editor
                </Button>
              </Link>
              <Button
                type="button"
                variant="secondary"
                className="gap-1.5"
                onClick={handleApprove}
              >
                <CheckCircle2 className="h-4 w-4" />
                Approve &amp; merge
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

