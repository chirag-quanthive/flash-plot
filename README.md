# Flash Plot

Premium dark-themed charting engine with a matplotlib-like API. Renders animated SVG charts with CSS keyframe animations, multi-layer bar glow effects, and a financial-grade dark theme.

Available as a **TypeScript/React** library (with MCP + HTTP API) and a **pure Python** package for Google Colab / Jupyter.

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Supported Chart Types](#supported-chart-types)
- [Python API Reference](#python-api-reference)
- [TypeScript API Reference](#typescript-api-reference)
- [MCP Server (AI Agent Integration)](#mcp-server-ai-agent-integration)
  - [Tool: chart_render](#tool-chart_render)
  - [Tool: chart_resolve_type](#tool-chart_resolve_type)
  - [Tool: chart_get_styles](#tool-chart_get_styles)
- [ChartSpec JSON Schema](#chartspec-json-schema)
- [HTTP API](#http-api)
- [Scene Graph Output](#scene-graph-output)
- [Architecture](#architecture)
- [Theme & Color Palettes](#theme--color-palettes)
- [Animation System](#animation-system)
- [Requirements](#requirements)

---

## Installation

### Python (Colab / Jupyter) — no server needed

```bash
pip install git+https://github.com/quant-hive/ChartingEngine.git#subdirectory=python
```

### TypeScript (Next.js / React)

```bash
git clone https://github.com/quant-hive/ChartingEngine.git
cd ChartingEngine
npm install
npm run dev        # Dev server on localhost:3000
```

---

## Quick Start

### Python

```python
from flash_plot import FlashPlot

fig = FlashPlot()
fig.set_title("Cumulative Returns")
fig.set_subtitle("Strategy vs Benchmark")
fig.plot([0, 5, -8, 15, 10, 25, 18, 55, 35, 80], color="#d4d4d4", label="Strategy")
fig.plot([5, 8, 10, 12, 15, 14, 16, 18, 15, 20], color="#707070", label="Benchmark")
fig.set_xticks(["Jan", "Mar", "May", "Jul", "Sep"])
fig.grid(True)
fig.legend()
fig.show()  # renders inline SVG in Jupyter/Colab
```

### TypeScript (Figure/Axes API)

```typescript
import { figure, FlashChart } from "./lib/plot";

const fig = figure();
const ax = fig.subplot(1, 1, 1);
ax.plot([0, 5, 12, 8, 18, 25], { color: "#d4d4d4", label: "Strategy" });
ax.plot([5, 8, 10, 12, 15], { color: "#707070", label: "Benchmark" });
ax.set_xticks(["Jan", "Feb", "Mar", "Apr", "May"]);
ax.grid(true);
ax.legend();
const scene = fig.render();

// In React:
<FlashChart scene={scene} />
```

### TypeScript (ChartSpec → Scene)

```typescript
import { renderChart } from "./lib/plot";

const scene = renderChart({
  type: "line",
  title: "Strategy vs Benchmark",
  series: [
    { data: [0, 5, 12, 8, 18], label: "Strategy", color: "#d4d4d4" },
    { data: [0, 3, 6, 5, 9], label: "Benchmark", color: "#707070" },
  ],
  xLabels: ["Jan", "Feb", "Mar", "Apr", "May"],
  grid: true,
});
```

---

## Supported Chart Types

| Type | Key | Description |
|------|-----|-------------|
| Line | `line` | Time series, trends, multi-line comparison |
| Bar | `bar` | Categorical comparison, grouped bars |
| Stacked Bar | `stacked_bar` | Composition over categories |
| Area | `area` | Cumulative values, filled line chart |
| Scatter | `scatter` | Correlation, clusters, risk-return |
| Bubble | `bubble` | Scatter with variable-size points |
| Histogram | `histogram` | Distribution, frequency |
| Pie | `pie` | Proportional breakdown |
| Donut | `donut` | Pie with center cutout |
| Candlestick | `candlestick` | OHLC price action |
| Surface 3D | `surface_3d` | Volatility surfaces, 3D data (WebGL) |
| Heatmap | `heatmap` | Correlation matrices, 2D grids |
| Waterfall | `waterfall` | Cumulative contribution, bridges |
| Violin | `violin` | Distribution shape comparison |
| Boxplot | `boxplot` | Statistical summary (quartiles, outliers) |

---

## Python API Reference

### `FlashPlot(width=595, height=280)`

Create a new chart figure.

### Plotting Methods

```python
fig.plot(y_data, x=None, color=None, label=None, line_width=1.5,
         line_style="solid", alpha=1.0, fill_opacity=None)

fig.bar(x_labels, y_data, color=None, label=None, alpha=1.0)

fig.scatter(x_data, y_data, color=None, label=None, size=4, alpha=1.0)

fig.hist(data, bins=10, color=None, label=None, alpha=1.0)

fig.fill_between(x, y1, y2=0, color=None, alpha=0.15, label=None)

fig.axhline(y, color="#707070", line_width=1, line_style="dashed")
fig.axvline(x, color="#707070", line_width=1, line_style="dashed")

fig.text(x, y, content, color="#d4d4d4", font_size=10, anchor="start")
fig.annotate(text, xy, xytext=None, color="#d4d4d4", font_size=9, arrow_color="#707070")
```

### Configuration Methods

```python
fig.set_title("Chart Title")
fig.set_subtitle("Subtitle text")
fig.set_xticks(["Q1", "Q2", "Q3", "Q4"])  # string or numeric
fig.set_yticks([0, 25, 50, 75, 100])
fig.grid(True)
fig.legend()
```

### Output

```python
fig.show()           # Display inline in Jupyter/Colab
svg = fig.render()   # Get SVG string
fig                  # Auto-renders in Jupyter (via _repr_html_)
```

---

## TypeScript API Reference

### Figure/Axes API (matplotlib-like)

```typescript
import { figure } from "./lib/plot";

const fig = figure();
fig.set_size(800, 400);

const ax = fig.subplot(nrows, ncols, index);

ax.plot(yData, options?)           // Line chart
ax.bar(xLabels, yData, options?)   // Bar chart
ax.scatter(xData, yData, options?) // Scatter plot
ax.hist(data, options?)            // Histogram
ax.fill_between(xData, y1, y2, options?) // Area fill

ax.axhline(y, options?)            // Horizontal reference
ax.axvline(x, options?)            // Vertical reference
ax.text(x, y, content, options?)   // Text annotation
ax.annotate(text, xy, options?)    // Annotation with arrow

ax.set_title("Title")
ax.set_subtitle("Subtitle")
ax.set_xticks(labels)
ax.set_yticks(values)
ax.set_xscale("log")              // "linear" | "log"
ax.set_yscale("log")
ax.set_xlim(min, max)
ax.set_ylim(min, max)
ax.grid(true)
ax.legend()

const scene = fig.render();        // → Scene graph
```

### React Components

```tsx
import { FlashChart, PieChart, Surface3D } from "./lib/plot";

<FlashChart scene={scene} />

<PieChart
  data={[
    { label: "Equities", value: 60, color: "#4aaaba" },
    { label: "Bonds", value: 30, color: "#d8b4fe" },
    { label: "Cash", value: 10, color: "#fbbf24" },
  ]}
  donut={true}
  donutRatio={0.55}
  showLegend={true}
/>

<Surface3D z={zMatrix} wireframe={true} />
```

### ChartSpec Rendering (declarative)

```typescript
import { renderChart } from "./lib/plot";

const scene = renderChart(chartSpec);  // ChartSpec → Scene
```

---

## MCP Server (AI Agent Integration)

The charting engine runs as an MCP (Model Context Protocol) server, exposing 3 tools for AI agents. Uses stdio transport for Claude Code integration.

### Starting the MCP Server

```bash
npx tsx src/mcp/server.ts
```

### `.mcp.json` Configuration

```json
{
  "mcpServers": {
    "flash-plot": {
      "type": "stdio",
      "command": "npx",
      "args": ["tsx", "src/mcp/server.ts"]
    }
  }
}
```

---

### Tool: `chart_render`

Renders a chart from a ChartSpec JSON object. Returns a Scene graph (for interactive React rendering) or SVG string (for static display).

**Input Schema:**

```json
{
  "spec": {
    "type": "line",
    "title": "Strategy Returns",
    "subtitle": "Cumulative performance",
    "series": [
      {
        "data": [0, 5, 12, 8, 18, 25],
        "label": "Strategy",
        "color": "#d4d4d4"
      }
    ],
    "xLabels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "grid": true
  },
  "format": "scene"
}
```

**Input Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `spec` | `ChartSpec` | Yes | Full chart specification (see [ChartSpec Schema](#chartspec-json-schema)) |
| `format` | `"scene"` \| `"svg"` | No | Output format. Default: `"scene"` |

**Output:**

```json
{
  "componentHint": "FlashChart",
  "chartType": "line",
  "scene": { ... },
  "svg": "<svg>...</svg>"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `componentHint` | `"FlashChart"` \| `"PieChart"` \| `"Surface3D"` | Which React component to use |
| `chartType` | `string` | The resolved chart type |
| `scene` | `Scene` | Scene graph for FlashChart (standard charts) |
| `pieData` | `{ slices, donut, donutRatio }` | Data for PieChart (pie/donut types) |
| `surfaceData` | `{ z, x, y, wireframe }` | Data for Surface3D (surface types) |
| `svg` | `string` | SVG string (only when `format: "svg"`) |

**Component routing:**

| Chart Type | componentHint | Data Field |
|-----------|---------------|------------|
| `line`, `bar`, `stacked_bar`, `scatter`, `area`, `histogram`, `candlestick`, `waterfall`, `violin`, `boxplot`, `heatmap`, `bubble` | `FlashChart` | `scene` |
| `pie`, `donut` | `PieChart` | `pieData` |
| `surface`, `surface_3d` | `Surface3D` | `surfaceData` |

---

### Tool: `chart_resolve_type`

Given a natural language description of data, recommends the best chart type with alternatives and an example spec.

**Input Schema:**

```json
{
  "description": "I have monthly revenue data for 3 product lines over 2 years",
  "columns": ["month", "product_a", "product_b", "product_c"]
}
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `description` | `string` | Yes | Natural language description of data and visualization goal |
| `columns` | `string[]` | No | Column/field names in the dataset |

**Output:**

```json
{
  "recommendedType": "line",
  "alternatives": ["bar", "area", "stacked_bar"],
  "reasoning": "Time series data with multiple series suggests a line chart for trend comparison. Bar chart works for period-by-period comparison.",
  "exampleSpec": {
    "type": "line",
    "series": [
      { "data": [], "label": "product_a" },
      { "data": [], "label": "product_b" },
      { "data": [], "label": "product_c" }
    ],
    "xLabels": [],
    "grid": true
  }
}
```

**Detection rules (in priority order):**

| Keywords Detected | Recommended Type |
|-------------------|-----------------|
| open, high, low, close, ohlc, candlestick | `candlestick` |
| surface, 3d, terrain, mesh | `surface_3d` |
| correlation, heatmap, matrix, covariance | `heatmap` |
| proportion, allocation, composition, weight, breakdown | `pie` |
| waterfall, cumulative, bridge, flow, contribution | `waterfall` |
| distribution, frequency, histogram, density | `histogram` |
| scatter, relationship, regression, cluster | `scatter` |
| comparison, compare, versus, category, sector | `bar` |
| date, time, year, month, quarter, period | `line` |
| *(fallback)* | `line` |

---

### Tool: `chart_get_styles`

Returns the complete theme definition, available color palettes, and the full chart type catalog. No input required.

**Output:**

```json
{
  "theme": {
    "name": "flash-dark",
    "background": "#121212",
    "surface": "#0f0f0f",
    "text": {
      "primary": "#ffffff",
      "secondary": "#8f8f8f",
      "muted": "#494949",
      "axis": "#494949"
    },
    "grid": { "color": "rgba(255,255,255,0.06)", "width": 0.5 },
    "axis": { "fontFamily": "'Inter', sans-serif", "fontSize": 8, "fontWeight": 500 },
    "title": { "fontFamily": "'EB Garamond', Georgia, serif", "fontSize": 14, "fontWeight": 500 },
    "subtitle": { "fontFamily": "'Inter', sans-serif", "fontSize": 10 },
    "defaultColors": ["#d4d4d4", "#707070", "#4ECDC4", "#FFD93D", "#FF6B6B", "#C084FC", "#67E8F9"],
    "bar": {
      "defaultFill": "#0f0f0f",
      "styles": [
        { "fill": "#4aaaba", "sideGlow": "rgba(78,205,196,0.25)", "topGlow": "rgba(255,255,255,0.35)", "sparkle": "rgba(78,205,196,0.85)" },
        { "fill": "#d8b4fe", "..." : "..." },
        "..."
      ]
    }
  },
  "availableThemes": ["flash-dark"],
  "palettes": {
    "line": ["#d4d4d4", "#707070", "#4ECDC4", "#FFD93D", "#FF6B6B", "#C084FC", "#67E8F9", "#FCA5A5"],
    "bar": ["#EF8CFF", "#8CA5FF", "#4ECDC4", "#FFD93D", "#FF6B6B", "#C084FC"],
    "scatter": ["#4ECDC4", "#FFD93D", "#FF6B6B", "#C084FC", "#67E8F9", "#d4d4d4"],
    "area": ["#4ECDC4", "#C084FC", "#FFD93D", "#FF6B6B", "#67E8F9", "#d4d4d4"],
    "pie": ["#4aaaba", "#d8b4fe", "#fbbf24", "#f9a8d4", "#6dd5c8", "#a5f3d8", "#C084FC", "#FF6B6B", "#67E8F9", "#FFD93D"],
    "histogram": ["#C084FC", "#4ECDC4", "#FFD93D"],
    "candlestick": ["#4ECDC4", "#FF6B6B"],
    "waterfall": ["#4ECDC4", "#FF6B6B", "#8CA5FF"],
    "heatmap": ["#0d1117", "#4aaaba", "#fbbf24", "#ff6b6b"],
    "violin": ["#C084FC", "#4ECDC4", "#FFD93D", "#FF6B6B", "#67E8F9", "#8CA5FF"],
    "surface": ["#C084FC"]
  },
  "chartTypes": [
    { "type": "line", "description": "Time series, trends, multi-line comparison" },
    { "type": "bar", "description": "Categorical comparison, grouped bars" },
    { "type": "stacked_bar", "description": "Composition over categories" },
    { "type": "scatter", "description": "Correlation, clusters, variable relationships" },
    { "type": "bubble", "description": "Scatter with variable-size points" },
    { "type": "area", "description": "Cumulative values, filled line chart" },
    { "type": "histogram", "description": "Frequency distribution" },
    { "type": "pie", "description": "Proportional breakdown" },
    { "type": "donut", "description": "Pie with center cutout" },
    { "type": "surface_3d", "description": "3D surface plot (volatility surfaces, terrain)" },
    { "type": "candlestick", "description": "OHLC price action" },
    { "type": "heatmap", "description": "2D grid visualization (correlations)" },
    { "type": "waterfall", "description": "Cumulative contribution breakdown" },
    { "type": "violin", "description": "Distribution shape comparison" },
    { "type": "boxplot", "description": "Statistical summary with quartiles" }
  ]
}
```

---

## ChartSpec JSON Schema

The `ChartSpec` is the primary input format for the rendering engine (used by MCP, HTTP API, and `renderChart()`).

### Full Schema

```typescript
interface ChartSpec {
  // Required
  type: "line" | "bar" | "stacked_bar" | "scatter" | "bubble" | "area"
      | "histogram" | "pie" | "donut" | "surface_3d" | "candlestick"
      | "heatmap" | "waterfall" | "violin" | "boxplot";

  // Metadata
  title?: string;
  subtitle?: string;

  // Data — standard charts
  series?: SeriesSpec[];

  // Data — pie/donut
  slices?: PieSliceSpec[];
  donutRatio?: number;              // 0–1, default 0.55

  // Data — surface
  surface?: SurfaceSpec;

  // Data — heatmap
  heatmap?: HeatmapSpec;

  // Histogram config
  bins?: number;                     // default 10

  // Axes
  xLabels?: string[];                // categorical x-axis labels
  xAxis?: AxisSpec;
  yAxis?: AxisSpec;

  // Display
  legend?: LegendSpec;
  grid?: boolean;
  width?: number;                    // default 595
  height?: number;                   // default 260

  // Overlays
  hlines?: { y: number; color?: string; label?: string; lineStyle?: "solid" | "dashed" }[];
  vlines?: { x: number; color?: string; label?: string; lineStyle?: "solid" | "dashed" }[];
  annotations?: { text: string; x: number; y: number; color?: string }[];
}
```

### SeriesSpec

```typescript
interface SeriesSpec {
  data: number[];                    // Y values (required)
  x?: number[];                      // X values (for scatter, numeric axes)
  label?: string;                    // Legend label
  color?: string;                    // Hex color (auto-assigned if omitted)
  lineWidth?: number;                // default 1.5
  lineStyle?: "solid" | "dashed" | "dotted" | "dashdot";
  fillOpacity?: number;              // Fill area under line (0–1)
  barWidth?: number;                 // Override bar width
  stacked?: boolean;                 // Stack with other series
  markerSize?: number;               // Scatter point size
  sizes?: number[];                  // Per-point sizes (bubble chart)

  // Candlestick OHLC
  open?: number[];
  high?: number[];
  low?: number[];
  close?: number[];

  // Boxplot
  q1?: number;
  median?: number;
  q3?: number;
  whiskerLow?: number;
  whiskerHigh?: number;
  outliers?: number[];
}
```

### PieSliceSpec

```typescript
interface PieSliceSpec {
  value: number;
  label: string;
  color?: string;                    // Auto-assigned from pie palette if omitted
}
```

### SurfaceSpec

```typescript
interface SurfaceSpec {
  z: number[][];                     // 2D height matrix (required)
  x?: number[][];                    // Optional X coordinates
  y?: number[][];                    // Optional Y coordinates
  color?: string;
  wireframe?: boolean;               // default true
  azimuth?: number;                  // Viewing angle
  elevation?: number;                // Viewing angle
}
```

### HeatmapSpec

```typescript
interface HeatmapSpec {
  data: number[][];                  // 2D value matrix
  rowLabels?: string[];
  colLabels?: string[];
  colorRange?: [string, string];     // [low, high] colors
}
```

### AxisSpec

```typescript
interface AxisSpec {
  label?: string;
  min?: number;
  max?: number;
  scale?: "linear" | "log";
  ticks?: number[];
  tickLabels?: string[];
}
```

### LegendSpec

```typescript
interface LegendSpec {
  show?: boolean;
  position?: "top" | "bottom" | "left" | "right";
}
```

---

### ChartSpec Examples

#### Line Chart

```json
{
  "type": "line",
  "title": "Strategy vs Benchmark",
  "subtitle": "Cumulative returns (%)",
  "series": [
    { "data": [0, 5, 12, 8, 18, 25, 20, 32], "label": "Strategy", "color": "#d4d4d4" },
    { "data": [0, 3, 6, 5, 9, 12, 11, 15], "label": "Benchmark", "color": "#707070" }
  ],
  "xLabels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
  "grid": true
}
```

#### Grouped Bar Chart

```json
{
  "type": "bar",
  "title": "Sector Allocation",
  "series": [
    { "data": [28, 18, 15, 12], "label": "Current" },
    { "data": [22, 20, 18, 10], "label": "Target" }
  ],
  "xLabels": ["Tech", "Health", "Finance", "Energy"],
  "grid": true
}
```

#### Scatter Plot

```json
{
  "type": "scatter",
  "title": "Risk vs Return",
  "series": [
    { "data": [8, 12, 6, 15, 10], "x": [5, 8, 3, 12, 7], "label": "Funds", "color": "#4ECDC4", "markerSize": 6 }
  ],
  "xAxis": { "label": "Volatility (%)" },
  "yAxis": { "label": "Return (%)" },
  "grid": true
}
```

#### Histogram

```json
{
  "type": "histogram",
  "title": "Return Distribution",
  "series": [
    { "data": [-3, -2.5, -1, 0, 0.5, 1, 1.5, 2, -0.3, 0.8, 1.2, -0.7], "label": "Returns" }
  ],
  "bins": 15
}
```

#### Pie / Donut

```json
{
  "type": "donut",
  "title": "Portfolio Allocation",
  "slices": [
    { "label": "Equities", "value": 60 },
    { "label": "Bonds", "value": 25 },
    { "label": "Cash", "value": 15 }
  ],
  "donutRatio": 0.55
}
```

#### Candlestick

```json
{
  "type": "candlestick",
  "title": "NVDA Price Action",
  "series": [{
    "data": [130, 135, 128, 140],
    "open": [125, 130, 136, 127],
    "high": [132, 137, 138, 142],
    "low": [123, 128, 126, 125],
    "close": [130, 135, 128, 140]
  }],
  "xLabels": ["Mon", "Tue", "Wed", "Thu"]
}
```

#### Surface 3D

```json
{
  "type": "surface_3d",
  "title": "Volatility Surface",
  "surface": {
    "z": [[0.3, 0.25, 0.22], [0.25, 0.21, 0.18], [0.22, 0.18, 0.16]],
    "wireframe": true
  }
}
```

#### Area with Fill Between

```json
{
  "type": "area",
  "title": "AUM Growth",
  "series": [
    { "data": [100, 120, 140, 160, 180, 200], "label": "AUM", "color": "#C084FC", "fillOpacity": 0.15 }
  ],
  "xLabels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  "grid": true
}
```

#### With Reference Lines & Annotations

```json
{
  "type": "line",
  "title": "Price with Levels",
  "series": [{ "data": [100, 105, 98, 110, 115, 108, 120] }],
  "hlines": [
    { "y": 110, "color": "#FF6B6B", "lineStyle": "dashed" },
    { "y": 100, "color": "#4ECDC4", "lineStyle": "dashed" }
  ],
  "annotations": [
    { "text": "Resistance", "x": 5, "y": 112, "color": "#FF6B6B" },
    { "text": "Support", "x": 5, "y": 97, "color": "#4ECDC4" }
  ],
  "grid": true
}
```

---

## HTTP API

### POST `/api/chart` — Command-based rendering

Accepts a sequence of matplotlib-like commands, returns SVG.

**Request:**

```json
{
  "commands": [
    { "method": "set_title", "args": ["Monthly Returns"] },
    { "method": "plot", "args": [[12, -5, 18, 8, 25]], "kwargs": { "color": "#d4d4d4", "label": "Returns" } },
    { "method": "bar", "args": [["Jan", "Feb", "Mar", "Apr", "May"], [12, -5, 18, 8, 25]], "kwargs": { "label": "PnL" } },
    { "method": "axhline", "args": [0], "kwargs": { "color": "#555", "linestyle": "dashed" } },
    { "method": "grid", "args": [true] },
    { "method": "legend" }
  ],
  "width": 595,
  "height": 280
}
```

**Supported commands:** `plot`, `bar`, `scatter`, `hist`, `fill_between`, `axhline`, `axvline`, `text`, `annotate`, `set_title`, `set_subtitle`, `set_xticks`, `set_yticks`, `grid`, `legend`

**Response:** `image/svg+xml`

### POST `/api/chart/render` — ChartSpec rendering

Accepts a ChartSpec, returns Scene JSON or SVG.

**Request:**

```json
{
  "spec": {
    "type": "bar",
    "title": "Sector Weights",
    "series": [{ "data": [28, 18, 15, 12], "label": "Weight %" }],
    "xLabels": ["Tech", "Health", "Finance", "Energy"],
    "grid": true
  },
  "format": "scene"
}
```

**Response (scene format):**

```json
{
  "componentHint": "FlashChart",
  "chartType": "bar",
  "scene": {
    "width": 595,
    "height": 260,
    "theme": "flash-dark",
    "subplots": [{ "plotArea": {...}, "elements": [...], "xAxis": {...}, "yAxis": {...}, ... }]
  }
}
```

**Response (svg format):**

```json
{
  "componentHint": "FlashChart",
  "chartType": "bar",
  "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" ...>...</svg>"
}
```

Both endpoints have CORS enabled for all origins.

---

## Scene Graph Output

The `renderChart()` function and MCP `chart_render` tool produce a Scene graph — a complete description of the chart ready for rendering.

```typescript
interface Scene {
  width: number;
  height: number;
  theme: string;
  subplots: SubplotScene[];
}

interface SubplotScene {
  row: number;
  col: number;
  bounds: Rect;                      // { x, y, w, h }
  plotArea: Rect;                    // Inner data area
  title?: string;
  subtitle?: string;
  titleStyle?: TextStyle;
  subtitleStyle?: TextStyle;
  xAxis: AxisScene;
  yAxis: AxisScene;
  grid: GridScene;
  elements: PlotElement[];           // Renderable chart elements
  legend?: LegendScene;
}
```

**Plot elements** (discriminated union on `type`):

| Type | Key Fields |
|------|------------|
| `line` | `path`, `points[]`, `color`, `lineWidth`, `lineStyle`, `dataValues[]` |
| `area` | `path`, `points[]`, `color`, `alpha` |
| `bar` | `bars[]` (each: `x`, `y`, `width`, `height`, `value`, `index`), `seriesIndex`, `xLabels[]` |
| `scatter` | `points[]` (each: `x`, `y`, `size`, `color`), `alpha` |
| `hline` | `y`, `xMin`, `xMax`, `color`, `lineWidth`, `lineStyle` |
| `vline` | `x`, `yMin`, `yMax`, `color`, `lineWidth`, `lineStyle` |
| `text` | `x`, `y`, `content`, `style`, `anchor`, `rotation?` |
| `annotation` | `text`, `xy`, `xytext?`, `style`, `arrowColor?` |

---

## Architecture

```
ChartingEngine/
├── core/                        # Framework-agnostic engine (2,500 LOC)
│   ├── figure.ts                #   Figure & Axes — matplotlib-like API
│   ├── renderChart.ts           #   ChartSpec → Scene converter
│   ├── types.ts                 #   All TypeScript type definitions
│   ├── theme.ts                 #   Flash Dark theme, bar glow styles
│   ├── scales.ts                #   Linear/log scales, tick computation
│   ├── layout.ts                #   Plot area & subplot grid layout
│   ├── paths.ts                 #   SVG path builders (line, area, bar, scatter, histogram)
│   └── index.ts                 #   Re-exports
│
├── react/                       # React renderer (2,000 LOC)
│   ├── FlashChart.tsx           #   Main animated SVG chart component
│   ├── PieChart.tsx             #   Pie/donut with gradient arcs
│   ├── Surface3D.tsx            #   WebGL 3D surface (Three.js)
│   ├── useAnimation.ts          #   Animation phase hook
│   └── index.ts                 #   Re-exports
│
├── server/                      # Server-side rendering (200 LOC)
│   ├── renderSvg.ts             #   Scene → static SVG string (no React/DOM)
│   └── index.ts
│
├── src/mcp/                     # MCP server for AI agents
│   ├── server.ts                #   stdio server with 3 tools
│   └── tools/
│       ├── chartRender.ts       #   chart_render tool implementation
│       ├── chartResolve.ts      #   chart_resolve_type tool implementation
│       └── chartStyles.ts       #   chart_get_styles tool implementation
│
├── src/app/api/chart/           # HTTP API endpoints
│   ├── route.ts                 #   POST /api/chart (command-based → SVG)
│   └── render/route.ts          #   POST /api/chart/render (ChartSpec → Scene/SVG)
│
├── src/app/test2/               # Interactive test playground
│   └── page.tsx                 #   JSON editor + live chart preview
│
├── python/                      # Pure Python package
│   ├── flash_plot/
│   │   ├── __init__.py
│   │   └── engine.py            #   FlashPlot class — renders SVG locally
│   └── setup.py
│
└── notebooks/
    └── flash_plot_demo.ipynb    #   7 chart demos for Colab/Jupyter
```

### Data Flow

```
Python:  FlashPlot API → SVG string → IPython.display.HTML

TypeScript (Figure API):
  figure() → Axes commands → fig.render() → Scene graph → <FlashChart scene={} />

TypeScript (ChartSpec):
  ChartSpec JSON → renderChart() → Scene graph → <FlashChart scene={} />

MCP:
  Agent → chart_render(spec) → Scene JSON → Agent passes to frontend → <FlashChart />

HTTP API:
  POST /api/chart/render → executeChartRender() → Scene JSON / SVG
  POST /api/chart        → Figure/Axes commands → renderSceneToSvg() → SVG
```

---

## Theme & Color Palettes

### Flash Dark Theme

| Token | Value | Usage |
|-------|-------|-------|
| Background | `#121212` | Chart background |
| Surface | `#0f0f0f` | Bar default fill |
| Text Primary | `#ffffff` | Titles |
| Text Secondary | `#8f8f8f` | Legend labels |
| Text Muted | `#494949` | Axis labels, subtitles |
| Grid | `rgba(255,255,255,0.06)` | Grid lines |

### Default Color Palettes (per chart type)

| Chart Type | Colors |
|-----------|--------|
| Line | `#d4d4d4` `#707070` `#4ECDC4` `#FFD93D` `#FF6B6B` `#C084FC` `#67E8F9` `#FCA5A5` |
| Bar | `#EF8CFF` `#8CA5FF` `#4ECDC4` `#FFD93D` `#FF6B6B` `#C084FC` |
| Scatter | `#4ECDC4` `#FFD93D` `#FF6B6B` `#C084FC` `#67E8F9` `#d4d4d4` |
| Area | `#4ECDC4` `#C084FC` `#FFD93D` `#FF6B6B` `#67E8F9` `#d4d4d4` |
| Pie | `#4aaaba` `#d8b4fe` `#fbbf24` `#f9a8d4` `#6dd5c8` `#a5f3d8` `#C084FC` `#FF6B6B` `#67E8F9` `#FFD93D` |
| Histogram | `#C084FC` `#4ECDC4` `#FFD93D` |
| Candlestick | `#4ECDC4` (up) `#FF6B6B` (down) |
| Waterfall | `#4ECDC4` (positive) `#FF6B6B` (negative) `#8CA5FF` (total) |
| Heatmap | `#0d1117` → `#4aaaba` → `#fbbf24` → `#ff6b6b` |

### Bar Glow Styles

Each bar series has a unique multi-layer glow effect with 5 layers: side glow, top highlight, bottom glow, left edge, and sparkle dots.

| Series | Fill | Glow Style |
|--------|------|------------|
| 1 | `#4aaaba` | Teal glow |
| 2 | `#d8b4fe` | Purple glow |
| 3 | `#fbbf24` | Gold glow |
| 4 | `#f9a8d4` | Pink glow |
| 5 | `#6dd5c8` | Mint glow |

---

## Animation System

The React `<FlashChart>` component includes a multi-phase CSS keyframe animation system:

| Phase | Timing | Elements |
|-------|--------|----------|
| 1. Grid Draw | 0–0.675s | Grid lines draw in sequentially with `stroke-dashoffset` |
| 2. Labels | 0.675s+ | Y-axis labels slide in, X-axis labels fade up |
| 3. Data | 1.28s+ | Lines draw, bars grow (scaleY), areas fade, scatter pops |
| 4. Shimmer | 2.5s+ | Axis labels get a brightness wave sweep |
| 5. Bar Sweep | After bars | Sequential highlight pulse across bars |
| 6. Glow Reveal | After sweep | Bar glow layers fade in with drift + sparkle animations |

All animations trigger on viewport intersection (IntersectionObserver with 15% threshold).

---

## Requirements

### Python
- Python 3.8+
- No external dependencies
- Optional: `numpy` (arrays auto-converted), `ipython` (for `display()`)

### TypeScript
- Node.js 18+
- Next.js 16+
- React 19+
- Dependencies: `@modelcontextprotocol/sdk` (MCP server only)

---

## License

MIT
