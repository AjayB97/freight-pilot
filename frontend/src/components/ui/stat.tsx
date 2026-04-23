import * as React from "react";
import { cn } from "@/lib/utils";

export function Stat({
  label,
  value,
  sublabel,
  tone = "default",
  hint,
  className,
  icon: Icon,
}: {
  label: string;
  value: React.ReactNode;
  sublabel?: React.ReactNode;
  tone?: "default" | "success" | "warning" | "destructive";
  hint?: string;
  className?: string;
  icon?: React.ComponentType<{ className?: string }>;
}) {
  const toneCls = {
    default: "text-foreground",
    success: "text-success",
    warning: "text-warning",
    destructive: "text-destructive",
  }[tone];

  return (
    <div className={cn("rounded-2xl border bg-card p-5 shadow-lg shadow-black/20", className)}>
      <div className="flex items-center justify-between gap-3">
        <div className="text-xs font-semibold text-muted-foreground tracking-[0.12em] uppercase">
          {label}
        </div>
        {Icon ? <Icon className="h-4 w-4 text-muted-foreground" /> : null}
      </div>
      <div className={cn("mt-1 text-3xl font-semibold leading-tight", toneCls)}>{value}</div>
      {sublabel ? <div className="mt-1 text-xs text-foreground/85">{sublabel}</div> : null}
      {hint ? <div className="mt-2 text-xs text-muted-foreground italic">{hint}</div> : null}
    </div>
  );
}
