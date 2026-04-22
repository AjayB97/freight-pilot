import { OutcomeBreakdown } from "@/lib/api";
import { formatUSD } from "@/lib/utils";

const OUTCOME_LABEL: Record<string, string> = {
  booked: "Booked",
  no_agreement: "No agreement",
  not_eligible: "Not eligible",
  no_matching_load: "No matching load",
  carrier_declined: "Carrier declined",
  escalated: "Escalated to rep",
  abandoned: "Abandoned",
};

const OUTCOME_TONE: Record<string, string> = {
  booked: "bg-success",
  no_agreement: "bg-destructive/80",
  not_eligible: "bg-muted-foreground/60",
  no_matching_load: "bg-warning",
  carrier_declined: "bg-destructive/60",
  escalated: "bg-primary",
  abandoned: "bg-muted-foreground/40",
};

export function OutcomesChart({ outcomes }: { outcomes: OutcomeBreakdown[] }) {
  const total = outcomes.reduce((s, o) => s + o.count, 0);
  if (!total) {
    return <div className="text-sm text-muted-foreground">No calls yet.</div>;
  }
  return (
    <div className="space-y-4">
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-muted">
        {outcomes.map((o) => (
          <div
            key={o.outcome}
            className={OUTCOME_TONE[o.outcome] ?? "bg-muted-foreground/40"}
            style={{ width: `${(o.count / total) * 100}%` }}
            title={`${OUTCOME_LABEL[o.outcome] ?? o.outcome}: ${o.count}`}
          />
        ))}
      </div>
      <ul className="space-y-2">
        {outcomes.map((o) => (
          <li key={o.outcome} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span
                className={`inline-block h-2.5 w-2.5 rounded-full ${OUTCOME_TONE[o.outcome] ?? "bg-muted-foreground/40"}`}
              />
              <span>{OUTCOME_LABEL[o.outcome] ?? o.outcome}</span>
            </div>
            <div className="tabular-nums text-muted-foreground">
              {o.count} · {((o.count / total) * 100).toFixed(0)}%
              {o.revenue ? <span className="ml-2">{formatUSD(o.revenue)}</span> : null}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
