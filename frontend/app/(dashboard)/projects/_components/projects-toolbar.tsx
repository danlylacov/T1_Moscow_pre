"use client";

import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Layers, Search, Filter } from "lucide-react";

export type PlatformFilter = "all" | "github" | "gitlab" | "gitlab-self";
export type LanguageFilter = "all" | "ts" | "python" | "go" | "java";
export type StatusFilter = "all" | "has-ci" | "missing-ci" | "has-docker";

interface ProjectsToolbarProps {
  search: string;
  onSearchChange: (value: string) => void;
  platform: PlatformFilter;
  onPlatformChange: (value: PlatformFilter) => void;
  language: LanguageFilter;
  onLanguageChange: (value: LanguageFilter) => void;
  status: StatusFilter;
  onStatusChange: (value: StatusFilter) => void;
  bulkMode: boolean;
  onBulkModeChange: (value: boolean) => void;
}

export function ProjectsToolbar({
  search,
  onSearchChange,
  platform,
  onPlatformChange,
  language,
  onLanguageChange,
  status,
  onStatusChange,
  bulkMode,
  onBulkModeChange,
}: ProjectsToolbarProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-50">
            Projects
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            All imported repositories from GitHub and GitLab.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Layers className="h-3.5 w-3.5 text-slate-500" />
          <span>Bulk Mode</span>
          <Switch
            checked={bulkMode}
            onCheckedChange={onBulkModeChange}
            aria-label="Toggle bulk mode"
          />
        </div>
      </div>

      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <Input
            placeholder="Search projects by name..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
        <div className="inline-flex items-center gap-1 rounded-full border border-slate-800 bg-slate-950 px-2 py-1">
          <Filter className="h-3 w-3 text-slate-500" />
          <span className="font-medium">Filters</span>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="w-14 text-right text-[11px] uppercase tracking-wide text-slate-500">
              Platform
            </span>
            <Select
              value={platform}
              onChange={(e) =>
                onPlatformChange(e.target.value as PlatformFilter)
              }
            >
              <option value="all">All</option>
              <option value="github">GitHub</option>
              <option value="gitlab">GitLab</option>
              <option value="gitlab-self">Self-hosted</option>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-14 text-right text-[11px] uppercase tracking-wide text-slate-500">
              Language
            </span>
            <Select
              value={language}
              onChange={(e) =>
                onLanguageChange(e.target.value as LanguageFilter)
              }
            >
              <option value="all">All</option>
              <option value="ts">TypeScript</option>
              <option value="python">Python</option>
              <option value="go">Go</option>
              <option value="java">Java</option>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-14 text-right text-[11px] uppercase tracking-wide text-slate-500">
              Status
            </span>
            <Select
              value={status}
              onChange={(e) =>
                onStatusChange(e.target.value as StatusFilter)
              }
            >
              <option value="all">All</option>
              <option value="has-ci">Has CI/CD</option>
              <option value="missing-ci">Missing CI/CD</option>
              <option value="has-docker">Has Dockerfile</option>
            </Select>
          </div>
        </div>
      </div>
    </div>
  );
}


