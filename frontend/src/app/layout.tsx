import type { Metadata } from "next";
import Link from "next/link";
import { Truck } from "lucide-react";
import { Inter } from "next/font/google";
import { TopNav } from "@/components/top-nav";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: "Freight Pilot — Inbound Carrier Sales",
  description: "Operator dashboard for the HappyRobot inbound carrier agent.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen`}>
        <header className="sticky top-0 z-30 border-b border-primary/20 bg-background/70 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-indigo-500 text-primary-foreground shadow-sm">
                <Truck className="h-4 w-4" />
              </div>
              <div>
                <div className="text-sm font-semibold leading-none">Freight Pilot</div>
                <div className="text-xs text-muted-foreground">Inbound Carrier Sales</div>
              </div>
            </Link>
            <TopNav />
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        <footer className="mt-12 border-t border-primary/20">
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
