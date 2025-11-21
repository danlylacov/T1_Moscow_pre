"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { GitMerge, Play, Clock, Shield, Box } from "lucide-react";

export type TriggerKey =
  | "on-push"
  | "on-merge-request"
  | "on-tags"
  | "schedule"
  | "manual";

interface TriggerSelectorProps {
  value: TriggerKey[];
  onChange: (value: TriggerKey[]) => void;
}

const TRIGGERS: {
  id: TriggerKey;
  label: string;
  description: string;
  icon: React.ReactNode;
}[] = [
  {
    id: "on-push",
    label: "On Push (main/develop)",
    description: "Run pipeline on pushes to main or develop branches.",
    icon: <Play className="h-3.5 w-3.5 text-sky-400" />,
  },
  {
    id: "on-merge-request",
    label: "On Merge Request",
    description: "Validate changes before merging into main.",
    icon: <GitMerge className="h-3.5 w-3.5 text-emerald-400" />,
  },
  {
    id: "on-tags",
    label: "On Tags (v*)",
    description: "Trigger releases only for version tags like v1.2.0.",
    icon: <Box className="h-3.5 w-3.5 text-violet-400" />,
  },
  {
    id: "schedule",
    label: "Schedule (Cron)",
    description: "Nightly or weekly cron-based executions.",
    icon: <Clock className="h-3.5 w-3.5 text-amber-400" />,
  },
  {
    id: "manual",
    label: "Manual (Web UI)",
    description: "Allow manual runs from your CI/CD dashboard.",
    icon: <Shield className="h-3.5 w-3.5 text-slate-300" />,
  },
];

export function TriggerSelector({ value, onChange }: TriggerSelectorProps) {
  const toggle = (id: TriggerKey) => {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      onChange([...value, id]);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Triggers</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        {TRIGGERS.map((trigger) => {
          const enabled = value.includes(trigger.id);
          return (
            <div
              key={trigger.id}
              className="flex items-center justify-between gap-3 rounded-md border border-slate-800 bg-slate-950/70 px-3 py-2"
            >
              <div className="flex flex-1 items-center gap-3">
                <div className="flex h-7 w-7 items-center justify-center rounded-md bg-slate-900">
                  {trigger.icon}
                </div>
                <div>
                  <Label className="cursor-pointer text-xs font-medium text-slate-100">
                    {trigger.label}
                  </Label>
                  <p className="text-[11px] text-slate-500">
                    {trigger.description}
                  </p>
                </div>
              </div>
              <Switch
                checked={enabled}
                onCheckedChange={() => toggle(trigger.id)}
                aria-label={trigger.label}
              />
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}


