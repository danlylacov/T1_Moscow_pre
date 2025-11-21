"use client";

import {
  ShieldAlert,
  CheckCircle2,
  FileText,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { IssueRow } from "./issue-row";

const MOCK_ISSUES = [
  {
    severity: "critical" as const,
    issue: "docker run --privileged detected in build stage.",
    location: "Line 42",
    recommendation: "Avoid --privileged; use fine-grained capabilities instead.",
  },
  {
    severity: "high" as const,
    issue: "curl | bash pipe detected in setup script.",
    location: "Line 18",
    recommendation: "Download script and verify checksum/signature before executing.",
  },
  {
    severity: "warning" as const,
    issue: "pytest command configured but tests/ directory missing in repo.",
    location: "Line 63",
    recommendation:
      "Create a tests/ directory or remove the pytest step to avoid false negatives.",
  },
];

export function ValidationReport() {
  const totalIssues = MOCK_ISSUES.length;

  return (
    <div className="space-y-5">
      {/* Overall status banner */}
      <Alert variant="destructive" className="border-red-500/60 bg-red-950/40">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-7 w-7 items-center justify-center rounded-full bg-red-500/15">
            <ShieldAlert className="h-4 w-4 text-red-300" />
          </span>
          <div className="space-y-1">
            <AlertTitle className="flex items-center gap-2 text-sm">
              {totalIssues > 0 ? (
                <>
                  <span>Security review required</span>
                  <Badge className="bg-red-500/20 text-red-100 border border-red-500/60 text-[10px]">
                    ⚠ {totalIssues} issues found
                  </Badge>
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <span>Pipeline is valid</span>
                </>
              )}
            </AlertTitle>
            <AlertDescription className="text-xs text-red-100/80">
              We detected potentially dangerous commands in this pipeline. Review
              and fix them before approving changes to your CI/CD configuration.
            </AlertDescription>
          </div>
        </div>
      </Alert>

      {/* Security audit table */}
      <Card className="border-slate-800 bg-slate-950/80">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900">
              <ShieldAlert className="h-4 w-4 text-red-400" />
            </div>
            <div>
              <CardTitle className="text-sm">Security audit</CardTitle>
              <CardDescription className="text-[11px] text-slate-400">
                Static analysis of pipeline commands and execution context.
              </CardDescription>
            </div>
          </div>
          <Badge variant="secondary" className="text-[10px]">
            Security policy: default
          </Badge>
        </CardHeader>
        <CardContent className="pt-0">
          <Table>
            <TableHeader>
              <TableRow className="bg-slate-950/80">
                <TableHead className="w-[140px] text-[11px]">
                  Severity
                </TableHead>
                <TableHead className="text-[11px]">Issue</TableHead>
                <TableHead className="w-[90px] text-[11px]">
                  Location
                </TableHead>
                <TableHead className="w-[240px] text-[11px]">
                  Recommendation
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {MOCK_ISSUES.map((issue) => (
                <IssueRow
                  key={`${issue.severity}-${issue.location}`}
                  severity={issue.severity}
                  issue={issue.issue}
                  location={issue.location}
                  recommendation={issue.recommendation}
                />
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Linter checks */}
      <Card className="border-slate-800 bg-slate-950/90">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-emerald-500/10">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            </div>
            <div>
              <CardTitle className="text-sm">Linter & syntax checks</CardTitle>
              <CardDescription className="text-[11px] text-slate-400">
                Basic validation of YAML structure and CI keywords.
              </CardDescription>
            </div>
          </div>
          <Badge variant="success" className="text-[10px]">
            YAML valid
          </Badge>
        </CardHeader>
        <CardContent className="space-y-2 pt-0">
          <Alert variant="success">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-400" />
              <div>
                <AlertTitle className="text-xs">
                  YAML structure valid
                </AlertTitle>
                <AlertDescription>
                  The pipeline file parses correctly and all stages, jobs, and
                  keys follow GitLab CI syntax.
                </AlertDescription>
              </div>
            </div>
          </Alert>

          <Alert>
            <div className="flex items-start gap-2">
              <FileText className="mt-0.5 h-4 w-4 text-slate-300" />
              <div>
                <AlertTitle className="text-xs">
                  Naming conventions
                </AlertTitle>
                <AlertDescription>
                  Job and stage names follow recommended conventions. Consider
                  adding descriptions to critical jobs for easier onboarding.
                </AlertDescription>
              </div>
            </div>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}


