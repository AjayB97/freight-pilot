import Link from "next/link";
import { Call } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { formatDateTime, formatUSD } from "@/lib/utils";

const OUTCOME_LABEL: Record<string, string> = {
  booked: "Booked",
  no_agreement: "No agreement",
  not_eligible: "Not eligible",
  no_matching_load: "No matching load",
  carrier_declined: "Carrier declined",
  escalated: "Escalated",
  abandoned: "Abandoned",
};

function outcomeVariant(o: string): "success" | "warning" | "destructive" | "muted" | "default" {
  switch (o) {
    case "booked":
      return "success";
    case "escalated":
      return "default";
    case "no_matching_load":
      return "warning";
    case "no_agreement":
    case "carrier_declined":
      return "destructive";
    default:
      return "muted";
  }
}

function sentimentVariant(s: string | null): "success" | "destructive" | "muted" {
  if (!s) return "muted";
  if (s === "positive") return "success";
  if (s === "negative" || s === "frustrated") return "destructive";
  return "muted";
}

export function CallRow({ call }: { call: Call }) {
  return (
    <Link
      href={`/calls/${call.id}`}
      className="block rounded-xl border bg-card p-4 shadow-sm transition hover:border-foreground/20"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 text-sm">
            <Badge variant={outcomeVariant(call.outcome)}>
              {OUTCOME_LABEL[call.outcome] ?? call.outcome}
            </Badge>
            {call.sentiment ? (
              <Badge variant={sentimentVariant(call.sentiment)}>{call.sentiment}</Badge>
            ) : null}
            {call.load_id ? (
              <span className="text-xs text-muted-foreground">· {call.load_id}</span>
            ) : null}
          </div>
          <div className="mt-1 text-sm font-medium truncate">
            {call.carrier_name ?? "Unknown carrier"}
            {call.mc_number ? (
              <span className="ml-2 text-muted-foreground font-normal">MC {call.mc_number}</span>
            ) : null}
          </div>
          {call.summary ? (
            <div className="mt-1 text-sm text-muted-foreground line-clamp-2">{call.summary}</div>
          ) : null}
        </div>
        <div className="text-right shrink-0">
          <div className="text-sm font-medium tabular-nums">
            {formatUSD(call.final_rate ?? call.loadboard_rate)}
          </div>
          {call.loadboard_rate && call.final_rate && call.final_rate !== call.loadboard_rate ? (
            <div className="text-xs text-muted-foreground tabular-nums">
              vs board {formatUSD(call.loadboard_rate)}
            </div>
          ) : null}
          <div className="mt-1 text-xs text-muted-foreground">
            {formatDateTime(call.created_at)}
          </div>
          {call.rounds ? (
            <div className="text-xs text-muted-foreground">{call.rounds} rounds</div>
          ) : null}
        </div>
      </div>
    </Link>
  );
}
