"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const stats = [
  {
    label: "Total Pipelines Created",
    value: "1,240",
    description: "All environments, last 30 days",
  },
  {
    label: "Avg. Test Duration",
    value: "4m 12s",
    description: "Median across active pipelines",
  },
  {
    label: "Validation Errors Prevented",
    value: "342",
    description: "Blocked before merging to main",
    highlight: true,
  },
];

export function StatsOverview() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <Card>
        <CardHeader className="pb-2">
          <CardTitle>Global Statistics</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="flex flex-col justify-between rounded-lg border border-slate-800/80 bg-slate-950/40 p-3"
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-xs font-medium text-slate-400">
                  {stat.label}
                </p>
                {stat.highlight && (
                  <Badge variant="success" className="text-[10px]">
                    Success
                  </Badge>
                )}
              </div>
              <p className="mt-2 text-xl font-semibold text-slate-50">
                {stat.value}
              </p>
              <p className="mt-1 text-[11px] text-slate-500">
                {stat.description}
              </p>
            </div>
          ))}
        </CardContent>
      </Card>
    </motion.div>
  );
}


