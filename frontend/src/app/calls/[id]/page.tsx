import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDateTime, formatUSD } from "@/lib/utils";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function CallDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let call;
  try {
    call = await api.getCall(Number(id));
  } catch {
    notFound();
  }

  const extracted = call.extracted ?? {};

  return (
    <div className="space-y-6">
      <div>
        <a href="/calls" className="text-sm text-muted-foreground hover:text-foreground">
          ← Back to calls
        </a>
        <div className="mt-2 flex items-center gap-2 flex-wrap">
          <h1 className="text-2xl font-semibold tracking-tight">
            {call.carrier_name ?? "Unknown carrier"}
          </h1>
          <Badge variant="muted">{call.outcome}</Badge>
          {call.sentiment ? <Badge variant="muted">{call.sentiment}</Badge> : null}
        </div>
        <div className="text-sm text-muted-foreground">
          {call.mc_number ? `MC ${call.mc_number} · ` : ""}
          {formatDateTime(call.started_at ?? call.created_at)}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Commercials</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            <Row k="Load" v={call.load_id ?? "—"} />
            <Row k="Loadboard rate" v={formatUSD(call.loadboard_rate)} />
            <Row k="Initial offer" v={formatUSD(call.initial_offer)} />
            <Row k="Final rate" v={formatUSD(call.final_rate)} mono />
            <Row k="Rounds" v={call.rounds?.toString() ?? "—"} />
          </CardContent>
        </Card>
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent className="text-sm whitespace-pre-wrap text-muted-foreground">
            {call.summary ?? "No summary captured."}
          </CardContent>
        </Card>
      </div>

      {Object.keys(extracted).length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Extracted fields</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="grid gap-3 sm:grid-cols-2 text-sm">
              {Object.entries(extracted).map(([k, v]) => (
                <div key={k} className="flex justify-between border-b pb-2">
                  <dt className="text-muted-foreground">{k}</dt>
                  <dd className="font-medium text-right">
                    {typeof v === "string" || typeof v === "number" || typeof v === "boolean"
                      ? String(v)
                      : JSON.stringify(v)}
                  </dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>
      ) : null}

      {call.transcript_url ? (
        <Card>
          <CardHeader>
            <CardTitle>Transcript</CardTitle>
          </CardHeader>
          <CardContent className="text-sm">
            <a
              className="text-primary underline"
              href={call.transcript_url}
              target="_blank"
              rel="noreferrer"
            >
              Open transcript in HappyRobot
            </a>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}

function Row({ k, v, mono }: { k: string; v: React.ReactNode; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{k}</span>
      <span className={mono ? "font-mono tabular-nums" : "tabular-nums"}>{v}</span>
    </div>
  );
}
