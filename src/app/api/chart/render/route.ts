import { NextRequest, NextResponse } from "next/server";
import { executeChartRender } from "@/mcp/tools/chartRender";
import type { ChartSpec } from "@/lib/plot/core/renderChart";

// ── CORS headers ────────────────────────────────────────────────────────

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export async function OPTIONS() {
  return new NextResponse(null, { status: 204, headers: CORS });
}

// ── POST /api/chart/render ──────────────────────────────────────────────
// Accepts a ChartSpec JSON body. Returns Scene JSON (or SVG).
//
// Example body:
// {
//   "spec": {
//     "type": "line",
//     "title": "Strategy vs Benchmark",
//     "series": [
//       { "data": [1, 3, 2, 5, 4], "label": "Strategy", "color": "#d4d4d4" },
//       { "data": [1, 2, 2, 3, 3], "label": "Benchmark", "color": "#707070" }
//     ],
//     "xLabels": ["Jan", "Feb", "Mar", "Apr", "May"]
//   },
//   "format": "scene"
// }
//
// Response:
// {
//   "componentHint": "FlashChart",
//   "chartType": "line",
//   "scene": { ... }
// }

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const spec: ChartSpec = body.spec ?? body;
    const format: "scene" | "svg" = body.format ?? "scene";

    const result = executeChartRender(spec, format);

    return NextResponse.json(result, { headers: CORS });
  } catch (err: any) {
    return NextResponse.json(
      { error: err.message ?? "Render failed" },
      { status: 400, headers: CORS }
    );
  }
}
