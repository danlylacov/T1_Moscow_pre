"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AnalysisTerminal } from "./_components/analysis-terminal";
import { StackCard, type StackItem } from "./_components/stack-card";
import { EditStackDialog } from "./_components/edit-stack-dialog";
import { AlertCircle, CheckCircle, Cpu, Database } from "lucide-react";

const logSteps = [
  "Cloning repository...",
  "Found package.json",
  "Detecting framework...",
  "Analyzing Dockerfile...",
  "Inspecting dependencies...",
  "Scanning infrastructure files...",
  "Detecting database drivers...",
  "Analysis complete.",
];

const detectedFiles = [
  { name: "Dockerfile", status: "found" as const },
  { name: "package.json", status: "found" as const },
  { name: "helm chart", status: "missing" as const },
  { name: "terraform", status: "missing" as const },
];

const initialStack: StackItem[] = [
  { id: "language", label: "Language", value: "Node.js v18", type: "language" },
  { id: "framework", label: "Framework", value: "NestJS", type: "framework" },
  { id: "test", label: "Test Runner", value: "Jest", type: "test" },
  { id: "container", label: "Container", value: "Docker", type: "container" },
  { id: "iac", label: "IaC", value: "Terraform", type: "iac" },
  { id: "database", label: "Database", value: "PostgreSQL", type: "database" },
];

export default function Page({
  params,
}: {
  params: { projectId: string };
}) {
  const router = useRouter();
  const [progress, setProgress] = useState(0);
  const [visibleLogs, setVisibleLogs] = useState<string[]>([]);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [stackItems, setStackItems] = useState(
    initialStack.map((item) => ({
      ...item,
      enabled: true,
      versions:
        item.id === "language"
          ? ["Node.js v18", "Node.js v20"]
          : item.id === "database"
          ? ["PostgreSQL 14", "PostgreSQL 15"]
          : item.id === "container"
          ? ["Docker", "Podman"]
          : [item.value],
    }))
  );

  useEffect(() => {
    let current = 0;
    const totalDuration = 3000;
    const step = 100 / (logSteps.length - 1);
    const interval = 150;

    const timer = setInterval(() => {
      current = Math.min(100, current + (100 * interval) / totalDuration);
      setProgress(current);

      const targetIndex = Math.min(
        logSteps.length - 1,
        Math.floor(current / step)
      );
      setVisibleLogs(logSteps.slice(0, targetIndex + 1));

      if (current >= 100) {
        clearInterval(timer);
        setAnalysisComplete(true);
      }
    }, interval);

    return () => clearInterval(timer);
  }, []);

  const enabledStackItems = useMemo(
    () => stackItems.filter((item) => item.enabled),
    [stackItems]
  );

  const editableStackItems = stackItems;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-50">
            Analyze repository
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Step 1 of 5 · Detecting stack and infrastructure for project{" "}
            <span className="font-mono text-slate-200">
              {params.projectId}
            </span>
          </p>
        </div>
        <Badge variant="secondary" className="flex items-center gap-1">
          <Cpu className="h-3.5 w-3.5 text-sky-400" />
          <span className="text-[11px]">Analysis</span>
        </Badge>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
        <Card>
          <CardHeader className="space-y-3">
            <CardTitle>Analysis status</CardTitle>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>
                  {analysisComplete
                    ? "Analysis complete"
                    : "Scanning repository..."}
                </span>
                <span className="font-mono text-slate-300">
                  {Math.round(progress)}%
                </span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>
          </CardHeader>
          <CardContent>
            <AnalysisTerminal logs={visibleLogs} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Detected files</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            {detectedFiles.map((file) => (
              <div
                key={file.name}
                className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-950/70 px-3 py-2"
              >
                <div className="flex items-center gap-2">
                  {file.status === "found" ? (
                    <CheckCircle className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-slate-500" />
                  )}
                  <span className="text-slate-100">{file.name}</span>
                </div>
                <Badge
                  variant={file.status === "found" ? "success" : "outline"}
                  className="text-[10px]"
                >
                  {file.status === "found" ? "Found" : "Missing"}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {analysisComplete && (
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-sky-400" />
              <h2 className="text-sm font-semibold text-slate-100">
                Auto-detected stack
              </h2>
            </div>
            <EditStackDialog
              items={editableStackItems}
              onChange={setStackItems}
            />
          </div>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {enabledStackItems.map((item, index) => (
              <StackCard key={item.id} item={item} index={index} />
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between border-t border-slate-800 pt-4">
        <p className="text-xs text-slate-500">
          Next: configure triggers, stages and environments for the pipeline.
        </p>
        <Button
          disabled={!analysisComplete}
          onClick={() =>
            router.push(`/projects/${params.projectId}/configure`)
          }
        >
          Proceed to Pipeline Configuration
        </Button>
      </div>
    </div>
  );
}

