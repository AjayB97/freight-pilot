import { Lightbulb, CheckCircle2 } from "lucide-react";

export function Recommendations({ items }: { items: string[] }) {
  if (!items.length) {
    return (
      <div className="flex items-start gap-3 rounded-xl border border-emerald-400/35 bg-gradient-to-r from-emerald-500/16 via-card/90 to-emerald-400/10 p-5 text-sm shadow-lg shadow-black/20">
        <CheckCircle2 className="h-5 w-5 mt-0.5 text-success shrink-0" />
        <div>
          <div className="font-medium">No issues flagged.</div>
          <div className="text-muted-foreground">
            Conversion, margin and sentiment are all within healthy ranges for this window.
          </div>
        </div>
      </div>
    );
  }
  return (
    <ul className="space-y-3">
      {items.map((rec, i) => (
        <li
          key={i}
          className="flex items-start gap-3 rounded-xl border border-amber-400/35 bg-gradient-to-r from-amber-500/16 via-card/90 to-orange-400/10 p-4 text-sm shadow-lg shadow-black/20"
        >
          <Lightbulb className="h-5 w-5 mt-0.5 text-warning-foreground shrink-0" />
          <div>{rec}</div>
        </li>
      ))}
    </ul>
  );
}
