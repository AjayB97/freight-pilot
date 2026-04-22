import { api } from "@/lib/api";
import { CallRow } from "@/components/call-row";

export const dynamic = "force-dynamic";

export default async function CallsPage() {
  const calls = await api.recentCalls(100);
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Calls</h1>
        <p className="text-sm text-muted-foreground">
          Full log of inbound carrier calls handled by the agent.
        </p>
      </div>
      {calls.length ? (
        <div className="grid gap-3 md:grid-cols-2">
          {calls.map((c) => (
            <CallRow key={c.id} call={c} />
          ))}
        </div>
      ) : (
        <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground">
          No calls yet.
        </div>
      )}
    </div>
  );
}
