"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface AccordionContextValue {
  value: string | null;
  setValue: (value: string | null) => void;
  collapsible: boolean;
}

const AccordionContext = React.createContext<AccordionContextValue | undefined>(
  undefined
);

function useAccordionContext() {
  const context = React.useContext(AccordionContext);
  if (!context) {
    throw new Error("Accordion components must be used within <Accordion>");
  }
  return context;
}

export interface AccordionProps
  extends React.HTMLAttributes<HTMLDivElement> {
  type?: "single";
  defaultValue?: string;
  value?: string | null;
  onValueChange?: (value: string | null) => void;
  collapsible?: boolean;
}

export function Accordion({
  type = "single",
  defaultValue,
  value: valueProp,
  onValueChange,
  collapsible = true,
  className,
  children,
  ...props
}: AccordionProps) {
  const [uncontrolled, setUncontrolled] = React.useState<string | null>(
    defaultValue ?? null
  );
  const value = valueProp ?? uncontrolled;

  const setValue = React.useCallback(
    (next: string | null) => {
      if (type !== "single") return;
      if (valueProp === undefined) {
        setUncontrolled(next);
      }
      onValueChange?.(next);
    },
    [onValueChange, type, valueProp]
  );

  return (
    <AccordionContext.Provider
      value={{ value, setValue, collapsible }}
    >
      <div className={cn("space-y-1", className)} {...props}>
        {children}
      </div>
    </AccordionContext.Provider>
  );
}

interface AccordionItemContextValue {
  itemValue: string;
}

const AccordionItemContext =
  React.createContext<AccordionItemContextValue | null>(null);

export interface AccordionItemProps
  extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
}

export function AccordionItem({
  value,
  className,
  children,
  ...props
}: AccordionItemProps) {
  return (
    <AccordionItemContext.Provider value={{ itemValue: value }}>
      <div
        className={cn(
          "overflow-hidden rounded-md border border-slate-800 bg-slate-950/80",
          className
        )}
        {...props}
      >
        {children}
      </div>
    </AccordionItemContext.Provider>
  );
}

function useAccordionItemContext() {
  const context = React.useContext(AccordionItemContext);
  if (!context) {
    throw new Error(
      "AccordionTrigger and AccordionContent must be used within <AccordionItem>"
    );
  }
  return context;
}

export interface AccordionTriggerProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export function AccordionTrigger({
  className,
  children,
  ...props
}: AccordionTriggerProps) {
  const { itemValue } = useAccordionItemContext();
  const { value, setValue, collapsible } = useAccordionContext();

  const open = value === itemValue;

  const toggle = () => {
    if (open && collapsible) {
      setValue(null);
    } else {
      setValue(itemValue);
    }
  };

  return (
    <button
      type="button"
      onClick={toggle}
      data-state={open ? "open" : "closed"}
      className={cn(
        "flex w-full items-center justify-between gap-2 px-3 py-2 text-left text-xs font-medium text-slate-200 hover:bg-slate-900",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export interface AccordionContentProps
  extends React.HTMLAttributes<HTMLDivElement> {}

export function AccordionContent({
  className,
  children,
  ...props
}: AccordionContentProps) {
  const { itemValue } = useAccordionItemContext();
  const { value } = useAccordionContext();

  const open = value === itemValue;

  return (
    <div
      data-state={open ? "open" : "closed"}
      className={cn(
        "border-t border-slate-800 text-xs text-slate-300",
        !open && "hidden",
        className
      )}
      {...props}
    >
      <div className="px-3 py-2">{children}</div>
    </div>
  );
}


