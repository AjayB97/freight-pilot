import { FunnelPoint } from "@/lib/api";

export function Funnel({ points }: { points: FunnelPoint[] }) {
  const max = Math.max(...points.map((p) => p.count), 1);
  return (
    <div className="space-y-3">
      {points.map((p, i) => {
        const previous = i > 0 ? points[i - 1].count : null;
        const dropCount = previous !== null ? Math.max(previous - p.count, 0) : 0;
        const dropOff = previous && previous > 0 ? dropCount / previous : null;
        const retainedWidth = (p.count / max) * 100;
        const previousWidth = previous !== null ? (previous / max) * 100 : retainedWidth;
        const dropWidth = Math.max(previousWidth - retainedWidth, 0);
        const retainedMinWidthClass = p.count > 0 ? "min-w-[3px]" : "";
        const dropMinWidthClass = dropCount > 0 ? "min-w-[3px]" : "";
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
            <div className="h-8 w-full rounded-md bg-muted overflow-hidden relative">
              <div
                className={`absolute inset-y-0 left-0 bg-primary/85 transition-[width] duration-300 ${
                  i === 0 ? "rounded-md" : "rounded-l-md"
                } ${retainedMinWidthClass}`}
                style={{ width: `${retainedWidth}%` }}
              />
              {i > 0 && dropWidth > 0 ? (
                <div
                  className={`absolute inset-y-0 rounded-r-md bg-destructive/70 transition-[width,left] duration-300 ${dropMinWidthClass}`}
                  style={{ left: `${retainedWidth}%`, width: `${dropWidth}%` }}
                />
              ) : null}
            </div>
            {i > 0 && dropCount > 0 ? (
              <div className="mt-1 text-xs text-destructive/90">
                Dropped {dropCount.toLocaleString()} from previous stage
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
