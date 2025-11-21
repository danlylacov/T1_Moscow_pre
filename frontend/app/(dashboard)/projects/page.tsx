"use client";

import { useMemo, useState } from "react";
import { ProjectsToolbar, PlatformFilter, LanguageFilter, StatusFilter } from "./_components/projects-toolbar";
import { ProjectsTable, projectsMock, Project } from "./_components/projects-table";

export default function Page() {
  const [search, setSearch] = useState("");
  const [platform, setPlatform] = useState<PlatformFilter>("all");
  const [language, setLanguage] = useState<LanguageFilter>("all");
  const [status, setStatus] = useState<StatusFilter>("all");
  const [bulkMode, setBulkMode] = useState(false);

  const filteredProjects = useMemo<Project[]>(() => {
    return projectsMock.filter((project) => {
      if (
        search &&
        !project.name.toLowerCase().includes(search.toLowerCase()) &&
        !project.repoPath.toLowerCase().includes(search.toLowerCase())
      ) {
        return false;
      }

      if (platform !== "all" && project.platform !== platform) {
        return false;
      }

      if (language !== "all" && project.language !== language) {
        return false;
      }

      if (status === "has-ci" && !project.hasCi) return false;
      if (status === "missing-ci" && project.hasCi) return false;
      if (status === "has-docker" && !project.hasDockerfile) return false;

      return true;
    });
  }, [search, platform, language, status]);

  return (
    <div className="space-y-6">
      <ProjectsToolbar
        search={search}
        onSearchChange={setSearch}
        platform={platform}
        onPlatformChange={setPlatform}
        language={language}
        onLanguageChange={setLanguage}
        status={status}
        onStatusChange={setStatus}
        bulkMode={bulkMode}
        onBulkModeChange={setBulkMode}
      />
      <ProjectsTable projects={filteredProjects} />
    </div>
  );
}

