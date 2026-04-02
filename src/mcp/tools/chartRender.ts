import { renderChart, extractPieSlices, extractSurfaceSpec } from "../../lib/plot/core/renderChart";
import { renderSceneToSvg } from "../../lib/plot/server/renderSvg";
import type { ChartSpec } from "../../lib/plot/core/renderChart";
import type { Scene } from "../../lib/plot/core/types";

// ── Result types ────────────────────────────────────────────────────────

export type ComponentHint = "FlashChart" | "PieChart" | "Surface3D";

export interface RenderResult {
  /** Which React component the frontend should use */
  componentHint: ComponentHint;
  /** The resolved chart type */
  chartType: string;
  /** Scene graph for FlashChart (standard chart types) */
  scene?: Scene;
  /** Pie/donut slice data for PieChart component */
  pieData?: {
    slices: { label: string; value: number; color: string }[];
    donut: boolean;
    donutRatio: number;
  };
  /** Surface data for Surface3D component */
  surfaceData?: {
    z: number[][];
    x?: number[][];
    y?: number[][];
    wireframe: boolean;
  };
  /** Optional SVG string (when format="svg") */
  svg?: string;
}

// ── Main render function ────────────────────────────────────────────────

export function executeChartRender(
  spec: ChartSpec,
  format: "scene" | "svg" = "scene"
): RenderResult {
  const type = spec.type;

  // Pie / Donut → extracted slice data for PieChart component
  if (type === "pie" || type === "donut") {
    const pieData = extractPieSlices(spec);
    const result: RenderResult = {
      componentHint: "PieChart",
      chartType: type,
      pieData,
    };
    if (format === "svg") {
      // For SVG fallback, render via the standard pipeline
      const scene = renderChart({ ...spec, type: "bar" }); // pie doesn't go through renderChart
      result.svg = renderSceneToSvg(scene);
    }
    return result;
  }

  // Surface / Surface 3D → extracted surface data for Surface3D component
  if (type === "surface" || type === "surface_3d") {
    const surfaceData = extractSurfaceSpec(spec);
    return {
      componentHint: "Surface3D",
      chartType: type,
      surfaceData: surfaceData
        ? {
            z: surfaceData.z,
            x: surfaceData.x,
            y: surfaceData.y,
            wireframe: surfaceData.wireframe ?? true,
          }
        : undefined,
    };
  }

  // All other chart types → standard Scene pipeline
  const scene = renderChart(spec);
  const result: RenderResult = {
    componentHint: "FlashChart",
    chartType: type,
    scene,
  };

  if (format === "svg") {
    result.svg = renderSceneToSvg(scene);
  }

  return result;
}
