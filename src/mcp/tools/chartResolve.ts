import type { ChartSpec } from "../../lib/plot/core/renderChart";

// ── Result type ─────────────────────────────────────────────────────────

export interface ResolveResult {
  /** Best chart type for this data */
  recommendedType: string;
  /** Alternative chart types that could also work */
  alternatives: string[];
  /** Brief explanation of why this type was chosen */
  reasoning: string;
  /** Skeleton ChartSpec the agent can fill with real data */
  exampleSpec: Partial<ChartSpec>;
}

// ── Keyword sets ────────────────────────────────────────────────────────

const TIME_KEYWORDS = ["date", "time", "timestamp", "datetime", "year", "month", "day", "week", "quarter", "period"];
const OHLC_KEYWORDS = ["open", "high", "low", "close", "ohlc", "candlestick"];
const DISTRIBUTION_KEYWORDS = ["distribution", "frequency", "histogram", "density", "kde"];
const PROPORTION_KEYWORDS = ["proportion", "share", "allocation", "composition", "breakdown", "percentage", "weight"];
const COMPARISON_KEYWORDS = ["comparison", "compare", "versus", "vs", "category", "categories", "sector", "group"];
const CORRELATION_KEYWORDS = ["correlation", "heatmap", "matrix", "covariance"];
const FLOW_KEYWORDS = ["waterfall", "cumulative", "bridge", "flow", "contribution"];
const SURFACE_KEYWORDS = ["surface", "3d", "terrain", "topography", "mesh", "grid"];
const SCATTER_KEYWORDS = ["scatter", "relationship", "regression", "cluster"];

function hasKeyword(text: string, keywords: string[]): boolean {
  const lower = text.toLowerCase();
  return keywords.some((k) => lower.includes(k));
}

// ── Resolver ────────────────────────────────────────────────────────────

export function resolveChartType(
  description: string,
  columns?: string[]
): ResolveResult {
  const desc = description.toLowerCase();
  const cols = (columns ?? []).map((c) => c.toLowerCase());

  // OHLC candlestick detection
  if (hasKeyword(desc, OHLC_KEYWORDS) || OHLC_KEYWORDS.filter((k) => cols.includes(k)).length >= 3) {
    return {
      recommendedType: "candlestick",
      alternatives: ["line", "area"],
      reasoning: "OHLC data detected — candlestick chart shows open/high/low/close per period.",
      exampleSpec: {
        type: "candlestick",
        title: "Price Action",
        series: [{ data: [], open: [], high: [], low: [], close: [] }],
      },
    };
  }

  // Surface / 3D
  if (hasKeyword(desc, SURFACE_KEYWORDS)) {
    return {
      recommendedType: "surface_3d",
      alternatives: ["heatmap"],
      reasoning: "3D/surface data — interactive surface plot with rotation and zoom.",
      exampleSpec: {
        type: "surface_3d",
        title: "Surface Plot",
        surface: { z: [[]], wireframe: true },
      },
    };
  }

  // Correlation / heatmap
  if (hasKeyword(desc, CORRELATION_KEYWORDS)) {
    return {
      recommendedType: "heatmap",
      alternatives: ["surface_3d"],
      reasoning: "Matrix/correlation data — heatmap shows value intensity across a grid.",
      exampleSpec: {
        type: "heatmap",
        title: "Correlation Matrix",
        heatmap: { data: [[]], rowLabels: [], colLabels: [] },
      },
    };
  }

  // Proportion / part-of-whole
  if (hasKeyword(desc, PROPORTION_KEYWORDS)) {
    return {
      recommendedType: "pie",
      alternatives: ["donut", "bar", "stacked_bar"],
      reasoning: "Part-of-whole data — pie/donut chart shows proportional breakdown.",
      exampleSpec: {
        type: "pie",
        title: "Allocation",
        slices: [{ label: "Category A", value: 0 }],
      },
    };
  }

  // Waterfall / flow
  if (hasKeyword(desc, FLOW_KEYWORDS)) {
    return {
      recommendedType: "waterfall",
      alternatives: ["bar", "stacked_bar"],
      reasoning: "Cumulative/flow data — waterfall chart shows sequential contributions.",
      exampleSpec: {
        type: "waterfall",
        title: "P&L Waterfall",
        series: [{ data: [], label: "Values" }],
        xLabels: [],
      },
    };
  }

  // Distribution
  if (hasKeyword(desc, DISTRIBUTION_KEYWORDS)) {
    return {
      recommendedType: "histogram",
      alternatives: ["violin", "boxplot"],
      reasoning: "Distribution data — histogram shows frequency/density.",
      exampleSpec: {
        type: "histogram",
        title: "Distribution",
        series: [{ data: [] }],
        bins: 20,
      },
    };
  }

  // Scatter / relationship
  if (hasKeyword(desc, SCATTER_KEYWORDS)) {
    return {
      recommendedType: "scatter",
      alternatives: ["bubble", "line"],
      reasoning: "Relationship data — scatter plot shows correlation between two variables.",
      exampleSpec: {
        type: "scatter",
        title: "Scatter Plot",
        series: [{ data: [], x: [], label: "Series" }],
      },
    };
  }

  // Comparison / categorical
  if (hasKeyword(desc, COMPARISON_KEYWORDS)) {
    return {
      recommendedType: "bar",
      alternatives: ["stacked_bar", "line"],
      reasoning: "Categorical comparison — bar chart shows values across categories.",
      exampleSpec: {
        type: "bar",
        title: "Comparison",
        series: [{ data: [], label: "Series" }],
        xLabels: [],
      },
    };
  }

  // Time series (default for most financial data)
  if (hasKeyword(desc, TIME_KEYWORDS) || cols.some((c) => TIME_KEYWORDS.some((k) => c.includes(k)))) {
    return {
      recommendedType: "line",
      alternatives: ["area", "bar"],
      reasoning: "Time series data — line chart shows trends over time.",
      exampleSpec: {
        type: "line",
        title: "Time Series",
        series: [{ data: [], label: "Series" }],
        xLabels: [],
      },
    };
  }

  // Fallback: line chart
  return {
    recommendedType: "line",
    alternatives: ["bar", "area", "scatter"],
    reasoning: "General data — line chart is a versatile default.",
    exampleSpec: {
      type: "line",
      title: "Chart",
      series: [{ data: [], label: "Series" }],
    },
  };
}
