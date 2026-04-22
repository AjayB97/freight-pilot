import { SentimentBreakdown } from "@/lib/api";

const TONE: Record<string, string> = {
  positive: "bg-success",
  neutral: "bg-muted-foreground/50",
  negative: "bg-destructive/70",
  frustrated: "bg-destructive",
  unknown: "bg-muted-foreground/30",
};

const LABEL: Record<string, string> = {
  positive: "Positive",
  neutral: "Neutral",
  negative: "Negative",
  frustrated: "Frustrated",
  unknown: "Unknown",
};

export function SentimentBar({ sentiment }: { sentiment: SentimentBreakdown[] }) {
  const total = sentiment.reduce((s, x) => s + x.count, 0);
  if (!total) {
    return <div className="text-sm text-muted-foreground">No sentiment captured yet.</div>;
  }
  return (
    <div className="space-y-3">
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-muted">
        {sentiment.map((s) => (
          <div
            key={s.sentiment}
            className={TONE[s.sentiment] ?? TONE.unknown}
            style={{ width: `${(s.count / total) * 100}%` }}
            title={`${LABEL[s.sentiment] ?? s.sentiment}: ${s.count}`}
          />
        ))}
      </div>
      <ul className="grid grid-cols-2 gap-2 text-sm">
        {sentiment.map((s) => (
          <li key={s.sentiment} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span
                className={`inline-block h-2.5 w-2.5 rounded-full ${TONE[s.sentiment] ?? TONE.unknown}`}
              />
              {LABEL[s.sentiment] ?? s.sentiment}
            </div>
            <div className="tabular-nums text-muted-foreground">
              {s.count} · {((s.count / total) * 100).toFixed(0)}%
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
