import { api } from "@/lib/api";
import { Stat } from "@/components/ui/stat";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Funnel } from "@/components/funnel";
import { Recommendations } from "@/components/recommendations";
import { OutcomesChart } from "@/components/outcomes-chart";
import { SentimentBar } from "@/components/sentiment-bar";
import { LaneTable } from "@/components/lane-table";
import { CallRow } from "@/components/call-row";
import { formatPct, formatUSD } from "@/lib/utils";
import { CalendarDays, CircleDollarSign, PhoneCall, TrendingUp } from "lucide-react";

export const dynamic = "force-dynamic";

function WindowTabs({ current }: { current: number }) {
  const windows = [7, 30, 90];
  return (
    <div className="inline-flex rounded-2xl border border-primary/30 bg-card/80 p-1 text-sm shadow-lg shadow-black/20 backdrop-blur">
      {windows.map((w) => (
        <a
          key={w}
          href={`?window=${w}`}
          className={
            "px-3 py-1.5 rounded-xl transition " +
            (w === current
              ? "bg-primary text-primary-foreground shadow-sm"
              : "text-muted-foreground hover:bg-primary/10 hover:text-foreground")
          }
        >
          Last {w}d
        </a>
      ))}
    </div>
  );
}

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ window?: string }>;
}) {
  const { window } = await searchParams;
  const windowDays = Number(window) || 30;

  const [metrics, recentCalls] = await Promise.all([
    api.metrics(windowDays),
    api.recentCalls(6),
  ]);

  const healthyMargin =
    metrics.avg_margin_pct !== null && metrics.avg_margin_pct >= 0 && metrics.avg_margin_pct <= 0.1;
  const marginTone = healthyMargin
    ? "success"
    : metrics.avg_margin_pct !== null && metrics.avg_margin_pct < 0
      ? "destructive"
      : "warning";
  const avgRoundsLabel =
    metrics.avg_rounds_to_book === null ? "—" : `${metrics.avg_rounds_to_book.toFixed(1)} rounds`;

  return (
    <div className="space-y-8 pb-3">
      <section className="overflow-hidden rounded-2xl border border-primary/25 bg-gradient-to-br from-primary/[0.18] via-card/90 to-violet-500/10 shadow-xl shadow-black/20">
        <div className="flex items-start justify-between gap-4 flex-wrap p-6 pb-4">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight text-balance">Operations overview</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Revenue, conversion, and margin performance for inbound carrier sales.
            </p>
          </div>
          <WindowTabs current={windowDays} />
        </div>
        <div className="grid gap-3 border-t border-primary/20 bg-background/40 p-4 md:grid-cols-3">
          <div className="rounded-xl border border-primary/25 bg-card/85 p-3">
            <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              <CalendarDays className="h-3.5 w-3.5" />
              Reporting window
            </div>
            <div className="mt-1 text-lg font-semibold">{windowDays} days</div>
          </div>
          <div className="rounded-xl border border-primary/25 bg-card/85 p-3">
            <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              <PhoneCall className="h-3.5 w-3.5" />
              Throughput
            </div>
            <div className="mt-1 text-lg font-semibold">
              {metrics.total_calls} calls <span className="text-muted-foreground">/ {metrics.booked_calls} booked</span>
            </div>
          </div>
          <div className="rounded-xl border border-primary/25 bg-card/85 p-3">
            <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              <TrendingUp className="h-3.5 w-3.5" />
              Avg rounds to book
            </div>
            <div className="mt-1 text-lg font-semibold">{avgRoundsLabel}</div>
          </div>
        </div>
      </section>

      {/* Top-line KPIs */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4">
        <Stat
          label="Booked revenue"
          value={formatUSD(metrics.booked_revenue)}
          sublabel={`${metrics.booked_calls} of ${metrics.total_calls} calls booked`}
          tone="success"
          hint="Sum of final rates for calls with outcome = booked."
          className="bg-gradient-to-br from-emerald-500/16 via-card/95 to-emerald-400/10 border-emerald-400/35"
          icon={CircleDollarSign}
        />
        <Stat
          label="Conversion"
          value={formatPct(metrics.conversion_rate, 1)}
          sublabel={`${metrics.booked_calls} bookings / ${metrics.total_calls} calls`}
          tone={metrics.conversion_rate >= 0.4 ? "success" : "warning"}
          hint="Calls that ended in outcome = booked."
          className="bg-gradient-to-br from-sky-500/18 via-card/95 to-cyan-400/12 border-sky-400/35"
          icon={TrendingUp}
        />
        <Stat
          label="Avg margin vs loadboard"
          value={
            metrics.avg_margin_pct === null
              ? "—"
              : `${metrics.avg_margin_pct > 0 ? "+" : ""}${(metrics.avg_margin_pct * 100).toFixed(1)}%`
          }
          sublabel={`Avg booked ${formatUSD(metrics.avg_final_rate)}`}
          tone={marginTone}
          hint="Where we're landing vs the listed rate. Close to 0% is ideal."
          className="bg-gradient-to-br from-amber-500/16 via-card/95 to-orange-400/10 border-amber-400/35"
          icon={TrendingUp}
        />
        <Stat
          label="Lost pipeline"
          value={formatUSD(metrics.lost_pipeline_value)}
          sublabel="Unbooked rates from no_agreement / declined / abandoned"
          tone={metrics.lost_pipeline_value > metrics.booked_revenue ? "destructive" : "default"}
          hint="Recoverable if negotiation or matching improves."
          className="bg-gradient-to-br from-rose-500/16 via-card/95 to-red-400/10 border-rose-400/35"
          icon={CircleDollarSign}
        />
      </div>

      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-lg font-semibold tracking-tight">Diagnostics</h2>
          <p className="text-sm text-muted-foreground">
            Funnel, outcomes, sentiment, and lane performance.
          </p>
        </div>
      </div>

      {/* Recommendations — the 'what do I do next' layer */}
      <section>
        <div className="mb-3 flex items-baseline justify-between">
          <h2 className="text-base font-semibold">What to do next</h2>
          <div className="text-xs text-muted-foreground">
            Auto-generated from the {windowDays}d window
          </div>
        </div>
        <Recommendations items={metrics.recommendations} />
      </section>

      {/* Funnel + Outcomes + Sentiment */}
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1 border-indigo-400/30 bg-gradient-to-br from-card/95 via-card/90 to-indigo-500/10 shadow-md shadow-indigo-950/40">
          <CardHeader>
            <CardTitle>Conversion funnel</CardTitle>
            <CardDescription>Stage-by-stage call progression.</CardDescription>
          </CardHeader>
          <CardContent>
            <Funnel points={metrics.funnel} />
          </CardContent>
        </Card>
        <Card className="lg:col-span-1 border-emerald-400/30 bg-gradient-to-br from-card/95 via-card/90 to-emerald-500/10 shadow-md shadow-emerald-950/40">
          <CardHeader>
            <CardTitle>Call outcomes</CardTitle>
            <CardDescription>Outcome mix across the selected window.</CardDescription>
          </CardHeader>
          <CardContent>
            <OutcomesChart outcomes={metrics.outcomes} />
          </CardContent>
        </Card>
        <Card className="lg:col-span-1 border-cyan-400/30 bg-gradient-to-br from-card/95 via-card/90 to-cyan-500/10 shadow-md shadow-cyan-950/40">
          <CardHeader>
            <CardTitle>Carrier sentiment</CardTitle>
            <CardDescription>
              {formatPct(metrics.negative_sentiment_rate, 0)} negative — drop in on those first.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <SentimentBar sentiment={metrics.sentiment} />
          </CardContent>
        </Card>
      </div>

      {/* Lanes */}
      <Card className="border-violet-400/30 bg-gradient-to-br from-card/95 via-card/90 to-violet-500/10 shadow-md shadow-violet-950/40">
        <CardHeader>
          <CardTitle>Top lanes by volume</CardTitle>
          <CardDescription>
            Conversion and margin by lane.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <LaneTable lanes={metrics.top_lanes} />
        </CardContent>
      </Card>

      {/* Recent calls */}
      <section>
        <div className="mb-3 flex items-baseline justify-between">
          <h2 className="text-base font-semibold">Recent calls</h2>
          <a href="/calls" className="text-sm text-muted-foreground hover:text-foreground">
            View all →
          </a>
        </div>
        {recentCalls.length ? (
          <div className="grid gap-3 md:grid-cols-2">
            {recentCalls.map((c) => (
              <CallRow key={c.id} call={c} />
            ))}
          </div>
        ) : (
          <div className="rounded-xl border border-primary/30 bg-gradient-to-br from-primary/20 via-card/90 to-cyan-500/10 p-8 text-center text-sm text-muted-foreground">
            No calls recorded yet. Once the HappyRobot agent wraps a call, it will POST to
            <code className="mx-1">/calls</code> and rows will appear here.
          </div>
        )}
      </section>
    </div>
  );
}
