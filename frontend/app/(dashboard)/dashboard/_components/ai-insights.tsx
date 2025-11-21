"use client";

import { motion } from "framer-motion";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Lightbulb } from "lucide-react";

const insights = [
  {
    id: "stale-pipelines",
    title: "Pipeline hygiene",
    message: "You haven't updated pipelines in 4 projects. Consider refreshing triggers and test stages.",
    severity: "info" as const,
  },
  {
    id: "unused-template",
    title: "Unused template detected",
    message: "Unused template found: \"legacy-java-build\". Archiving it could simplify your template catalog.",
    severity: "warning" as const,
  },
];

export function AiInsights() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.1 }}
    >
      <Card className="relative overflow-hidden border-violet-600/40 bg-slate-950/60">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(139,92,246,0.18),_transparent_55%),radial-gradient(circle_at_bottom,_rgba(14,165,233,0.16),_transparent_55%)]" />
        <CardHeader className="relative flex flex-row items-center justify-between space-y-0 pb-3">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-violet-600/20 text-violet-200">
              <Brain className="h-4 w-4" />
            </div>
            <div>
              <CardTitle>AI Recommendations</CardTitle>
              <p className="mt-1 text-xs text-slate-300">
                Smart insights generated from your recent activity.
              </p>
            </div>
          </div>
          <Badge className="relative border border-violet-500/40 bg-violet-500/10 text-[10px] text-violet-100">
            AI-powered
          </Badge>
        </CardHeader>
        <CardContent className="relative space-y-3">
          {insights.map((insight, index) => (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.12 + index * 0.05 }}
            >
              <Alert
                variant={insight.severity === "warning" ? "default" : "success"}
                className="border-violet-500/40 bg-slate-950/80/60 text-slate-100"
              >
                <div className="flex items-start gap-2">
                  <div className="mt-0.5">
                    <Lightbulb className="h-4 w-4 text-violet-300" />
                  </div>
                  <div>
                    <AlertTitle className="text-xs font-semibold text-slate-100">
                      {insight.title}
                    </AlertTitle>
                    <AlertDescription className="mt-1 text-[11px] text-slate-300">
                      {insight.message}
                    </AlertDescription>
                  </div>
                </div>
              </Alert>
            </motion.div>
          ))}
        </CardContent>
      </Card>
    </motion.div>
  );
}


