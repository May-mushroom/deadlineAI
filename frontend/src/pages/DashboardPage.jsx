import StatCard from "../components/StatCard";

const STATS = ["Total tasks added", "Total completed", "Total late", "Average delay"];

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {STATS.map((label) => (
          <StatCard key={label} label={label}>
            —
          </StatCard>
        ))}
      </div>
      <StatCard label="Insights" valueClass="text-sm text-muted">
        Insights will appear here once AI processing is connected.
      </StatCard>
    </div>
  );
}
