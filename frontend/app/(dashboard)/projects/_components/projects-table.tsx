"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  CheckCircle2,
  CircleSlash,
  GitBranch,
  Github,
  Gitlab,
  Layers,
  MoreVertical,
  Play,
} from "lucide-react";

export type Platform = "github" | "gitlab" | "gitlab-self";

export interface Project {
  id: string;
  name: string;
  repoPath: string;
  platform: Platform;
  language: "ts" | "python" | "go" | "java";
  stack: string[];
  branch: string;
  hasCi: boolean;
  hasDockerfile: boolean;
  lastActivity: string;
}

const projectsMock: Project[] = [
  {
    id: "1",
    name: "shop-frontend",
    repoPath: "acme/shop-frontend",
    platform: "github",
    language: "ts",
    stack: ["Next.js", "TypeScript", "Node.js", "Docker"],
    branch: "main",
    hasCi: false,
    hasDockerfile: true,
    lastActivity: "12 min ago",
  },
  {
    id: "2",
    name: "api-gateway",
    repoPath: "platform/api-gateway",
    platform: "gitlab",
    language: "go",
    stack: ["Go", "Docker", "Kubernetes"],
    branch: "main",
    hasCi: true,
    hasDockerfile: true,
    lastActivity: "2h ago",
  },
  {
    id: "3",
    name: "legacy-auth",
    repoPath: "legacy/legacy-auth",
    platform: "gitlab-self",
    language: "java",
    stack: ["Java", "Spring Boot"],
    branch: "master",
    hasCi: false,
    hasDockerfile: false,
    lastActivity: "5h ago",
  },
  {
    id: "4",
    name: "ml-feature-store",
    repoPath: "ml/feature-store",
    platform: "github",
    language: "python",
    stack: ["Python", "FastAPI", "Docker"],
    branch: "main",
    hasCi: true,
    hasDockerfile: true,
    lastActivity: "1d ago",
  },
  {
    id: "5",
    name: "internal-dashboard",
    repoPath: "tools/internal-dashboard",
    platform: "gitlab",
    language: "ts",
    stack: ["React", "Node.js"],
    branch: "develop",
    hasCi: true,
    hasDockerfile: false,
    lastActivity: "3d ago",
  },
];

function PlatformIcon({ platform }: { platform: Platform }) {
  if (platform === "github") {
    return <Github className="h-4 w-4 text-slate-300" />;
  }
  if (platform === "gitlab") {
    return <Gitlab className="h-4 w-4 text-orange-400" />;
  }
  return <Gitlab className="h-4 w-4 text-emerald-400" />;
}

function CiStatus({ hasCi }: { hasCi: boolean }) {
  if (hasCi) {
    return (
      <div className="inline-flex items-center gap-1 text-xs text-emerald-300">
        <CheckCircle2 className="h-3.5 w-3.5" />
        <span>Active</span>
      </div>
    );
  }
  return (
    <div className="inline-flex items-center gap-1 text-xs text-slate-400">
      <CircleSlash className="h-3.5 w-3.5" />
      <span>Missing</span>
    </div>
  );
}

interface ProjectsTableProps {
  projects?: Project[];
}

export function ProjectsTable({ projects }: ProjectsTableProps) {
  const router = useRouter();
  const data = projects ?? projectsMock;

  const handlePrimaryAction = useCallback(
    (project: Project) => {
      if (project.hasCi) {
        router.push(`/projects/${project.id}/editor`);
      } else {
        router.push(`/projects/${project.id}/analyze`);
      }
    },
    [router]
  );

  const handleAnalyze = (project: Project) => {
    router.push(`/projects/${project.id}/analyze`);
  };

  const handleViewBranches = (project: Project) => {
    // Placeholder route for branches view
    router.push(`/projects/${project.id}/branches`);
  };

  const handleSettings = (project: Project) => {
    router.push(`/projects/${project.id}/settings`);
  };

  return (
    <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/60">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Project</TableHead>
            <TableHead>Stack</TableHead>
            <TableHead>Branch</TableHead>
            <TableHead>CI/CD Status</TableHead>
            <TableHead>Last Activity</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((project) => (
            <TableRow key={project.id}>
              <TableCell>
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900">
                    <PlatformIcon platform={project.platform} />
                  </div>
                  <div>
                    <div className="flex items-center gap-1 text-sm font-medium text-slate-100">
                      {project.name}
                    </div>
                    <p className="text-xs text-slate-500">
                      {project.repoPath}
                    </p>
                  </div>
                </div>
              </TableCell>
              <TableCell>
                <div className="flex flex-wrap gap-1">
                  {project.stack.map((tech) => (
                    <Badge key={tech} variant="secondary">
                      {tech}
                    </Badge>
                  ))}
                </div>
              </TableCell>
              <TableCell>
                <div className="inline-flex items-center gap-1 text-xs text-slate-300">
                  <GitBranch className="h-3.5 w-3.5 text-slate-500" />
                  <span>{project.branch}</span>
                </div>
              </TableCell>
              <TableCell>
                <CiStatus hasCi={project.hasCi} />
              </TableCell>
              <TableCell className="text-xs text-slate-400">
                {project.lastActivity}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1.5">
                  <Button
                    size="sm"
                    className="text-xs"
                    onClick={() => handlePrimaryAction(project)}
                  >
                    {project.hasCi ? (
                      <>
                        <Layers className="mr-1.5 h-3.5 w-3.5" />
                        View Pipeline
                      </>
                    ) : (
                      <>
                        <Play className="mr-1.5 h-3.5 w-3.5" />
                        Generate Pipeline
                      </>
                    )}
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-slate-700 bg-slate-950 text-slate-300 hover:bg-slate-900">
                      <MoreVertical className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem
                        onClick={() => handleAnalyze(project)}
                      >
                        Analyze Repository
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => handleViewBranches(project)}
                      >
                        View Branches
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => handleSettings(project)}
                      >
                        Project Settings
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export { projectsMock };


