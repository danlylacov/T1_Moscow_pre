"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Stage, StageSettingsDialog } from "./stage-settings-dialog";
import { GitMerge, Play, Shield, Box, Server } from "lucide-react";

interface StagesListProps {
  stages: Stage[];
  onChange: (stages: Stage[]) => void;
}

export function StagesList({ stages, onChange }: StagesListProps) {
  const updateStage = (updated: Stage) => {
    onChange(stages.map((s) => (s.id === updated.id ? updated : s)));
  };

  const toggleStage = (stage: Stage, enabled: boolean) => {
    updateStage({ ...stage, enabled });
  };

  const iconForStage = (id: string) => {
    if (id === "lint") return <GitMerge className="h-4 w-4 text-sky-400" />;
    if (id === "tests") return <Play className="h-4 w-4 text-emerald-400" />;
    if (id === "build") return <Box className="h-4 w-4 text-violet-400" />;
    if (id === "security") return <Shield className="h-4 w-4 text-amber-400" />;
    return <Server className="h-4 w-4 text-slate-300" />;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Stages</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {stages.map((stage, index) => (
          <div key={stage.id} className="relative">
            <div className="flex items-center justify-between gap-3 rounded-md border border-slate-800 bg-slate-950/70 px-3 py-2">
              <div className="flex flex-1 items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900">
                  {iconForStage(stage.id)}
                </div>
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-slate-100">
                      {stage.name}
                    </span>
                    <Badge
                      variant={stage.enabled ? "success" : "outline"}
                      className="text-[10px]"
                    >
                      {stage.enabled ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    {stage.description}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={stage.enabled}
                  onCheckedChange={(checked) => toggleStage(stage, checked)}
                  aria-label={`Toggle stage ${stage.name}`}
                />
                <StageSettingsDialog stage={stage} onChange={updateStage} />
              </div>
            </div>
            {index < stages.length - 1 && (
              <div className="ml-4 h-3 border-l border-dashed border-slate-800" />
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}


