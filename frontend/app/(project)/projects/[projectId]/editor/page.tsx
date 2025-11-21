"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import {
  Save,
  GitPullRequest,
  Play,
  Check,
  XCircle,
  Sparkles,
  History,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ToastProvider } from "@/components/ui/toast";

import { CodeEditor } from "./_components/code-editor";
import { PublishDialog } from "./_components/publish-dialog";
import { SuccessView } from "./_components/success-view";

const BASE_YAML = `image: node:18-alpine

stages:
  - lint
  - test
  - build

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

const ENHANCED_YAML = `image: node:18-alpine

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

export default function EditorPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params?.projectId ?? "unknown";
  const [code, setCode] = useState(ENHANCED_YAML);
  const [mode, setMode] = useState<"edit" | "diff">("edit");
  const [publishOpen, setPublishOpen] = useState(false);
  const [isPublished, setIsPublished] = useState(false);

  const handlePublished = () => {
    setIsPublished(true);
  };

  if (isPublished) {
    return <SuccessView projectId={projectId} />;
  }

  const linesBase = BASE_YAML.split("\n");
  const linesEnhanced = code.split("\n");

  const maxLines = Math.max(linesBase.length, linesEnhanced.length);

  return (
    <ToastProvider>
      <div className="min-h-[calc(100vh-4rem)] bg-slate-950 px-6 py-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-4">
          {/* Toolbar */}
          <Card className="border-slate-800 bg-slate-950/90">
            <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900">
                  <Save className="h-5 w-5 text-sky-400" />
                </div>
                <div className="space-y-1">
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <span className="font-mono text-slate-50">
                      .gitlab-ci.yml
                    </span>
                    <Badge variant="success" className="text-[10px]">
                      Lint passed
                    </Badge>
                  </CardTitle>
                  <CardDescription className="text-xs text-slate-400">
                    Review and fine-tune the generated pipeline before pushing
                    it to Git.
                  </CardDescription>
                </div>
              </div>
              <div className="flex flex-col items-stretch gap-2 sm:flex-row sm:items-center">
                <Tabs
                  defaultValue="edit"
                  value={mode}
                  onValueChange={(v) => setMode(v as "edit" | "diff")}
                >
                  <TabsList>
                    <TabsTrigger value="edit">Edit</TabsTrigger>
                    <TabsTrigger value="diff">Diff</TabsTrigger>
                  </TabsList>
                </Tabs>

                <Sheet>
                  <SheetTrigger className="h-9 rounded-md border border-slate-800 bg-slate-950 px-3 text-xs text-slate-200 hover:border-sky-500 hover:bg-slate-900 flex items-center gap-1.5">
                    <Sparkles className="h-4 w-4 text-sky-400" />
                    AI assistant
                  </SheetTrigger>
                  <SheetContent>
                    <div className="flex h-full flex-col">
                      <div className="border-b border-slate-800 px-4 py-3">
                        <p className="text-xs font-medium text-slate-100">
                          AI assistant
                        </p>
                        <p className="text-[11px] text-slate-500">
                          Ask questions about this pipeline or request safe
                          optimizations.
                        </p>
                      </div>
                      <ScrollArea className="flex-1 px-4 py-3">
                        <div className="space-y-3 text-xs text-slate-200">
                          <div className="rounded-md bg-slate-900 px-3 py-2">
                            <p className="text-[11px] text-slate-400">
                              Suggestion
                            </p>
                            <p>
                              You can split the <code>build</code> job into{" "}
                              <code>build</code> and <code>publish</code>{" "}
                              stages to separate image creation from registry
                              pushes.
                            </p>
                          </div>
                          <div className="rounded-md bg-slate-900 px-3 py-2">
                            <p className="text-[11px] text-slate-400">
                              Security tip
                            </p>
                            <p>
                              Avoid running containers with{" "}
                              <code>--privileged</code>. Prefer granular
                              capabilities or non-root users.
                            </p>
                          </div>
                          <div className="rounded-md bg-slate-900 px-3 py-2">
                            <p className="text-[11px] text-slate-400">
                              Quick question
                            </p>
                            <p>
                              &quot;How can I add a manual deploy stage that
                              only runs on the main branch?&quot;
                            </p>
                          </div>
                        </div>
                      </ScrollArea>
                      <div className="border-t border-slate-800 px-4 py-3">
                        <div className="flex items-center gap-2">
                          <input
                            className="h-8 flex-1 rounded-md border border-slate-800 bg-slate-950 px-2 text-xs text-slate-100 outline-none focus-visible:ring-2 focus-visible:ring-sky-500"
                            placeholder="Ask the assistant about a specific job or stage…"
                          />
                          <Button className="h-8 px-3 text-xs">
                            Send
                          </Button>
                        </div>
                      </div>
                    </div>
                  </SheetContent>
                </Sheet>
              </div>
            </CardHeader>
          </Card>

          {/* Main body */}
          <Card className="border-slate-800 bg-slate-950/95">
            <CardContent className="flex flex-col gap-4 pt-4">
              {mode === "edit" ? (
                <CodeEditor code={code} onChange={setCode} />
              ) : (
                <div className="relative flex h-[520px] rounded-xl border border-slate-800 bg-slate-950/90">
                  <ScrollArea className="flex-1 rounded-xl bg-slate-950">
                    <div className="flex font-mono text-[11px] leading-relaxed">
                      <div className="select-none border-r border-slate-800 bg-slate-950/95 px-3 py-3 text-right text-[10px] text-slate-500">
                        {Array.from({ length: maxLines }).map((_, index) => (
                          <div key={index} className="h-4">
                            {index + 1}
                          </div>
                        ))}
                      </div>
                      <div className="flex-1 px-3 py-3">
                        {Array.from({ length: maxLines }).map((_, index) => {
                          const baseLine = linesBase[index] ?? "";
                          const enhancedLine = linesEnhanced[index] ?? "";

                          if (baseLine === enhancedLine) {
                            return (
                              <div
                                key={index}
                                className="h-4 whitespace-pre text-slate-100"
                              >
                                {enhancedLine}
                              </div>
                            );
                          }

                          if (!baseLine && enhancedLine) {
                            return (
                              <div
                                key={index}
                                className="h-4 whitespace-pre bg-emerald-500/10 text-emerald-200"
                              >
                                + {enhancedLine}
                              </div>
                            );
                          }

                          if (baseLine && !enhancedLine) {
                            return (
                              <div
                                key={index}
                                className="h-4 whitespace-pre bg-red-500/10 text-red-200 line-through"
                              >
                                - {baseLine}
                              </div>
                            );
                          }

                          return (
                            <div key={index} className="flex h-4 flex-col">
                              <span className="whitespace-pre bg-red-500/10 text-red-200 line-through">
                                - {baseLine}
                              </span>
                              <span className="whitespace-pre bg-emerald-500/10 text-emerald-200">
                                + {enhancedLine}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </ScrollArea>
                </div>
              )}

              <div className="flex flex-col justify-between gap-3 border-t border-slate-800 pt-3 text-xs text-slate-400 sm:flex-row sm:items-center">
                <div className="flex items-center gap-2">
                  <Badge variant="secondary" className="flex items-center gap-1.5 text-[10px]">
                    <History className="h-3.5 w-3.5 text-slate-300" />
                    Last validation: just now • No blocking issues
                  </Badge>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <Link href={`/projects/${params.projectId}/validate`}>
                    <Button
                      type="button"
                      variant="secondary"
                      className="h-8 gap-1.5 px-3 text-xs"
                    >
                      <XCircle className="h-4 w-4" />
                      Back to validation
                    </Button>
                  </Link>
                  <Button
                    type="button"
                    variant="outline"
                    className="h-8 gap-1.5 border-slate-700 px-3 text-xs"
                  >
                    <Play className="h-4 w-4 text-emerald-400" />
                    Dry-run pipeline
                  </Button>
                  <Button
                    type="button"
                    className="h-8 gap-1.5 bg-emerald-500 px-3 text-xs text-slate-950 hover:bg-emerald-400"
                    onClick={() => setPublishOpen(true)}
                  >
                    <GitPullRequest className="h-4 w-4" />
                    Commit &amp; push
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <PublishDialog
          open={publishOpen}
          onOpenChange={setPublishOpen}
          onPublished={handlePublished}
        />
      </div>
    </ToastProvider>
  );
}

