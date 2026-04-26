"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, ClipboardList, FileText, PhoneCall } from "lucide-react";

const ITEMS = [
  { href: "/", label: "Overview", icon: BarChart3 },
  { href: "/calls", label: "Calls", icon: PhoneCall },
  { href: "/loads", label: "Loads", icon: FileText },
  { href: "/negotiations", label: "Negotiations", icon: ClipboardList },
];

function isActive(pathname: string, href: string) {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function TopNav() {
  const pathname = usePathname();

  return (
    <nav className="flex items-center gap-2 text-sm">
      {ITEMS.map(({ href, label, icon: Icon }) => {
        const active = isActive(pathname, href);
        return (
          <Link
            key={href}
            href={href}
            aria-current={active ? "page" : undefined}
            className={
              "inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 transition " +
              (active
                ? "bg-primary/15 text-foreground ring-1 ring-primary/40 shadow-sm font-semibold"
                : "text-muted-foreground hover:bg-primary/10 hover:text-foreground")
            }
          >
            <Icon className={"h-3.5 w-3.5 " + (active ? "text-primary" : "")} />
            <span>{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
