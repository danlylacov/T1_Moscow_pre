"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SystemSelector, type CiSystem } from "./_components/system-selector";
import {
  TriggerSelector,
  type TriggerKey,
} from "./_components/trigger-selector";
import {
  StagesList,
} from "./_components/stages-list";
import {
  Stage,
  StageConfig,
} from "./_components/stage-settings-dialog";
import { GitMerge } from "lucide-react";

const defaultStageConfig: StageConfig = {
  executor: "docker",
  image: "node:18-alpine",
  script: "npm ci\nnpm test",
  artifacts: "coverage/, dist/",
};

const defaultStages: Stage[] = [
  {
    id: "lint",
    name: "Lint",
    description: "Runs ESLint and static checks.",
    enabled: true,
    config: {
      ...defaultStageConfig,
      script: "npm ci\nnpm run lint",
    },
  },
  {
    id: "tests",
    name: "Tests",
    description: "Executes unit and integration test suites.",
    enabled: true,
    config: {
      ...defaultStageConfig,
      script: "npm ci\nnpm test",
    },
  },
  {
    id: "build",
    name: "Build Image",
    description: "Builds Docker image using detected Dockerfile.",
    enabled: true,
    config: {
      ...defaultStageConfig,
      script: "docker build -t app:latest .",
      artifacts: "image.tar",
    },
  },
  {
    id: "security",
    name: "Security Scan",
    description: "Runs SAST/Dependency scanning tools.",
    enabled: false,
    config: {
      ...defaultStageConfig,
      script: "npm ci\nnpm run security:scan",
    },
  },
  {
    id: "deploy",
    name: "Deploy to K8s",
    description: "Applies Kubernetes manifests to target cluster.",
    enabled: false,
    config: {
      ...defaultStageConfig,
      executor: "k8s",
      image: "bitnami/kubectl:latest",
      script: "kubectl apply -f k8s/",
      artifacts: "k8s/",
    },
  },
];

export default function Page({
  params,
}: {
  params: { projectId: string };
}) {
  const router = useRouter();
  const [system, setSystem] = useState<CiSystem>("gitlab");
  const [triggers, setTriggers] = useState<TriggerKey[]>([
    "on-push",
    "on-merge-request",
  ]);
  const [stages, setStages] = useState<Stage[]>(defaultStages);

  const handleBack = () => {
    router.push(`/projects/${params.projectId}/analyze`);
  };

  const handleNext = () => {
    router.push(`/projects/${params.projectId}/generate`);
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-50">
            Configure CI/CD
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Step 2 of 5 · Choose system, triggers and stages for{" "}
            <span className="font-mono text-slate-200">
              {params.projectId}
            </span>
          </p>
        </div>
        <Badge variant="secondary" className="flex items-center gap-1">
          <GitMerge className="h-3.5 w-3.5 text-sky-400" />
          <span className="text-[11px]">Configurator</span>
        </Badge>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,1.3fr)]">
        <div className="space-y-4">
          <SystemSelector value={system} onChange={setSystem} />
          <TriggerSelector value={triggers} onChange={setTriggers} />
        </div>
        <div className="space-y-4">
          <StagesList stages={stages} onChange={setStages} />
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-slate-800 pt-4">
        <Button variant="ghost" onClick={handleBack}>
          Back to Analysis
        </Button>
        <Button onClick={handleNext}>
          Generate Pipeline
        </Button>
      </div>
    </div>
  );
}

