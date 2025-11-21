"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Terminal } from "lucide-react";

export interface AnalysisTerminalProps {
  logs: string[];
}

export function AnalysisTerminal({ logs }: AnalysisTerminalProps) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/80">
      <div className="flex items-center gap-2 border-b border-slate-800 px-3 py-2 text-xs text-slate-400">
        <Terminal className="h-3.5 w-3.5 text-slate-500" />
        <span>Analysis log</span>
      </div>
      <ScrollArea className="max-h-56 rounded-b-xl bg-slate-950 p-3 font-mono text-[11px] text-slate-300">
        <AnimatePresence initial={false}>
          {logs.map((line, index) => (
            <motion.div
              key={`${line}-${index}`}
              initial={{ opacity: 0, y: 2 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -2 }}
              transition={{ duration: 0.15 }}
              className="flex gap-2"
            >
              <span className="select-none text-slate-600">&gt;</span>
              <span>{line}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </ScrollArea>
    </div>
  );
}


