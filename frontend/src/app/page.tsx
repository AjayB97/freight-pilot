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

export const dynamic = "force-dynamic";

function WindowTabs({ current }: { current: number }) {
  const windows = [7, 30, 90];
  return (
    <div className="inline-flex rounded-lg border bg-card p-1 text-sm">
      {windows.map((w) => (
        <a
          key={w}
          href={`?window=${w}`}
          className={
            "px-3 py-1.5 rounded-md transition " +
            (w === current
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:text-foreground")
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

  return (
    <div className="space-y-8">
      <div className="flex items-end justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Operations overview</h1>
          <p className="text-sm text-muted-foreground">
            How the inbound carrier agent is performing against revenue, conversion and margin.
          </p>
        </div>
        <WindowTabs current={windowDays} />
      </div>

      {/* Top-line KPIs */}
      <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Booked revenue"
          value={formatUSD(metrics.booked_revenue)}
          sublabel={`${metrics.booked_calls} of ${metrics.total_calls} calls booked`}
          tone="success"
          hint="Sum of final rates for calls with outcome = booked."
        />
        <Stat
          label="Conversion"
          value={formatPct(metrics.conversion_rate, 1)}
          sublabel={`${metrics.booked_calls} bookings / ${metrics.total_calls} calls`}
          tone={metrics.conversion_rate >= 0.4 ? "success" : "warning"}
          hint="Calls that ended in outcome = booked."
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
        />
        <Stat
          label="Lost pipeline"
          value={formatUSD(metrics.lost_pipeline_value)}
          sublabel="Unbooked rates from no_agreement / declined / abandoned"
          tone={metrics.lost_pipeline_value > metrics.booked_revenue ? "destructive" : "default"}
          hint="Recoverable if negotiation or matching improves."
        />
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
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Conversion funnel</CardTitle>
            <CardDescription>Where calls drop off between ring and book.</CardDescription>
          </CardHeader>
          <CardContent>
            <Funnel points={metrics.funnel} />
          </CardContent>
        </Card>
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Call outcomes</CardTitle>
            <CardDescription>Distribution of how calls ended.</CardDescription>
          </CardHeader>
          <CardContent>
            <OutcomesChart outcomes={metrics.outcomes} />
          </CardContent>
        </Card>
        <Card className="lg:col-span-1">
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
      <Card>
        <CardHeader>
          <CardTitle>Top lanes by volume</CardTitle>
          <CardDescription>
            Conversion and margin per lane. Double down on green, investigate red.
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
          <div className="rounded-xl border bg-card p-8 text-center text-sm text-muted-foreground">
            No calls recorded yet. Once the HappyRobot agent wraps a call, it will POST to
            <code className="mx-1">/calls</code> and rows will appear here.
          </div>
        )}
      </section>
    </div>
  );
}
