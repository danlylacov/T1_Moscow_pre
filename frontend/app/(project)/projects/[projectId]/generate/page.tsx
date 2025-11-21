"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Sparkles,
  FileCode,
  CheckCircle,
  Loader2,
  Zap,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const GENERATION_STEPS = [
  "Analyzing project structure...",
  "Matching best-practice templates...",
  "Optimizing cache strategies...",
  "Configuring multi-stage Docker build...",
  "Finalizing YAML syntax...",
] as const;

const MOCK_YAML = `image: node:18-alpine

stages:
  - lint
  - test
  - build

cache:
  paths:
    - node_modules/

lint:
  stage: lint
  script:
    - npm ci
    - npm run lint

test:
  stage: test
  script:
    - npm run test

build:
  stage: build
  script:
    - docker build -t my-app .
`;

interface GeneratePageProps {
  params: {
    projectId: string;
  };
}

export default function GeneratePage({ params }: GeneratePageProps) {
  const [isGenerating, setIsGenerating] = useState(true);
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [runId, setRunId] = useState(0);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setIsGenerating(true);
    setActiveStepIndex(0);

    const stepDuration = 600; // ms
    let currentIndex = 0;

    const interval = setInterval(() => {
      currentIndex += 1;
      if (currentIndex >= GENERATION_STEPS.length - 1) {
        setActiveStepIndex(GENERATION_STEPS.length - 1);
        clearInterval(interval);
        // Small delay to let the last step be visible as "active" before finishing
        setTimeout(() => {
          setIsGenerating(false);
        }, stepDuration);
      } else {
        setActiveStepIndex(currentIndex);
      }
    }, stepDuration);

    return () => {
      clearInterval(interval);
    };
  }, [runId]);

  const handleRegenerate = () => {
    setRunId((id) => id + 1);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(MOCK_YAML);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // noop – clipboard might not be available
    }
  };

  const validateHref = `/projects/${params.projectId}/validate`;

  if (isGenerating) {
    return (
      <div className="min-h-[calc(100vh-4rem)] px-6 py-10 flex items-center justify-center">
        <Card className="relative w-full max-w-3xl overflow-hidden border-slate-800 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
          <motion.div
            className="pointer-events-none absolute -inset-32 rounded-full bg-sky-500/10 blur-3xl"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
          />

          <CardHeader className="relative flex flex-col items-center text-center space-y-4">
            <motion.div
              className="relative flex h-16 w-16 items-center justify-center rounded-2xl border border-sky-500/40 bg-slate-950/80 shadow-[0_0_40px_rgba(56,189,248,0.35)]"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.4 }}
            >
              <motion.div
                className="absolute inset-0 rounded-2xl border border-sky-500/30"
                animate={{
                  opacity: [0.2, 0.7, 0.2],
                  scale: [1, 1.08, 1],
                }}
                transition={{
                  duration: 1.8,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
              <Sparkles className="h-8 w-8 text-sky-400" />
            </motion.div>

            <div className="space-y-1">
              <CardTitle className="text-base font-semibold text-slate-50">
                AI Agent is assembling your pipeline
              </CardTitle>
              <CardDescription className="text-xs text-slate-400">
                We&apos;re analyzing your configuration and applying CI/CD best
                practices.
              </CardDescription>
            </div>
          </CardHeader>

          <CardContent className="relative space-y-6">
            <div className="flex items-center justify-center gap-2 text-xs text-slate-400">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-sky-400" />
              <span>Thinking through build, cache, and deployment strategy…</span>
            </div>

            <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
              <div className="mb-3 flex items-center justify-between text-xs text-slate-400">
                <span>Generation steps</span>
                <span>
                  Step {activeStepIndex + 1} of {GENERATION_STEPS.length}
                </span>
              </div>

              <div className="space-y-2">
                {GENERATION_STEPS.map((step, index) => {
                  const isCompleted = index < activeStepIndex;
                  const isActive = index === activeStepIndex;

                  return (
                    <motion.div
                      key={step}
                      className="flex items-center gap-3 rounded-lg border border-slate-800/80 bg-slate-900/70 px-3 py-2"
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <div className="flex h-6 w-6 items-center justify-center rounded-full border border-slate-700 bg-slate-950/80">
                        {isCompleted ? (
                          <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
                        ) : isActive ? (
                          <Loader2 className="h-3.5 w-3.5 animate-spin text-sky-400" />
                        ) : (
                          <span className="h-1.5 w-1.5 rounded-full bg-slate-600" />
                        )}
                      </div>
                      <div className="flex-1 text-xs text-slate-200">{step}</div>
                    </motion.div>
                  );
                })}
              </div>

              <div className="mt-4 flex items-center justify-between text-[11px] text-slate-500">
                <span>
                  You&apos;ll see the full YAML preview in a few seconds.
                </span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2 text-[11px]"
                  onClick={handleRegenerate}
                >
                  Regenerate
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] px-6 py-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        {/* Strategy summary */}
        <Card className="border-slate-800 bg-slate-950/70">
          <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/10 text-sky-400">
                <Sparkles className="h-5 w-5" />
              </div>
              <div className="space-y-1">
                <CardTitle className="text-base">
                  Generated GitLab CI pipeline for Node.js with Docker strategy
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Based on your project stack, we selected a multi-stage Docker
                  build with caching for dependencies and lean deployment
                  images.
                </CardDescription>
              </div>
            </div>

            <div className="flex flex-col items-start gap-2 sm:items-end">
              <Badge variant="secondary" className="flex items-center gap-1.5">
                <FileCode className="h-3.5 w-3.5 text-sky-400" />
                <span>Template used: node-nest-docker</span>
              </Badge>
              <Badge variant="success" className="flex items-center gap-1.5">
                <Sparkles className="h-3 w-3 text-emerald-300" />
                <span>AI-optimized configuration</span>
              </Badge>
            </div>
          </CardHeader>
        </Card>

        <div className="grid gap-6 lg:grid-cols-[minmax(0,2.2fr)_minmax(0,1fr)]">
          {/* Pipeline preview */}
          <Card className="border-slate-800 bg-slate-950/80">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-md bg-slate-900/80">
                  <FileCode className="h-4 w-4 text-sky-400" />
                </div>
                <div>
                  <CardTitle className="text-sm">Pipeline preview</CardTitle>
                  <CardDescription className="text-[11px] text-slate-400">
                    .gitlab-ci.yml generated from your configuration
                  </CardDescription>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="h-8 gap-1 border-slate-700 bg-slate-950 text-xs"
                  onClick={handleCopy}
                >
                  <Zap className="h-3.5 w-3.5 text-sky-400" />
                  {copied ? "Copied" : "Copy YAML"}
                </Button>
              </div>
            </CardHeader>

            <CardContent className="pt-0">
              <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950/90">
                <div className="flex items-center gap-1 border-b border-slate-800 bg-slate-900/70 px-3 py-1.5 text-[11px] text-slate-400">
                  <span className="h-2 w-2 rounded-full bg-red-500/80" />
                  <span className="h-2 w-2 rounded-full bg-amber-400/80" />
                  <span className="h-2 w-2 rounded-full bg-emerald-500/80" />
                  <span className="ml-2 text-slate-500">
                    .gitlab-ci.yml • YAML preview
                  </span>
                </div>

                <ScrollArea className="max-h-[420px]">
                  <pre className="m-0 bg-transparent p-3 text-[11px] leading-relaxed text-slate-100">
                    <code className="font-mono whitespace-pre">
                      {MOCK_YAML}
                    </code>
                  </pre>
                </ScrollArea>
              </div>
            </CardContent>
          </Card>

          {/* Optimization tips and actions */}
          <div className="flex flex-col gap-4">
            <Card className="border-slate-800 bg-slate-950/80">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-sm">
                  <Zap className="h-4 w-4 text-amber-300" />
                  Optimization tips
                </CardTitle>
                <CardDescription className="text-[11px] text-slate-400">
                  Tuned for fast feedback and reproducible builds.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Alert variant="success" className="text-xs">
                  <AlertTitle className="flex items-center gap-2 text-xs">
                    <CheckCircle className="h-4 w-4 text-emerald-400" />
                    Smart caching
                  </AlertTitle>
                  <AlertDescription>
                    ⚡ Caching enabled for <code>node_modules</code> to speed up
                    repeat runs.
                  </AlertDescription>
                </Alert>

                <Alert variant="default" className="text-xs">
                  <AlertTitle className="flex items-center gap-2 text-xs">
                    <FileCode className="h-4 w-4 text-sky-400" />
                    Docker build optimization
                  </AlertTitle>
                  <AlertDescription>
                    ⚡ Docker layer caching active to avoid rebuilding unchanged
                    layers.
                  </AlertDescription>
                </Alert>

                <Alert variant="default" className="text-xs">
                  <AlertTitle className="flex items-center gap-2 text-xs">
                    <Sparkles className="h-4 w-4 text-sky-400" />
                    Ready for validation
                  </AlertTitle>
                  <AlertDescription>
                    Next step: run a dry-run validation and adjust stages or
                    environment variables if needed.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>

            <Card className="border-slate-800 bg-slate-950/90">
              <CardContent className="flex flex-col gap-3 pt-4">
                <div className="flex flex-col gap-1 text-xs text-slate-400">
                  <span className="font-medium text-slate-200">
                    What&apos;s next?
                  </span>
                  <span>
                    Validate this pipeline against your project to catch
                    potential misconfigurations before committing.
                  </span>
                </div>

                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex gap-2">
                    <Link href={validateHref}>
                      <Button className="gap-1.5">
                        <CheckCircle className="h-4 w-4" />
                        Validate pipeline
                      </Button>
                    </Link>
                    <Button
                      type="button"
                      variant="secondary"
                      className="gap-1.5"
                      onClick={handleRegenerate}
                    >
                      <Loader2 className="h-4 w-4" />
                      Regenerate
                    </Button>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    You can always tweak the YAML in your repo after validating.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

