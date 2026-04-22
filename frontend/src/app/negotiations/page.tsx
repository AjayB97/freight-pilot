import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { formatDateTime, formatUSD } from "@/lib/utils";

export const dynamic = "force-dynamic";

function toneFor(resp: string): "success" | "warning" | "destructive" {
  if (resp === "accept") return "success";
  if (resp === "reject") return "destructive";
  return "warning";
}

export default async function NegotiationsPage() {
  const rows = await api.recentNegotiations(100);
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Negotiations</h1>
        <p className="text-sm text-muted-foreground">
          Every round of every negotiation. This is the audit trail — each decision is
          deterministic given the load and offer.
        </p>
      </div>
      {rows.length === 0 ? (
        <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground">
          No negotiations yet.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border bg-card shadow-sm">
          <table className="w-full text-sm">
            <thead className="text-xs uppercase text-muted-foreground bg-muted/50">
              <tr>
                <th className="text-left font-medium px-4 py-3">When</th>
                <th className="text-left font-medium px-4 py-3">Load</th>
                <th className="text-left font-medium px-4 py-3">MC</th>
                <th className="text-right font-medium px-4 py-3">Round</th>
                <th className="text-right font-medium px-4 py-3">Board</th>
                <th className="text-right font-medium px-4 py-3">Offer</th>
                <th className="text-left font-medium px-4 py-3">Response</th>
                <th className="text-right font-medium px-4 py-3">Counter</th>
                <th className="text-left font-medium px-4 py-3">Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-t">
                  <td className="px-4 py-3 text-muted-foreground whitespace-nowrap">
                    {formatDateTime(r.created_at)}
                  </td>
                  <td className="px-4 py-3 font-mono">{r.load_id ?? "—"}</td>
                  <td className="px-4 py-3 text-muted-foreground">{r.mc_number ?? "—"}</td>
                  <td className="px-4 py-3 text-right tabular-nums">{r.round_number}</td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {formatUSD(r.loadboard_rate)}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {formatUSD(r.carrier_offer)}
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={toneFor(r.broker_response)}>{r.broker_response}</Badge>
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {formatUSD(r.broker_counter)}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground text-xs max-w-md">
                    {r.reasoning}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
