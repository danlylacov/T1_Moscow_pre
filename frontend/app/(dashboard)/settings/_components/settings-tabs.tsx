"use client";

import { useState } from "react";
import {
  Settings,
  Users,
  Zap,
  Shield,
  Globe,
  Plus,
  Trash2,
} from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";

const MOCK_BANNED = ["rm -rf /", "curl | bash"];

export function SettingsTabs() {
  const [tab, setTab] = useState<"integrations" | "org">("integrations");
  const [enforceOrgMode, setEnforceOrgMode] = useState(true);
  const [bannedCommands, setBannedCommands] = useState<string[]>(MOCK_BANNED);
  const [newCommand, setNewCommand] = useState("");
  const [runnerImagePrefix, setRunnerImagePrefix] = useState("registry.company.com/ci/");
  const [connectOpen, setConnectOpen] = useState(false);

  const { showToast } = useToast();

  const isAdmin = true; // simulate admin; in real app this would come from user context

  const handleAddCommand = () => {
    if (!newCommand.trim()) return;
    setBannedCommands((prev) => [...prev, newCommand.trim()]);
    setNewCommand("");
  };

  const handleRemoveCommand = (cmd: string) => {
    setBannedCommands((prev) => prev.filter((c) => c !== cmd));
  };

  const handleSaveOrgSettings = () => {
    showToast({
      variant: "success",
      title: "Organization settings saved",
      description: "Global policies and templates have been updated.",
    });
  };

  const handleConnectIntegration = (event: React.FormEvent) => {
    event.preventDefault();
    setConnectOpen(false);
    showToast({
      variant: "success",
      title: "Integration connected",
      description: "We successfully connected to your Git provider.",
    });
  };

  const handleRevoke = (name: string) => {
    showToast({
      variant: "destructive",
      title: `Access revoked for ${name}`,
      description: "You can reconnect this integration at any time.",
    });
  };

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900">
            <Settings className="h-5 w-5 text-sky-400" />
          </div>
          <div className="space-y-0.5">
            <h1 className="text-sm font-semibold text-slate-100">
              Settings
            </h1>
            <p className="text-xs text-slate-400">
              Manage integrations, organization-wide policies, and templates.
            </p>
          </div>
        </div>
        <Badge variant="secondary" className="text-[10px]">
          Workspace: self-deploy-demo
        </Badge>
      </div>

      <Tabs
        defaultValue="integrations"
        value={tab}
        onValueChange={(value) => setTab(value as "integrations" | "org")}
        className="space-y-4"
      >
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <TabsList>
            <TabsTrigger value="integrations">Integrations</TabsTrigger>
            {isAdmin && (
              <TabsTrigger value="org">Organization settings</TabsTrigger>
            )}
          </TabsList>
          <p className="text-[11px] text-slate-500">
            Settings are applied instantly across all new pipelines.
          </p>
        </div>

        <TabsContent value="integrations">
          <Card className="border-slate-800 bg-slate-950/90">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900">
                  <Zap className="h-4 w-4 text-amber-300" />
                </div>
                <div>
                  <CardTitle className="text-sm">
                    Git integrations
                  </CardTitle>
                  <CardDescription className="text-[11px] text-slate-400">
                    Connect GitHub, GitLab and other providers to generate and
                    validate pipelines.
                  </CardDescription>
                </div>
              </div>
              <Dialog open={connectOpen} onOpenChange={setConnectOpen}>
                <DialogTrigger asChild>
                  <Button className="h-8 gap-1.5 px-3 text-xs">
                    <Plus className="h-4 w-4" />
                    Connect new integration
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Connect new integration</DialogTitle>
                    <DialogDescription>
                      Add a new Git provider or self-hosted GitLab instance.
                    </DialogDescription>
                  </DialogHeader>
                  <form className="space-y-3 text-xs" onSubmit={handleConnectIntegration}>
                    <div className="space-y-1.5">
                      <label
                        htmlFor="provider"
                        className="text-[11px] font-medium text-slate-300"
                      >
                        Provider
                      </label>
                      <Input
                        id="provider"
                        placeholder="GitHub, GitLab, Bitbucket…"
                        className="h-8 text-xs"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label
                        htmlFor="instance-url"
                        className="text-[11px] font-medium text-slate-300"
                      >
                        Instance URL (optional)
                      </label>
                      <Input
                        id="instance-url"
                        type="url"
                        placeholder="https://gitlab.company.com"
                        className="h-8 text-xs"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label
                        htmlFor="token"
                        className="text-[11px] font-medium text-slate-300"
                      >
                        Personal access token
                      </label>
                      <Input
                        id="token"
                        type="password"
                        placeholder="••••••••"
                        className="h-8 text-xs"
                      />
                      <p className="text-[11px] text-slate-500">
                        Tokens are encrypted and stored securely. You can revoke
                        access at any time.
                      </p>
                    </div>
                    <div className="mt-3 flex items-center justify-end gap-2">
                      <Button
                        type="button"
                        variant="secondary"
                        className="h-8 px-3 text-xs"
                        onClick={() => setConnectOpen(false)}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        className="h-8 px-3 text-xs"
                      >
                        Connect
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </CardHeader>

            <CardContent className="space-y-4 pt-0">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-950/80">
                    <TableHead className="text-[11px]">Provider</TableHead>
                    <TableHead className="text-[11px]">Details</TableHead>
                    <TableHead className="text-[11px]">Status</TableHead>
                    <TableHead className="text-[11px] text-right">
                      Actions
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell className="text-xs">
                      <div className="flex items-center gap-2">
                        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-slate-900">
                          <span className="text-[11px] font-semibold text-slate-100">
                            GH
                          </span>
                        </div>
                        <div>
                          <div className="text-xs font-medium text-slate-100">
                            GitHub (SaaS)
                          </div>
                          <div className="text-[11px] text-slate-500">
                            User: alex@corp
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-[11px] text-slate-400">
                      Scopes: repo, read:org
                    </TableCell>
                    <TableCell className="text-[11px]">
                      <Badge
                        variant="success"
                        className="bg-emerald-500/10 text-[10px] text-emerald-300"
                      >
                        Connected
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right text-[11px]">
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        className="border-red-500/50 text-red-300 hover:bg-red-500/10"
                        onClick={() => handleRevoke("GitHub")}
                      >
                        <Trash2 className="mr-1 h-3.5 w-3.5" />
                        Revoke access
                      </Button>
                    </TableCell>
                  </TableRow>

                  <TableRow>
                    <TableCell className="text-xs">
                      <div className="flex items-center gap-2">
                        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-slate-900">
                          <Globe className="h-4 w-4 text-amber-300" />
                        </div>
                        <div>
                          <div className="text-xs font-medium text-slate-100">
                            GitLab (Self-hosted)
                          </div>
                          <div className="text-[11px] text-slate-500">
                            https://git.company.com
                          </div>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-[11px] text-slate-400">
                      Managed by org policy • CI token
                    </TableCell>
                    <TableCell className="text-[11px]">
                      <Badge
                        variant="secondary"
                        className="bg-emerald-500/10 text-[10px] text-emerald-300"
                      >
                        Active
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right text-[11px]">
                      <div className="flex justify-end gap-2">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="border-slate-700 text-slate-200 hover:bg-slate-900"
                        >
                          Edit token
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="border-red-500/50 text-red-300 hover:bg-red-500/10"
                          onClick={() => handleRevoke("GitLab")}
                        >
                          <Trash2 className="mr-1 h-3.5 w-3.5" />
                          Disconnect
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>

              <Alert className="text-xs">
                <AlertTitle className="flex items-center gap-2 text-xs">
                  <Shield className="h-4 w-4 text-emerald-300" />
                  Least-privilege by default
                </AlertTitle>
                <AlertDescription>
                  We recommend using tokens scoped only to CI and read-only
                  permissions where possible.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="org">
          <div className="space-y-4">
            {/* Global policies */}
            <Card className="border-slate-800 bg-slate-950/90">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900">
                    <Shield className="h-4 w-4 text-emerald-300" />
                  </div>
                  <div>
                    <CardTitle className="text-sm">
                      Global policies
                    </CardTitle>
                    <CardDescription className="text-[11px] text-slate-400">
                      Enforce security rules and image standards across all
                      pipelines in this organization.
                    </CardDescription>
                  </div>
                </div>
                <Badge variant="secondary" className="text-[10px]">
                  Admin only
                </Badge>
              </CardHeader>
              <CardContent className="space-y-4 pt-0 text-xs">
                <div className="flex items-center justify-between gap-3 rounded-lg border border-slate-800 bg-slate-950/80 px-3 py-2">
                  <div>
                    <p className="text-xs font-medium text-slate-100">
                      Enforce organization mode
                    </p>
                    <p className="text-[11px] text-slate-500">
                      Require pipelines to use only approved images and
                      disallow risky shell commands.
                    </p>
                  </div>
                  <Switch
                    checked={enforceOrgMode}
                    onCheckedChange={setEnforceOrgMode}
                  />
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-medium text-slate-100">
                    Banned commands
                  </p>
                  <p className="text-[11px] text-slate-500">
                    These commands will cause validation to fail if detected in
                    any job.
                  </p>
                  <div className="space-y-2">
                    {bannedCommands.map((cmd) => (
                      <div
                        key={cmd}
                        className="flex items-center justify-between rounded-md border border-red-500/40 bg-red-500/5 px-3 py-1.5"
                      >
                        <span className="font-mono text-[11px] text-red-100">
                          {cmd}
                        </span>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="border-red-500/60 text-[10px] text-red-200 hover:bg-red-500/10"
                          onClick={() => handleRemoveCommand(cmd)}
                        >
                          <Trash2 className="mr-1 h-3 w-3" />
                          Remove
                        </Button>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2 pt-1">
                    <Input
                      value={newCommand}
                      onChange={(e) => setNewCommand(e.target.value)}
                      placeholder="e.g. docker run --privileged"
                      className="h-8 text-[11px]"
                    />
                    <Button
                      type="button"
                      size="sm"
                      className="h-8 gap-1.5 px-3 text-[11px]"
                      onClick={handleAddCommand}
                    >
                      <Plus className="h-3.5 w-3.5" />
                      Add
                    </Button>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-medium text-slate-100">
                    Standardized runner images
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Pipelines should use images that start with this prefix.
                    Leave blank to disable this rule.
                  </p>
                  <Input
                    value={runnerImagePrefix}
                    onChange={(e) => setRunnerImagePrefix(e.target.value)}
                    placeholder="registry.company.com/ci/"
                    className="h-8 text-[11px] font-mono"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Global templates */}
            <Card className="border-slate-800 bg-slate-950/90">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900">
                    <Zap className="h-4 w-4 text-sky-400" />
                  </div>
                  <div>
                    <CardTitle className="text-sm">
                      Global templates
                    </CardTitle>
                    <CardDescription className="text-[11px] text-slate-400">
                      Recommended CI/CD blueprints defined at the organization
                      level.
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 pt-0 text-xs">
                <div className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-950/80 px-3 py-2">
                  <div className="space-y-0.5">
                    <p className="text-xs font-medium text-slate-100">
                      Java-Spring-Base
                    </p>
                    <p className="text-[11px] text-slate-500">
                      Multi-stage Docker build with unit tests and coverage
                      reports.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="success"
                      className="bg-emerald-500/10 text-[10px] text-emerald-300"
                    >
                      Active
                    </Badge>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="h-7 px-3 text-[11px]"
                    >
                      View YAML
                    </Button>
                  </div>
                </div>
                <div className="flex items-center justify-between rounded-md border border-slate-800 bg-slate-950/80 px-3 py-2">
                  <div className="space-y-0.5">
                    <p className="text-xs font-medium text-slate-100">
                      Node-Next-Docker
                    </p>
                    <p className="text-[11px] text-slate-500">
                      Node.js pipeline with lint, tests, and Docker image
                      publishing.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="secondary"
                      className="text-[10px] text-slate-200"
                    >
                      Active
                    </Badge>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="h-7 px-3 text-[11px]"
                    >
                      View YAML
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Users & roles (optional) */}
            <Card className="border-slate-800 bg-slate-950/90">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <div className="flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-900">
                    <Users className="h-4 w-4 text-slate-200" />
                  </div>
                  <div>
                    <CardTitle className="text-sm">
                      Users &amp; roles
                    </CardTitle>
                    <CardDescription className="text-[11px] text-slate-400">
                      Preview who can manage pipelines and organization
                      settings.
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 pt-0 text-xs">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-950/80">
                      <TableHead className="text-[11px]">User</TableHead>
                      <TableHead className="text-[11px]">Role</TableHead>
                      <TableHead className="text-[11px]">Last activity</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell className="text-xs">
                        <div className="space-y-0.5">
                          <div className="text-xs font-medium text-slate-100">
                            Alex
                          </div>
                          <div className="text-[11px] text-slate-500">
                            alex@company.com
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-[11px]">
                        <Badge
                          variant="secondary"
                          className="text-[10px] text-slate-100"
                        >
                          Admin
                        </Badge>
                      </TableCell>
                      <TableCell className="text-[11px] text-slate-400">
                        5 minutes ago
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell className="text-xs">
                        <div className="space-y-0.5">
                          <div className="text-xs font-medium text-slate-100">
                            Jane
                          </div>
                          <div className="text-[11px] text-slate-500">
                            jane@company.com
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-[11px]">
                        <Badge
                          variant="secondary"
                          className="text-[10px] text-slate-100"
                        >
                          Member
                        </Badge>
                      </TableCell>
                      <TableCell className="text-[11px] text-slate-400">
                        Yesterday
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </Card>

            <div className="flex items-center justify-end">
              <Button
                type="button"
                className="h-8 gap-1.5 px-4 text-xs"
                onClick={handleSaveOrgSettings}
              >
                Save changes
              </Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}


