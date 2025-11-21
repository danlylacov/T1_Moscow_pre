"use client";

import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Cpu, Database, Terminal as TerminalIcon } from "lucide-react";

export interface StackItem {
  id: string;
  label: string;
  value: string;
  type: "language" | "framework" | "test" | "container" | "iac" | "database";
}

const typeLabel: Record<StackItem["type"], string> = {
  language: "Language",
  framework: "Framework",
  test: "Test Runner",
  container: "Container",
  iac: "Infrastructure as Code",
  database: "Database",
};

function TypeIcon({ type }: { type: StackItem["type"] }) {
  if (type === "database") {
    return <Database className="h-4 w-4 text-sky-300" />;
  }
  if (type === "language" || type === "framework" || type === "test") {
    return <Cpu className="h-4 w-4 text-emerald-300" />;
  }
  return <TerminalIcon className="h-4 w-4 text-violet-300" />;
}

interface StackCardProps {
  item: StackItem;
  index: number;
}

export function StackCard({ item, index }: StackCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: 0.05 * index }}
    >
      <Card className="bg-slate-950/70">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-md bg-slate-900">
              <TypeIcon type={item.type} />
            </div>
            <CardTitle>{item.label}</CardTitle>
          </div>
          <Badge variant="secondary" className="text-[10px]">
            {typeLabel[item.type]}
          </Badge>
        </CardHeader>
        <CardContent>
          <p className="text-sm font-semibold text-slate-50">{item.value}</p>
        </CardContent>
      </Card>
    </motion.div>
  );
}


