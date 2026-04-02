import { NextRequest, NextResponse } from "next/server";
import { figure } from "@/lib/plot/core/figure";
import { renderSceneToSvg } from "@/lib/plot/server/renderSvg";

// ── Types for the JSON chart spec ──────────────────────────────────────

interface ChartCommand {
  method: string;
  args?: unknown[];
  kwargs?: Record<string, unknown>;
}

interface ChartSpec {
  commands: ChartCommand[];
  width?: number;
  height?: number;
}

// ── POST /api/chart ────────────────────────────────────────────────────
// Accepts a JSON body describing chart commands, returns SVG.
//
// Example body:
// {
//   "commands": [
//     { "method": "set_title", "args": ["My Chart"] },
//     { "method": "plot", "args": [[1,2,3,4]], "kwargs": {"color":"#4ECDC4","label":"Series A"} },
//     { "method": "grid", "args": [true] },
//     { "method": "legend" }
//   ],
//   "width": 595,
//   "height": 280
// }

export async function POST(req: NextRequest) {
  try {
    const spec: ChartSpec = await req.json();

    const fig = figure({
      width: spec.width ?? 595,
      height: spec.height ?? 280,
    });
    const ax = fig.subplot(1, 1, 1);

    for (const cmd of spec.commands) {
      const method = cmd.method;
      const args = cmd.args ?? [];
      const kwargs = cmd.kwargs ?? {};

      // Merge kwargs into the last positional arg if it's an options object
      const callArgs = [...args];
      if (Object.keys(kwargs).length > 0) {
        callArgs.push(kwargs);
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const target = ax as any;
      if (typeof target[method] === "function") {
        target[method](...callArgs);
      } else {
        return NextResponse.json(
          { error: `Unknown method: ${method}` },
          { status: 400 }
        );
      }
    }

    const scene = fig.render();
    const svg = renderSceneToSvg(scene);

    return new NextResponse(svg, {
      headers: {
        "Content-Type": "image/svg+xml",
        "Access-Control-Allow-Origin": "*",
      },
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}

// Allow CORS preflight for Colab
export async function OPTIONS() {
  return new NextResponse(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
