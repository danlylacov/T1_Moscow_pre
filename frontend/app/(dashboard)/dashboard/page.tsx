import { StatsOverview } from "./_components/stats-overview";
import { IntegrationsList } from "./_components/integrations-list";
import { AiInsights } from "./_components/ai-insights";
import { RecentActivity } from "./_components/recent-activity";

export default function Page() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-50">
            Dashboard
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Overview of your pipelines, integrations, and AI insights.
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <StatsOverview />
        </div>
        <div className="space-y-6">
          <IntegrationsList />
        </div>
      </div>

      <AiInsights />

      <RecentActivity />
    </div>
  );
}



