/**
 * Typed client for the Freight Pilot API.
 *
 * All calls happen from server components so the API key never hits the
 * browser. Never import this file from a client component.
 */
import "server-only";

const BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8080";
const API_KEY = process.env.API_KEY ?? "dev-local-key";

type FetchOptions = RequestInit & { revalidate?: number };

async function apiFetch<T>(path: string, opts: FetchOptions = {}): Promise<T> {
  const { revalidate = 15, ...rest } = opts;
  const res = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...(rest.headers ?? {}),
    },
    next: { revalidate },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${path} failed: ${res.status} ${body}`);
  }
  return (await res.json()) as T;
}

// ----- Types (mirror backend schemas) -----

export type FunnelPoint = { stage: string; count: number };
export type OutcomeBreakdown = { outcome: string; count: number; revenue: number };
export type SentimentBreakdown = { sentiment: string; count: number };
export type LanePerformance = {
  origin: string;
  destination: string;
  equipment_type: string;
  calls: number;
  booked: number;
  conversion: number;
  avg_final_rate: number | null;
  avg_loadboard_rate: number | null;
  avg_margin_pct: number | null;
};

export type MetricsSummary = {
  window_days: number;
  total_calls: number;
  booked_calls: number;
  conversion_rate: number;
  booked_revenue: number;
  avg_final_rate: number | null;
  avg_loadboard_rate: number | null;
  avg_margin_pct: number | null;
  avg_rounds_to_book: number | null;
  lost_pipeline_value: number;
  negative_sentiment_rate: number;
  funnel: FunnelPoint[];
  outcomes: OutcomeBreakdown[];
  sentiment: SentimentBreakdown[];
  top_lanes: LanePerformance[];
  stale_loads: number;
  recommendations: string[];
};

export type Call = {
  id: number;
  external_call_id: string | null;
  mc_number: string | null;
  carrier_name: string | null;
  load_id: string | null;
  outcome: string;
  sentiment: string | null;
  loadboard_rate: number | null;
  initial_offer: number | null;
  final_rate: number | null;
  rounds: number | null;
  summary: string | null;
  transcript_url: string | null;
  extracted: Record<string, unknown> | null;
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
};

export type Load = {
  load_id: string;
  origin: string;
  destination: string;
  pickup_datetime: string;
  delivery_datetime: string;
  equipment_type: string;
  loadboard_rate: number;
  notes: string | null;
  weight: number | null;
  commodity_type: string | null;
  num_of_pieces: number | null;
  miles: number | null;
  dimensions: string | null;
  status: string;
};

export type NegotiationEvent = {
  id: number;
  call_external_id: string | null;
  load_id: string | null;
  mc_number: string | null;
  round_number: number;
  loadboard_rate: number;
  carrier_offer: number;
  broker_response: "accept" | "counter" | "reject";
  broker_counter: number | null;
  reasoning: string | null;
  created_at: string;
};

// ----- Endpoints -----

export const api = {
  metrics: (windowDays: number = 30) =>
    apiFetch<MetricsSummary>(`/metrics/summary?window_days=${windowDays}`),
  recentCalls: (limit = 50) => apiFetch<Call[]>(`/calls?limit=${limit}`),
  getCall: (id: number) => apiFetch<Call>(`/calls/${id}`),
  loads: (status?: string, q?: string) => {
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (q) params.set("q", q);
    params.set("limit", "200");
    return apiFetch<Load[]>(`/loads?${params.toString()}`);
  },
  recentNegotiations: (limit = 50) =>
    apiFetch<NegotiationEvent[]>(`/metrics/negotiations?limit=${limit}`),
  health: () => apiFetch<{ status: string }>(`/health`, { revalidate: 0 }),
};
