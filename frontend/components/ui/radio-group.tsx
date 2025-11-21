"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface RadioGroupProps {
  value: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

interface RadioGroupItemProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> {
  value: string;
}

const RadioGroupContext = React.createContext<{
  value: string;
  setValue: (value: string) => void;
} | null>(null);

export function RadioGroup({
  value,
  onValueChange,
  children,
  className,
}: RadioGroupProps) {
  const setValue = (next: string) => {
    onValueChange?.(next);
  };

  return (
    <RadioGroupContext.Provider value={{ value, setValue }}>
      <div className={cn("flex flex-col gap-2", className)}>{children}</div>
    </RadioGroupContext.Provider>
  );
}

export const RadioGroupItem = React.forwardRef<
  HTMLInputElement,
  RadioGroupItemProps
>(({ className, value, ...props }, ref) => {
  const ctx = React.useContext(RadioGroupContext);
  if (!ctx) {
    throw new Error("RadioGroupItem must be used within a RadioGroup");
  }
  const checked = ctx.value === value;

  return (
    <input
      ref={ref}
      type="radio"
      value={value}
      checked={checked}
      onChange={() => ctx.setValue(value)}
      className={cn("sr-only", className)}
      {...props}
    />
  );
});

RadioGroupItem.displayName = "RadioGroupItem";


