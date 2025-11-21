"use client";

import * as React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

export interface CodeEditorProps {
  code: string;
  onChange: (value: string) => void;
}

export function CodeEditor({ code, onChange }: CodeEditorProps) {
  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(event.target.value);
  };

  const lines = React.useMemo(() => code.split("\n"), [code]);

  return (
    <div className="relative flex h-[520px] rounded-xl border border-slate-800 bg-slate-950/90">
      <ScrollArea className="flex-1 rounded-l-xl bg-slate-950">
        <div className="flex font-mono text-[11px] leading-relaxed text-slate-100">
          <div className="select-none border-r border-slate-800 bg-slate-950/95 px-3 py-3 text-right text-[10px] text-slate-500">
            {lines.map((_, index) => (
              <div key={index} className="h-4">
                {index + 1}
              </div>
            ))}
          </div>
          <textarea
            value={code}
            spellCheck={false}
            onChange={handleChange}
            className={cn(
              "min-h-full w-full resize-none border-0 bg-transparent px-3 py-3 outline-none",
              "font-mono text-[11px] leading-relaxed text-slate-100",
              "focus-visible:ring-0"
            )}
          />
        </div>
      </ScrollArea>
    </div>
  );
}


