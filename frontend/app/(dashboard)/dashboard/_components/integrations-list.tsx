"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Github, Gitlab, Server } from "lucide-react";

const integrations = [
  {
    id: "github",
    name: "GitHub",
    projects: 27,
    icon: Github,
    accent: "from-sky-500/40 to-sky-400/10",
  },
  {
    id: "gitlab-cloud",
    name: "GitLab Cloud",
    projects: 14,
    icon: Gitlab,
    accent: "from-pink-500/40 to-orange-400/10",
  },
  {
    id: "gitlab-self",
    name: "Self-hosted GitLab",
    projects: 52,
    icon: Server,
    accent: "from-emerald-500/40 to-emerald-400/10",
  },
];

export function IntegrationsList() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.05 }}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle>Platform Status &amp; Integrations</CardTitle>
            <p className="mt-1 text-xs text-slate-400">
              Connected VCS providers across your organization.
            </p>
          </div>
          <Button size="sm">Connect new integration</Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {integrations.map((integration) => {
            const Icon = integration.icon;
            return (
              <div
                key={integration.id}
                className="flex items-center justify-between rounded-lg border border-slate-800/80 bg-slate-950/40 px-3 py-2"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-slate-900 to-slate-950">
                    <div
                      className={`flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br ${integration.accent}`}
                    >
                      <Icon className="h-4 w-4 text-slate-50" />
                    </div>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-100">
                      {integration.name}
                    </p>
                    <p className="text-xs text-slate-500">
                      {integration.projects} projects connected
                    </p>
                  </div>
                </div>
                <Badge variant="secondary" className="text-[10px]">
                  Active
                </Badge>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </motion.div>
  );
}


