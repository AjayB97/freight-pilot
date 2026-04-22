import { Lightbulb, CheckCircle2 } from "lucide-react";

export function Recommendations({ items }: { items: string[] }) {
  if (!items.length) {
    return (
      <div className="flex items-start gap-3 rounded-xl border bg-card p-5 text-sm">
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
          className="flex items-start gap-3 rounded-xl border bg-card p-4 text-sm shadow-sm"
        >
          <Lightbulb className="h-5 w-5 mt-0.5 text-warning-foreground shrink-0" />
          <div>{rec}</div>
        </li>
      ))}
    </ul>
  );
}
