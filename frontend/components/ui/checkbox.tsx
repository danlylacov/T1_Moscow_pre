"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface CheckboxProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {}

export const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, checked, ...props }, ref) => {
    return (
      <label className="inline-flex items-center gap-2 text-sm text-slate-100">
        <span
          className={cn(
            "relative flex h-4 w-4 items-center justify-center rounded border border-slate-700 bg-slate-950",
            checked && "border-sky-400 bg-sky-500/20"
          )}
        >
          <input
            ref={ref}
            type="checkbox"
            className="peer absolute inset-0 h-full w-full cursor-pointer opacity-0"
            checked={checked}
            {...props}
          />
          <span
            className={cn(
              "pointer-events-none h-2.5 w-2.5 rounded-sm bg-sky-400 opacity-0 transition-opacity",
              checked && "opacity-100"
            )}
          />
        </span>
        {props["aria-label"] && (
          <span className="text-xs text-slate-300">{props["aria-label"]}</span>
        )}
      </label>
    );
  }
);

Checkbox.displayName = "Checkbox";


