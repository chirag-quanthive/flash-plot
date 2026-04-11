#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

import { executeChartRender } from "./tools/chartRender.js";
import { resolveChartType } from "./tools/chartResolve.js";
import { getChartStyles } from "./tools/chartStyles.js";

// ── Server setup ────────────────────────────────────────────────────────

const server = new McpServer({
  name: "flash-plot",
  version: "1.0.0",
});

// ── Tool: chart_render ──────────────────────────────────────────────────

server.tool(
  "chart_render",
  "Render a chart from a ChartSpec JSON. Returns a Scene graph (for FlashChart), pie slice data (for PieChart), or surface data (for Surface3D) — plus an optional SVG string. The componentHint field tells the frontend which React component to use.",
  {
    spec: z.object({
      type: z.string().describe("Chart type: line, bar, stacked_bar, scatter, bubble, area, histogram, pie, donut, surface_3d, candlestick, heatmap, waterfall, violin, boxplot"),
      title: z.string().optional(),
      subtitle: z.string().optional(),
      series: z.array(z.object({
        data: z.array(z.number()),
        x: z.array(z.number()).optional(),
        label: z.string().optional(),
        color: z.string().optional(),
        lineWidth: z.number().optional(),
        lineStyle: z.enum(["solid", "dashed", "dotted", "dashdot"]).optional(),
        fillOpacity: z.number().optional(),
        barWidth: z.number().optional(),
        stacked: z.boolean().optional(),
        markerSize: z.number().optional(),
        sizes: z.array(z.number()).optional(),
        open: z.array(z.number()).optional(),
        high: z.array(z.number()).optional(),
        low: z.array(z.number()).optional(),
        close: z.array(z.number()).optional(),
        q1: z.number().optional(),
        median: z.number().optional(),
        q3: z.number().optional(),
        whiskerLow: z.number().optional(),
        whiskerHigh: z.number().optional(),
        outliers: z.array(z.number()).optional(),
      })).optional(),
      slices: z.array(z.object({
        value: z.number(),
        label: z.string(),
        color: z.string().optional(),
      })).optional(),
      donutRatio: z.number().optional(),
      surface: z.object({
        z: z.array(z.array(z.number())),
        x: z.array(z.array(z.number())).optional(),
        y: z.array(z.array(z.number())).optional(),
        color: z.string().optional(),
        wireframe: z.boolean().optional(),
      }).optional(),
      heatmap: z.object({
        data: z.array(z.array(z.number())),
        rowLabels: z.array(z.string()).optional(),
        colLabels: z.array(z.string()).optional(),
        colorRange: z.tuple([z.string(), z.string()]).optional(),
      }).optional(),
      bins: z.number().optional(),
      xLabels: z.array(z.string()).optional(),
      xAxis: z.object({
        label: z.string().optional(),
        min: z.number().optional(),
        max: z.number().optional(),
        scale: z.enum(["linear", "log", "symlog"]).optional(),
      }).optional(),
      yAxis: z.object({
        label: z.string().optional(),
        min: z.number().optional(),
        max: z.number().optional(),
        scale: z.enum(["linear", "log", "symlog"]).optional(),
      }).optional(),
      legend: z.object({
        show: z.boolean().optional(),
        position: z.enum(["best", "upper-left", "upper-right", "lower-left", "lower-right"]).optional(),
      }).optional(),
      grid: z.boolean().optional(),
      width: z.number().optional(),
      height: z.number().optional(),
      hlines: z.array(z.object({
        y: z.number(),
        color: z.string().optional(),
        label: z.string().optional(),
        lineStyle: z.enum(["solid", "dashed"]).optional(),
      })).optional(),
      vlines: z.array(z.object({
        x: z.number(),
        color: z.string().optional(),
        label: z.string().optional(),
        lineStyle: z.enum(["solid", "dashed"]).optional(),
      })).optional(),
      annotations: z.array(z.object({
        text: z.string(),
        x: z.number(),
        y: z.number(),
        color: z.string().optional(),
      })).optional(),
    }).describe("Full ChartSpec — the JSON schema for chart rendering"),
    format: z.enum(["scene", "svg"]).optional().describe("Output format. 'scene' returns JSON for React components (default). 'svg' also includes a static SVG string."),
  },
  async ({ spec, format }) => {
    try {
      const result = executeChartRender(spec as any, format ?? "scene");
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(result),
          },
        ],
      };
    } catch (err: any) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({ error: err.message ?? "Render failed" }),
          },
        ],
        isError: true,
      };
    }
  }
);

// ── Tool: chart_resolve_type ────────────────────────────────────────────

server.tool(
  "chart_resolve_type",
  "Given a description of the data and optionally column names, recommend the best chart type. Returns the recommended type, alternatives, reasoning, and a skeleton ChartSpec.",
  {
    description: z.string().describe("Natural language description of the data (e.g. 'monthly revenue by product category', 'stock OHLC prices', 'portfolio allocation weights')"),
    columns: z.array(z.string()).optional().describe("Column names from the dataset (e.g. ['date', 'open', 'high', 'low', 'close', 'volume'])"),
  },
  async ({ description, columns }) => {
    const result = resolveChartType(description, columns);
    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(result),
        },
      ],
    };
  }
);

// ── Tool: chart_get_styles ──────────────────────────────────────────────

server.tool(
  "chart_get_styles",
  "Get the current chart theme, color palettes, and list of all supported chart types with descriptions. Use this to understand available styling options before rendering.",
  {},
  async () => {
    const result = getChartStyles();
    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(result),
        },
      ],
    };
  }
);

// ── Start server ────────────────────────────────────────────────────────

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("flash-plot MCP server failed to start:", err);
  process.exit(1);
});
