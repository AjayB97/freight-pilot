import { LanePerformance } from "@/lib/api";
import { formatPct, formatUSD } from "@/lib/utils";

export function LaneTable({ lanes }: { lanes: LanePerformance[] }) {
  if (!lanes.length) {
    return (
      <div className="text-sm text-muted-foreground">
        No lane data yet. Lanes populate after the first few calls.
      </div>
    );
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="text-xs uppercase text-muted-foreground">
          <tr>
            <th className="text-left font-medium py-2 pr-4">Lane</th>
            <th className="text-left font-medium py-2 pr-4">Equipment</th>
            <th className="text-right font-medium py-2 pr-4">Calls</th>
            <th className="text-right font-medium py-2 pr-4">Booked</th>
            <th className="text-right font-medium py-2 pr-4">Conv.</th>
            <th className="text-right font-medium py-2 pr-4">Avg rate</th>
            <th className="text-right font-medium py-2">Margin</th>
          </tr>
        </thead>
        <tbody>
          {lanes.map((l, i) => (
            <tr key={i} className="border-t">
              <td className="py-2.5 pr-4">
                <div className="font-medium">
                  {l.origin} <span className="text-muted-foreground">→</span> {l.destination}
                </div>
              </td>
              <td className="py-2.5 pr-4 text-muted-foreground">{l.equipment_type}</td>
              <td className="py-2.5 pr-4 text-right tabular-nums">{l.calls}</td>
              <td className="py-2.5 pr-4 text-right tabular-nums">{l.booked}</td>
              <td className="py-2.5 pr-4 text-right tabular-nums">
                {formatPct(l.conversion, 0)}
              </td>
              <td className="py-2.5 pr-4 text-right tabular-nums">
                {formatUSD(l.avg_final_rate)}
              </td>
              <td
                className={
                  "py-2.5 text-right tabular-nums " +
                  (l.avg_margin_pct && l.avg_margin_pct < 0
                    ? "text-destructive"
                    : l.avg_margin_pct && l.avg_margin_pct > 0
                      ? "text-success"
                      : "")
                }
              >
                {l.avg_margin_pct !== null && l.avg_margin_pct !== undefined
                  ? `${l.avg_margin_pct > 0 ? "+" : ""}${(l.avg_margin_pct * 100).toFixed(1)}%`
                  : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
