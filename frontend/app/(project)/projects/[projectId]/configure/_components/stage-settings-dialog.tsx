"use client";

import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Settings } from "lucide-react";

export type Executor = "docker" | "shell" | "k8s";

export interface StageConfig {
  executor: Executor;
  image: string;
  script: string;
  artifacts: string;
}

export interface Stage {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  config: StageConfig;
}

interface StageSettingsDialogProps {
  stage: Stage;
  onChange: (stage: Stage) => void;
}

export function StageSettingsDialog({
  stage,
  onChange,
}: StageSettingsDialogProps) {
  const [open, setOpen] = React.useState(false);
  const [local, setLocal] = React.useState<Stage>(stage);

  React.useEffect(() => {
    setLocal(stage);
  }, [stage, open]);

  const handleSave = () => {
    onChange(local);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="border-slate-700 text-xs"
        >
          <Settings className="mr-1.5 h-3.5 w-3.5" />
          Configure
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Configure stage: {stage.name}</DialogTitle>
          <DialogDescription>
            Adjust executor, image and script for this pipeline stage.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 pt-1 text-xs">
          <div className="space-y-1.5">
            <Label>Executor</Label>
            <Select
              value={local.config.executor}
              onChange={(e) =>
                setLocal((prev) => ({
                  ...prev,
                  config: { ...prev.config, executor: e.target.value as Executor },
                }))
              }
            >
              <option value="docker">Docker</option>
              <option value="shell">Shell</option>
              <option value="k8s">Kubernetes</option>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label>Image</Label>
            <Input
              placeholder="e.g. node:18-alpine"
              value={local.config.image}
              onChange={(e) =>
                setLocal((prev) => ({
                  ...prev,
                  config: { ...prev.config, image: e.target.value },
                }))
              }
            />
          </div>

          <div className="space-y-1.5">
            <Label>Script</Label>
            <Textarea
              rows={4}
              placeholder="npm ci&#10;npm test"
              value={local.config.script}
              onChange={(e) =>
                setLocal((prev) => ({
                  ...prev,
                  config: { ...prev.config, script: e.target.value },
                }))
              }
            />
          </div>

          <div className="space-y-1.5">
            <Label>Artifacts</Label>
            <Input
              placeholder="e.g. coverage/, dist/"
              value={local.config.artifacts}
              onChange={(e) =>
                setLocal((prev) => ({
                  ...prev,
                  config: { ...prev.config, artifacts: e.target.value },
                }))
              }
            />
          </div>
        </div>

        <div className="mt-4 flex justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setOpen(false)}
          >
            Cancel
          </Button>
          <Button size="sm" onClick={handleSave}>
            Save
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}


