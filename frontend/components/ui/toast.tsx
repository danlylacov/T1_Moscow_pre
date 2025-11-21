"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface ToastProps {
  title?: string;
  description?: string;
  variant?: "default" | "success" | "destructive";
}

const variantClasses: Record<NonNullable<ToastProps["variant"]>, string> = {
  default: "border-slate-700 bg-slate-900 text-slate-100",
  success: "border-emerald-500/50 bg-emerald-500/10 text-emerald-50",
  destructive: "border-red-500/50 bg-red-500/10 text-red-50",
};

export function Toast({
  title,
  description,
  variant = "default",
}: ToastProps) {
  return (
    <div
      className={cn(
        "w-full max-w-sm rounded-lg border px-4 py-3 text-xs shadow-lg",
        variantClasses[variant]
      )}
    >
      {title && (
        <div className="mb-1 font-medium leading-tight">{title}</div>
      )}
      {description && (
        <p className="text-[11px] text-inherit/80">{description}</p>
      )}
    </div>
  );
}

interface ToastContextValue {
  showToast: (toast: ToastProps) => void;
}

const ToastContext = React.createContext<ToastContextValue | null>(null);

export function useToast() {
  const ctx = React.useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within <ToastProvider>.");
  }
  return ctx;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [current, setCurrent] = React.useState<ToastProps | null>(null);

  const showToast = (toast: ToastProps) => {
    setCurrent(toast);
    setTimeout(() => setCurrent(null), 2200);
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {current && (
        <div className="pointer-events-none fixed inset-x-0 bottom-4 z-50 flex justify-center">
          <Toast
            title={current.title}
            description={current.description}
            variant={current.variant}
          />
        </div>
      )}
    </ToastContext.Provider>
  );
}


