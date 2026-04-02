import { getTheme, listThemes, FLASH_DARK } from "../../lib/plot/core/theme";
import { DEFAULT_COLORS } from "../../lib/plot/core/renderChart";

// ── Chart type catalog ──────────────────────────────────────────────────

const CHART_TYPE_CATALOG = [
  { type: "line", description: "Line chart for time series and trends" },
  { type: "bar", description: "Bar chart for categorical comparisons" },
  { type: "stacked_bar", description: "Stacked bar chart for part-of-whole across categories" },
  { type: "scatter", description: "Scatter plot for correlation between two variables" },
  { type: "bubble", description: "Bubble chart — scatter with variable-size markers" },
  { type: "area", description: "Area chart — filled line chart for volume/magnitude" },
  { type: "histogram", description: "Histogram for frequency distribution" },
  { type: "pie", description: "Pie chart for proportional breakdown" },
  { type: "donut", description: "Donut chart — pie with hollow center" },
  { type: "surface_3d", description: "Interactive 3D surface plot with rotation/zoom" },
  { type: "candlestick", description: "Candlestick chart for OHLC price data" },
  { type: "heatmap", description: "Heatmap for matrix/correlation data" },
  { type: "waterfall", description: "Waterfall chart for cumulative contributions" },
  { type: "violin", description: "Violin plot for distribution shape" },
  { type: "boxplot", description: "Box plot for quartile summary statistics" },
];

// ── Result type ─────────────────────────────────────────────────────────

export interface StylesResult {
  /** Current theme object */
  theme: typeof FLASH_DARK;
  /** Available theme names */
  availableThemes: string[];
  /** Default color palettes per chart type */
  palettes: typeof DEFAULT_COLORS;
  /** All supported chart types with descriptions */
  chartTypes: typeof CHART_TYPE_CATALOG;
}

// ── Getter ──────────────────────────────────────────────────────────────

export function getChartStyles(): StylesResult {
  return {
    theme: getTheme("flash-dark"),
    availableThemes: listThemes(),
    palettes: DEFAULT_COLORS,
    chartTypes: CHART_TYPE_CATALOG,
  };
}
