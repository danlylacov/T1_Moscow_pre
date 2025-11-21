"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { GitMerge, Server } from "lucide-react";

export type CiSystem = "gitlab" | "jenkins";

interface SystemSelectorProps {
  value: CiSystem;
  onChange: (value: CiSystem) => void;
}

export function SystemSelector({ value, onChange }: SystemSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>CI/CD System</CardTitle>
      </CardHeader>
      <CardContent>
        <RadioGroup
          value={value}
          onValueChange={(val) => onChange(val as CiSystem)}
          className="grid gap-3 md:grid-cols-2"
        >
          <SystemOption
            id="gitlab"
            value="gitlab"
            label="GitLab CI"
            description="YAML-based pipelines, tightly integrated with GitLab."
            icon={<GitMerge className="h-5 w-5 text-orange-400" />}
            selected={value === "gitlab"}
          />
          <SystemOption
            id="jenkins"
            value="jenkins"
            label="Jenkins"
            description="Flexible pipelines for complex and legacy setups."
            icon={<Server className="h-5 w-5 text-emerald-400" />}
            selected={value === "jenkins"}
          />
        </RadioGroup>
      </CardContent>
    </Card>
  );
}

interface SystemOptionProps {
  id: string;
  value: CiSystem;
  label: string;
  description: string;
  icon: React.ReactNode;
  selected: boolean;
}

function SystemOption({
  id,
  value,
  label,
  description,
  icon,
  selected,
}: SystemOptionProps) {
  return (
    <Label
      htmlFor={id}
      className={`relative flex cursor-pointer flex-col gap-2 rounded-lg border px-4 py-3 text-left text-slate-100 transition-colors ${
        selected
          ? "border-sky-500 bg-slate-950/80 ring-1 ring-sky-500"
          : "border-slate-800 bg-slate-950/60 hover:border-slate-700"
      }`}
    >
      <RadioGroupItem id={id} value={value} />
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900">
            {icon}
          </div>
          <span className="text-sm font-semibold">{label}</span>
        </div>
      </div>
      <p className="text-xs text-slate-400">{description}</p>
    </Label>
  );
}


