"use client";

import { Bot, FileText, ChevronRight } from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export function AIExplanation() {
  return (
    <div className="space-y-5">
      <Card className="border-slate-800 bg-slate-950/85">
        <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-3">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/10 text-sky-400">
              <Bot className="h-5 w-5" />
            </div>
            <div className="space-y-1">
              <CardTitle className="text-sm">
                AI explanation of your pipeline
              </CardTitle>
              <CardDescription className="text-xs text-slate-400">
                Human-readable summary of what this <code>.gitlab-ci.yml</code>{" "}
                does and why it was designed this way.
              </CardDescription>
            </div>
          </div>
          <Badge variant="secondary" className="text-[10px]">
            Infrastructure as text
          </Badge>
        </CardHeader>
        <CardContent className="space-y-3 text-xs leading-relaxed text-slate-200">
          <p>
            This pipeline automates the Node.js build process using Docker. It
            enforces a clear separation between lint, test, and build stages so
            that failures surface early and production images are only built
            from code that has passed quality checks.
          </p>
          <p className="text-slate-400">
            Dependencies are cached across runs and build logic is encapsulated
            in Docker images, making local and CI environments behave
            consistently.
          </p>
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/90">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm">
            <FileText className="h-4 w-4 text-sky-400" />
            Pipeline stages as a timeline
          </CardTitle>
          <CardDescription className="text-[11px] text-slate-400">
            Expand each stage to see how it contributes to your delivery flow.
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-1 text-xs text-slate-200">
          <Accordion type="single" collapsible defaultValue="build">
            <AccordionItem value="build">
              <AccordionTrigger className="text-xs">
                <div className="flex items-center gap-2">
                  <ChevronRight className="h-3 w-3 text-slate-500" />
                  <span className="font-medium text-slate-100">
                    Build stage
                  </span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <p className="mb-1">
                  Compiles your Node.js application using the official{" "}
                  <code>node:18-alpine</code> image. It installs dependencies
                  and prepares the app for downstream jobs.
                </p>
                <p className="text-slate-400">
                  Caches <code>node_modules</code> between runs to reuse
                  previously downloaded packages, typically reducing CI time by
                  around 40% on subsequent pipelines.
                </p>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="test">
              <AccordionTrigger className="text-xs">
                <div className="flex items-center gap-2">
                  <ChevronRight className="h-3 w-3 text-slate-500" />
                  <span className="font-medium text-slate-100">
                    Test stage
                  </span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <p className="mb-1">
                  Runs your automated test suite (for example, Jest or pytest)
                  to validate application behaviour on every change.
                </p>
                <p className="text-slate-400">
                  Test results and coverage reports can be published as CI
                  artifacts, giving visibility into code health and preventing
                  regressions from being merged.
                </p>
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="docker-build">
              <AccordionTrigger className="text-xs">
                <div className="flex items-center gap-2">
                  <ChevronRight className="h-3 w-3 text-slate-500" />
                  <span className="font-medium text-slate-100">
                    Docker build & image optimization
                  </span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <p className="mb-1">
                  Builds a Docker image for the application, typically using a
                  multi-stage Dockerfile so that build-time tools are not
                  shipped in the final image.
                </p>
                <p className="text-slate-400">
                  This keeps the runtime container small, improves startup time,
                  and reduces the attack surface by only including what is
                  needed to run the app in production.
                </p>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </CardContent>
      </Card>
    </div>
  );
}


