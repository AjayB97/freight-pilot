import { FunnelPoint } from "@/lib/api";

export function Funnel({ points }: { points: FunnelPoint[] }) {
  const max = Math.max(...points.map((p) => p.count), 1);
  return (
    <div className="space-y-3">
      {points.map((p, i) => {
        const width = Math.max((p.count / max) * 100, 4);
        const previous = i > 0 ? points[i - 1].count : null;
        const dropOff =
          previous && previous > 0 ? 1 - p.count / previous : null;
        return (
          <div key={p.stage} className="">
            <div className="flex items-baseline justify-between mb-1.5">
              <div className="text-sm font-medium">{p.stage}</div>
              <div className="text-sm tabular-nums text-muted-foreground">
                {p.count.toLocaleString()}
                {dropOff !== null && dropOff > 0 ? (
                  <span className="ml-2 text-xs text-destructive">
                    −{(dropOff * 100).toFixed(0)}%
                  </span>
                ) : null}
              </div>
            </div>
            <div className="h-8 w-full rounded-md bg-muted overflow-hidden">
              <div
                className="h-full rounded-md bg-primary/85 transition-[width] duration-300"
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
