import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatUSD } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function LoadsPage() {
  const loads = await api.loads();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Loads</h1>
        <p className="text-sm text-muted-foreground">
          Every load visible to the agent. Status flips to &quot;booked&quot; when a call closes.
        </p>
      </div>
      <div className="overflow-x-auto rounded-xl border bg-card shadow-sm">
        <table className="w-full text-sm">
          <thead className="text-xs uppercase text-muted-foreground bg-muted/50">
            <tr>
              <th className="text-left font-medium px-4 py-3">Load</th>
              <th className="text-left font-medium px-4 py-3">Lane</th>
              <th className="text-left font-medium px-4 py-3">Equipment</th>
              <th className="text-left font-medium px-4 py-3">Pickup</th>
              <th className="text-right font-medium px-4 py-3">Miles</th>
              <th className="text-right font-medium px-4 py-3">Rate</th>
              <th className="text-left font-medium px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {loads.map((l) => (
              <tr key={l.load_id} className="border-t">
                <td className="px-4 py-3 font-medium">{l.load_id}</td>
                <td className="px-4 py-3">
                  {l.origin} <span className="text-muted-foreground">→</span> {l.destination}
                </td>
                <td className="px-4 py-3 text-muted-foreground">{l.equipment_type}</td>
                <td className="px-4 py-3 text-muted-foreground">
                  {formatDate(l.pickup_datetime)}
                </td>
                <td className="px-4 py-3 text-right tabular-nums text-muted-foreground">
                  {l.miles ? l.miles.toLocaleString() : "—"}
                </td>
                <td className="px-4 py-3 text-right tabular-nums font-medium">
                  {formatUSD(l.loadboard_rate)}
                </td>
                <td className="px-4 py-3">
                  <Badge variant={l.status === "booked" ? "success" : "muted"}>{l.status}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
