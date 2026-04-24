import * as React from "react";
import { cn } from "@/lib/utils";

type Variant = "default" | "success" | "warning" | "destructive" | "muted";

const variants: Record<Variant, string> = {
  default: "bg-primary text-primary-foreground",
  success: "bg-success/15 text-success border border-success/30",
  warning: "bg-warning/18 text-warning border border-warning/45",
  destructive: "bg-destructive/15 text-destructive border border-destructive/30",
  muted: "bg-muted text-muted-foreground",
};

export function Badge({
  className,
  variant = "default",
  ...props
}: React.HTMLAttributes<HTMLSpanElement> & { variant?: Variant }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium",
        variants[variant],
        className,
      )}
      {...props}
    />
  );
}
