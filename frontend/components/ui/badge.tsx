"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type BadgeVariant = "default" | "secondary" | "success" | "destructive" | "outline";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: "bg-slate-800 text-slate-50",
  secondary: "bg-slate-900 text-slate-300 border border-slate-700",
  success: "bg-emerald-500/10 text-emerald-300 border border-emerald-500/40",
  destructive: "bg-red-500/10 text-red-300 border border-red-500/40",
  outline: "border border-slate-700 text-slate-200",
};

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}


