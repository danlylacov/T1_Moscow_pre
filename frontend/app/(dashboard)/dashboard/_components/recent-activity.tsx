"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowRight, GitBranchPlus, Search } from "lucide-react";

type PipelineStatus = "success" | "failed";

const recentPipelines: {
  id: string;
  project: string;
  status: PipelineStatus;
  date: string;
}[] = [
  {
    id: "1",
    project: "web-platform / self-deploy",
    status: "success",
    date: "2025-11-18 18:42",
  },
  {
    id: "2",
    project: "mobile-ci / android-release",
    status: "failed",
    date: "2025-11-18 17:21",
  },
  {
    id: "3",
    project: "infra / k8s-gateway",
    status: "success",
    date: "2025-11-18 15:09",
  },
  {
    id: "4",
    project: "ml / feature-store-sync",
    status: "success",
    date: "2025-11-18 12:54",
  },
  {
    id: "5",
    project: "legacy / billing-service",
    status: "failed",
    date: "2025-11-18 09:13",
  },
];

function StatusBadge({ status }: { status: PipelineStatus }) {
  if (status === "success") {
    return <Badge variant="success">Success</Badge>;
  }
  return <Badge variant="destructive">Failed</Badge>;
}

export function RecentActivity() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.15 }}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div>
            <CardTitle>Recent Activity</CardTitle>
            <p className="mt-1 text-xs text-slate-400">
              Last 5 generated pipelines across all projects.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm" variant="secondary">
              <Search className="mr-1.5 h-3.5 w-3.5" />
              Analyze Repository
            </Button>
            <Button size="sm">
              <GitBranchPlus className="mr-1.5 h-3.5 w-3.5" />
              Create New Pipeline
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Project</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recentPipelines.map((pipeline) => (
                <TableRow key={pipeline.id}>
                  <TableCell className="font-medium text-slate-100">
                    {pipeline.project}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={pipeline.status} />
                  </TableCell>
                  <TableCell className="text-xs text-slate-400">
                    {pipeline.date}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      size="sm"
                      variant="outline"
                      className="border-slate-700 text-xs"
                    >
                      View
                      <ArrowRight className="ml-1.5 h-3 w-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </motion.div>
  );
}


