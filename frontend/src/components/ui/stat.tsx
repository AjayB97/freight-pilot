import * as React from "react";
import { cn } from "@/lib/utils";

export function Stat({
  label,
  value,
  sublabel,
  tone = "default",
  hint,
  className,
}: {
  label: string;
  value: React.ReactNode;
  sublabel?: React.ReactNode;
  tone?: "default" | "success" | "warning" | "destructive";
  hint?: string;
  className?: string;
}) {
  const toneCls = {
    default: "text-foreground",
    success: "text-success",
    warning: "text-warning-foreground",
    destructive: "text-destructive",
  }[tone];

  return (
    <div className={cn("rounded-xl border bg-card p-5 shadow-sm", className)}>
      <div className="text-xs font-medium text-muted-foreground tracking-wide uppercase">
        {label}
      </div>
      <div className={cn("mt-1 text-2xl font-semibold leading-tight", toneCls)}>{value}</div>
      {sublabel ? <div className="mt-1 text-xs text-muted-foreground">{sublabel}</div> : null}
      {hint ? <div className="mt-2 text-xs text-muted-foreground/80 italic">{hint}</div> : null}
    </div>
  );
}
