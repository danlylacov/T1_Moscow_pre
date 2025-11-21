"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface SheetContextValue {
  open: boolean;
  setOpen: (open: boolean) => void;
}

const SheetContext = React.createContext<SheetContextValue | null>(null);

function useSheetContext() {
  const ctx = React.useContext(SheetContext);
  if (!ctx) {
    throw new Error("Sheet components must be used within <Sheet>.");
  }
  return ctx;
}

export interface SheetProps {
  children: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export function Sheet({ children, open, onOpenChange }: SheetProps) {
  const [uncontrolled, setUncontrolled] = React.useState(false);
  const isControlled = open !== undefined;
  const actualOpen = isControlled ? open : uncontrolled;

  const setOpen = (next: boolean) => {
    if (!isControlled) {
      setUncontrolled(next);
    }
    onOpenChange?.(next);
  };

  return (
    <SheetContext.Provider value={{ open: actualOpen, setOpen }}>
      {children}
    </SheetContext.Provider>
  );
}

export const SheetTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(({ className, ...props }, ref) => {
  const { open, setOpen } = useSheetContext();
  return (
    <button
      ref={ref}
      type="button"
      aria-haspopup="dialog"
      aria-expanded={open}
      onClick={() => setOpen(!open)}
      className={cn(className)}
      {...props}
    />
  );
});

SheetTrigger.displayName = "SheetTrigger";

export const SheetContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, children, ...props }, ref) => {
  const { open, setOpen } = useSheetContext();
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-black/40">
      <div
        ref={ref}
        className={cn(
          "h-full w-full max-w-md border-l border-slate-800 bg-slate-950 shadow-xl",
          className
        )}
        role="dialog"
        aria-modal="true"
        {...props}
      >
        {children}
        <button
          type="button"
          aria-label="Close"
          className="absolute right-4 top-3 text-xs text-slate-500 hover:text-slate-200"
          onClick={() => setOpen(false)}
        >
          ✕
        </button>
      </div>
    </div>
  );
});

SheetContent.displayName = "SheetContent";


