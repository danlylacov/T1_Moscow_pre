"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Github, Server, ShieldCheck } from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";

export function UserAuthForm() {
  const router = useRouter();
  const [tab, setTab] = useState<"cloud" | "selfhosted">("cloud");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const handleCloudSignIn = () => {
    setIsSubmitting(true);
    setStatus("Signing you in…");
    setTimeout(() => {
      setIsSubmitting(false);
      setStatus(null);
      router.push("/dashboard");
    }, 1000);
  };

  const handleEmailSignIn = (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setStatus("Checking credentials…");
    setTimeout(() => {
      setIsSubmitting(false);
      setStatus(null);
      router.push("/dashboard");
    }, 1000);
  };

  const handleVerifySelfHosted = (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setStatus("Checking connection to your GitLab instance…");
    setTimeout(() => {
      setIsSubmitting(false);
      setStatus(null);
      router.push("/dashboard");
    }, 1200);
  };

  return (
    <Card className="border-slate-800 bg-slate-950/80 shadow-lg">
      <CardHeader className="space-y-1 text-center">
        <CardTitle className="text-base">Welcome to Self-Deploy</CardTitle>
        <CardDescription className="text-xs text-slate-400">
          Выберите способ входа: облачные аккаунты или корпоративный GitLab.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs
          defaultValue="cloud"
          value={tab}
          onValueChange={(value) => setTab(value as "cloud" | "selfhosted")}
        >
          <TabsList className="w-full justify-between">
            <TabsTrigger value="cloud" className="flex-1">
              Cloud (SaaS)
            </TabsTrigger>
            <TabsTrigger value="selfhosted" className="flex-1">
              Self-hosted
            </TabsTrigger>
          </TabsList>

          <TabsContent value="cloud" className="mt-4 space-y-4">
            <div className="space-y-2">
              <Button
                type="button"
                className="flex w-full items-center justify-center gap-2 bg-slate-900 text-slate-50 hover:bg-slate-800"
                onClick={handleCloudSignIn}
                disabled={isSubmitting}
              >
                <Github className="h-4 w-4" />
                Continue with GitHub
              </Button>
              <Button
                type="button"
                variant="outline"
                className="flex w-full items-center justify-center gap-2 border-amber-500/50 bg-slate-950 text-amber-300 hover:bg-slate-900"
                onClick={handleCloudSignIn}
                disabled={isSubmitting}
              >
                <Server className="h-4 w-4" />
                Continue with GitLab.com
              </Button>
            </div>

            <div className="flex items-center gap-3 text-[11px] text-slate-500">
              <Separator className="flex-1" />
              <span>Or continue with email</span>
              <Separator className="flex-1" />
            </div>

            <form className="space-y-3" onSubmit={handleEmailSignIn}>
              <div className="space-y-1.5">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  placeholder="you@company.com"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  placeholder="••••••••"
                />
              </div>
              <Button
                type="submit"
                className="mt-1 w-full"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Signing in…" : "Sign in"}
              </Button>
            </form>
          </TabsContent>

          <TabsContent value="selfhosted" className="mt-4 space-y-4">
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <ShieldCheck className="h-4 w-4 text-emerald-300" />
              <span>Connect Enterprise Instance</span>
            </div>
            <form className="space-y-3" onSubmit={handleVerifySelfHosted}>
              <div className="space-y-1.5">
                <Label htmlFor="gitlab-url">GitLab URL</Label>
                <Input
                  id="gitlab-url"
                  type="url"
                  required
                  placeholder="https://gitlab.company.com"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="gitlab-token">Personal Access Token</Label>
                <Input
                  id="gitlab-token"
                  type="password"
                  required
                  placeholder="••••••••"
                />
                <p className="text-[11px] text-slate-500">
                  Tokens are encrypted and stored securely. Можно ограничить
                  права только CI/CD-операциями.
                </p>
              </div>
              <Button
                type="submit"
                className="mt-1 w-full"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Verifying…" : "Verify & connect"}
              </Button>
            </form>
          </TabsContent>
        </Tabs>

        {status && (
          <div className="rounded-md border border-slate-800 bg-slate-900/80 px-3 py-2 text-[11px] text-slate-300">
            {status}
          </div>
        )}

        <p className="mt-2 text-center text-[11px] text-slate-500">
          Don&apos;t have an account?{" "}
          <a
            href="/register"
            className="font-medium text-sky-400 hover:underline"
          >
            Sign up
          </a>
        </p>
      </CardContent>
    </Card>
  );
}


