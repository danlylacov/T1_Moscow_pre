"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface SwitchProps
  extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "onChange"> {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
}

export const Switch = React.forwardRef<HTMLButtonElement, SwitchProps>(
  ({ className, checked = false, onCheckedChange, ...props }, ref) => {
    return (
      <button
        ref={ref}
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onCheckedChange?.(!checked)}
        className={cn(
          "inline-flex h-5 w-9 items-center rounded-full border border-slate-700 bg-slate-900 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950",
          checked && "bg-sky-500 border-sky-400",
          className
        )}
        {...props}
      >
        <span
          className={cn(
            "ml-0.5 inline-block h-3.5 w-3.5 rounded-full bg-slate-300 transition-transform",
            checked && "translate-x-3.5 bg-slate-950"
          )}
        />
      </button>
    );
  }
);

Switch.displayName = "Switch";


