"use client";

import { ShieldAlert, AlertTriangle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

type Severity = "critical" | "high" | "warning";

export interface IssueRowProps {
  severity: Severity;
  issue: string;
  location: string;
  recommendation: string;
}

const severityStyles: Record<
  Severity,
  {
    label: string;
    badgeClass: string;
    rowClass: string;
    icon: "shield" | "triangle";
  }
> = {
  critical: {
    label: "Critical",
    badgeClass: "bg-red-500/15 text-red-200 border border-red-500/50",
    rowClass: "bg-red-500/5",
    icon: "shield",
  },
  high: {
    label: "High",
    badgeClass:
      "bg-amber-500/15 text-amber-100 border border-amber-500/60",
    rowClass: "bg-amber-500/5",
    icon: "shield",
  },
  warning: {
    label: "Warning",
    badgeClass:
      "bg-yellow-500/10 text-yellow-100 border border-yellow-500/50",
    rowClass: "bg-yellow-500/5",
    icon: "triangle",
  },
};

export function IssueRow({
  severity,
  issue,
  location,
  recommendation,
}: IssueRowProps) {
  const config = severityStyles[severity];

  return (
    <TableRow
      className={cn(
        "border-slate-800/80 hover:bg-slate-900/90",
        config.rowClass
      )}
    >
      <TableCell className="w-[120px] text-xs">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-slate-950">
            {config.icon === "shield" ? (
              <ShieldAlert className="h-3.5 w-3.5 text-red-400" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5 text-amber-300" />
            )}
          </span>
          <Badge className={cn("text-[10px]", config.badgeClass)}>
            {config.label}
          </Badge>
        </div>
      </TableCell>
      <TableCell className="text-xs text-slate-100">{issue}</TableCell>
      <TableCell className="w-[90px] text-xs text-slate-400">
        {location}
      </TableCell>
      <TableCell className="w-[220px] text-xs text-slate-300">
        {recommendation}
      </TableCell>
    </TableRow>
  );
}


