import type { Metadata } from "next";
import Link from "next/link";
import { Truck } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Freight Pilot — Inbound Carrier Sales",
  description: "Operator dashboard for the HappyRobot inbound carrier agent.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b bg-card/60 backdrop-blur">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <Truck className="h-4 w-4" />
              </div>
              <div>
                <div className="text-sm font-semibold leading-none">Freight Pilot</div>
                <div className="text-xs text-muted-foreground">Inbound Carrier Sales</div>
              </div>
            </Link>
            <nav className="flex items-center gap-5 text-sm">
              <Link href="/" className="text-muted-foreground hover:text-foreground">
                Overview
              </Link>
              <Link href="/calls" className="text-muted-foreground hover:text-foreground">
                Calls
              </Link>
              <Link href="/loads" className="text-muted-foreground hover:text-foreground">
                Loads
              </Link>
              <Link
                href="/negotiations"
                className="text-muted-foreground hover:text-foreground"
              >
                Negotiations
              </Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        <footer className="border-t mt-12">
          <div className="mx-auto max-w-7xl px-6 py-6 text-xs text-muted-foreground flex justify-between">
            <div>Freight Pilot · Built for Acme Logistics</div>
            <div>
              Powered by <span className="font-medium">HappyRobot</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
