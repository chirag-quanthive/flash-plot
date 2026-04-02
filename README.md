# Flash Plot -- Charting Engine

Premium dark-themed charting engine powering Flash 2.0. Renders animated SVG charts with multi-layer bar glow effects, sparkle animations, and a financial-grade dark theme.

Available as a **TypeScript/React** library (with MCP + HTTP API) and a **pure Python** package for Google Colab / Jupyter. Both produce visually identical output.

---

## Quick Start

### TypeScript (Next.js)

```bash
git clone https://github.com/quant-hive/ChartingEngine.git
cd ChartingEngine
npm install
npm run dev
# Open http://localhost:3000/test2
```

### Python (Colab / Jupyter)

```bash
pip install git+https://github.com/quant-hive/ChartingEngine.git#subdirectory=python
```

```python
from flash_plot import FlashPlot

fig = FlashPlot()
fig.set_title("Cumulative Returns")
fig.set_subtitle("Strategy vs Benchmark")
fig.plot([0, 5, 12, 8, 18, 25], label="Strategy")
fig.plot([0, 3, 6, 4, 10, 14], label="Benchmark")
fig.grid(True)
fig.legend()
fig.show()
```

---

## Supported Chart Types

| Type | Description | Component |
|------|-------------|-----------|
| `line` | Time series and trends | FlashChart |
| `bar` | Categorical comparisons | FlashChart |
| `stacked_bar` | Part-of-whole across categories | FlashChart |
| `scatter` | Correlation between two variables | FlashChart |
| `bubble` | Scatter with variable-size markers | FlashChart |
| `area` | Filled line chart for volume/magnitude | FlashChart |
| `histogram` | Frequency distribution | FlashChart |
| `pie` | Proportional breakdown | PieChart |
| `donut` | Pie with hollow center | PieChart |
| `surface_3d` | Interactive 3D surface with rotation/zoom | Surface3D |
| `candlestick` | OHLC price data | FlashChart |
| `heatmap` | Color-mapped 2D grid | FlashChart |
| `waterfall` | Cumulative contributions | FlashChart |
| `violin` | Distribution shape (KDE) | FlashChart |
| `boxplot` | Quartile summary statistics | FlashChart |

---

## Architecture

```
ChartSpec JSON -----> renderChart() -----> Scene Graph -----> FlashChart (React/SVG)
                                                       |----> renderSceneToSvg() (static SVG)
                                                       |----> PieChart (pie/donut)
                                                       |----> Surface3D (3D surface)

Python FlashPlot -----> SVG string (Colab-compatible, visually identical)
```

### Data Flow

1. **Input**: `ChartSpec` JSON (from agent, API, or code)
2. **Processing**: `renderChart()` creates a Scene graph with computed layout, tick positions, element geometry
3. **Rendering**: Scene graph feeds into:
   - `FlashChart` -- React component with CSS animations, glow effects, tooltips, scrollable bars
   - `renderSceneToSvg()` -- Static SVG string for server-side rendering
   - Python `FlashPlot` -- Direct SVG rendering with identical visual output

### File Structure

```
src/
  lib/plot/
    core/
      figure.ts        # Figure/Axes classes (matplotlib-like API)
      renderChart.ts    # ChartSpec -> Scene graph (universal renderer)
      types.ts          # All TypeScript type definitions
      theme.ts          # FLASH_DARK theme (colors, fonts, sizes)
      layout.ts         # Layout computation (padding, plot area)
      scales.ts         # Axis scaling (linear, log, symlog)
      paths.ts          # SVG path builders
    react/
      FlashChart.tsx    # Main React renderer (animated SVG)
      PieChart.tsx      # Pie/donut component
      Surface3D.tsx     # Interactive 3D surface
      useAnimation.ts   # Animation hooks
    server/
      renderSvg.ts      # Scene -> static SVG string
  lib/
    chartEngine.tsx     # ChartCard, ChartHeader, ChartSettingsDropdown
    graphApi.ts         # Mock data API
  mcp/
    server.ts           # MCP server (stdio transport, 3 tools)
    tools/
      chartRender.ts    # chart_render tool implementation
      chartResolve.ts   # chart_resolve_type tool implementation
      chartStyles.ts    # chart_get_styles tool implementation
  app/
    api/chart/
      route.ts          # POST /api/chart (matplotlib commands -> SVG)
      render/route.ts   # POST /api/chart/render (ChartSpec -> Scene/SVG)
    test2/page.tsx      # Interactive MCP test playground
    test/page.tsx       # Matplotlib-style API demo (14 chart examples)
python/
  flash_plot/
    engine.py           # Pure Python SVG renderer (Colab-compatible)
    __init__.py
  setup.py
notebooks/
  flash_plot_demo.ipynb # 7 demo charts for Colab
```

---

## FLASH_DARK Theme

All values are defined in `src/lib/plot/core/theme.ts` and replicated exactly in `python/flash_plot/engine.py`.

| Token | Value |
|-------|-------|
| Background | `#121212` |
| Surface | `#0f0f0f` |
| Text primary | `#ffffff` |
| Text secondary | `#8f8f8f` |
| Text muted / axis | `#494949` |
| Grid color | `#2a2a2a` |
| Grid width | `0.3` |
| Title font | `'EB Garamond', 'Times New Roman', Georgia, serif` |
| Title size | `18px`, weight `400`, spacing `-0.2px` |
| Subtitle font | `'Inter', sans-serif` |
| Subtitle size | `11px`, weight `400`, spacing `-0.1px`, color `#555555` |
| Axis font | `'Inter', sans-serif` |
| Axis size | `10px`, weight `500`, spacing `-0.12px` |
| Legend font | `'Inter', sans-serif`, `11px` |
| Legend text color | `#8f8f8f` |

### Bar Glow Styles

Each bar series uses a themed style with gradient fill and multi-layer glow effects:

| Property | Series 0 (Pink) | Series 1 (Blue) |
|----------|-----------------|-----------------|
| Fill | `#EF8CFF` | `#8CA5FF` |
| Gradient top | `#e586fa` | `#86bafa` |
| Gradient bottom | `#884f94` | `#4f7194` |
| Side glow | `#624096` | `#405A96` |
| Top glow | `#763AA4` | `#3A5FA4` |
| Bottom glow | `#7B42DD` | `#427BDD` |
| Left edge | `#7432E6` | `#3268E6` |
| Sparkle | `#E49BFF` | `#9BB6FF` |
| Default fill (dark base) | `#1e1f24` | `#1e1f24` |

### Color Palettes by Chart Type

```json
{
  "line":      ["#d4d4d4", "#707070", "#4ECDC4", "#FFD93D", "#FF6B6B", "#C084FC", "#67E8F9", "#FCA5A5"],
  "bar":       ["#EF8CFF", "#8CA5FF", "#4ECDC4", "#FFD93D", "#FF6B6B", "#C084FC"],
  "scatter":   ["#4ECDC4", "#FFD93D", "#FF6B6B", "#C084FC", "#67E8F9", "#d4d4d4"],
  "area":      ["#4ECDC4", "#C084FC", "#FFD93D", "#FF6B6B", "#67E8F9", "#d4d4d4"],
  "histogram": ["#C084FC", "#4ECDC4", "#FFD93D"],
  "pie":       ["#4aaaba", "#d8b4fe", "#fbbf24", "#f9a8d4", "#6dd5c8", "#a5f3d8", "#C084FC", "#FF6B6B", "#67E8F9", "#FFD93D"]
}
```

### Layout Constants

```
Width: 595 (default)    Height: 260 (default)
Padding: { top: 4, right: 16, bottom: 28, left: 32 }
Inset: 16
Plot area: x = left + inset, y = top + inset, w = width - left - right - 2*inset, h = height - top - bottom - 2*inset
```

---

## Bar Glow Effect (Frontend)

The FlashChart React component renders bars with a 9-layer glow stack:

1. **Dark base rect** (`#1e1f24`) -- grows from bottom via `scaleY` animation
2. **Colored fill** (e.g. `#EF8CFF`) -- main bar color
3. **Side glow** -- curved SVG path along right edge, Gaussian blur (`sigma: 5`), CSS drift animation
4. **Top highlight** -- bright rectangle at top, blur (`sigma: 4`), drift animation
5. **Bottom glow** -- curved path at base, blur (`sigma: 5`), drift animation
6. **Left edge** -- thin edge highlight, blur (`sigma: 5`), drift animation
7. **Sparkle dots** -- 15 positioned dots with float animation (3 patterns, staggered)
8. **Bottom white** -- white wedge at base, blur (`sigma: 2.25`)
9. **Top white** -- white wedge at top, blur (`sigma: 2.25`)

All layers are clipped to bar bounds via nested `<svg>` viewport. Animations use CSS `@keyframes` for drift, float, and reveal sequences.

### Bar Glow Effect (Python/Colab)

Since Colab's HTML sanitizer strips `<style>` and `<filter>` elements, the Python engine simulates the glow using gradient layers:

1. **Dark base rect** (`#1e1f24`)
2. **Main gradient** (gradTop -> gradBottom via `<linearGradient>`)
3. **Side glow gradient** (sideGlow color fading left-to-right)
4. **Left edge highlight** (thin gradient strip)
5. **Top highlight gradient** (topGlow fading downward)
6. **Bottom glow gradient** (bottomGlow fading upward)
7. **White top edge** (white rect, `opacity: 0.15`)
8. **White bottom edge** (white rect, `opacity: 0.12`)
9. **Sparkle dots** (static circles with sparkle color, `opacity: 0.85`)

All layers are clipped via nested `<svg>` viewport, identical to the frontend approach.

---

## Animation System (Frontend)

Charts animate in 4 phases when they enter the viewport (IntersectionObserver):

| Phase | Timing | Elements |
|-------|--------|----------|
| 1. Grid draw-in | `0s` | Grid lines draw from left via `stroke-dashoffset` |
| 2. Label appear | `0.675s` | Y-axis labels slide in, X-axis labels rise up |
| 3. Data reveal | `1.28s` | Lines draw in, bars grow from bottom, scatter pops, areas fade |
| 4. Shimmer | `2.5s` | Axis labels flash bright then settle, bar glow layers fade in |

### Timing Constants

```
T_LABELS   = 0.675s    (label fade-in start)
T_DATA     = 1.28s     (data element start)
T_SHIMMER  = 2.5s      (shimmer wave start)
SHIMMER_STEP = 0.08s   (delay between labels)
SHIMMER_DUR  = 0.24s   (shimmer duration per label)
Bar grow     = 0.81s   (cubic-bezier 0.22, 1, 0.36, 1)
Line draw    = 1.89s   (cubic-bezier 0.22, 1, 0.36, 1)
Bar stagger  = 0.054s  (per bar index)
```

---

## MCP Server

The MCP server exposes 3 tools over stdio transport for AI agent integration.

### Setup

Add to `.mcp.json`:

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

Or run directly:

```bash
npx tsx src/mcp/server.ts
```

---

### Tool: `chart_render`

Render a chart from a ChartSpec JSON. Returns a Scene graph for the frontend, plus optional SVG.

**Input Schema:**

```json
{
  "spec": {
    "type": "line | bar | stacked_bar | scatter | bubble | area | histogram | pie | donut | surface_3d | candlestick | heatmap | waterfall | violin | boxplot",
    "title": "string (optional)",
    "subtitle": "string (optional)",
    "series": [
      {
        "data": [1, 2, 3],
        "x": [0, 1, 2],
        "label": "string (optional)",
        "color": "#hex (optional)",
        "lineWidth": 1.5,
        "lineStyle": "solid | dashed | dotted | dashdot",
        "fillOpacity": 0.15,
        "barWidth": 18,
        "stacked": false,
        "markerSize": 4,
        "sizes": [10, 20, 30],
        "open": [], "high": [], "low": [], "close": [],
        "q1": 0, "median": 0, "q3": 0,
        "whiskerLow": 0, "whiskerHigh": 0, "outliers": []
      }
    ],
    "slices": [
      { "value": 30, "label": "Tech", "color": "#hex (optional)" }
    ],
    "donutRatio": 0.55,
    "surface": {
      "z": [[1, 2], [3, 4]],
      "x": [],
      "y": [],
      "color": "#C084FC",
      "wireframe": true
    },
    "heatmap": {
      "data": [[1, 2], [3, 4]],
      "rowLabels": ["A", "B"],
      "colLabels": ["X", "Y"],
      "colorRange": ["#0d1117", "#ff6b6b"]
    },
    "bins": 10,
    "xLabels": ["Jan", "Feb", "Mar"],
    "xAxis": { "label": "", "min": 0, "max": 100, "scale": "linear | log | symlog" },
    "yAxis": { "label": "", "min": 0, "max": 100, "scale": "linear | log | symlog" },
    "legend": { "show": true, "position": "best | upper-left | upper-right | lower-left | lower-right" },
    "grid": true,
    "width": 595,
    "height": 260,
    "hlines": [{ "y": 0, "color": "#494949", "label": "", "lineStyle": "solid | dashed" }],
    "vlines": [{ "x": 0, "color": "#494949", "label": "", "lineStyle": "solid | dashed" }],
    "annotations": [{ "text": "Note", "x": 100, "y": 50, "color": "#808080" }]
  },
  "format": "scene | svg"
}
```

**Output:**

```json
{
  "componentHint": "FlashChart | PieChart | Surface3D",
  "chartType": "line",
  "scene": { "...Scene graph JSON..." },
  "pieData": { "slices": [...], "donut": false, "donutRatio": 0.55 },
  "surfaceData": { "z": [[]], "wireframe": true },
  "svg": "<svg>...</svg>"
}
```

The `componentHint` tells the frontend which React component to use:
- `"FlashChart"` -- standard chart types (line, bar, scatter, area, histogram, candlestick, waterfall, violin, boxplot)
- `"PieChart"` -- pie and donut charts
- `"Surface3D"` -- 3D surface plots

---

### Tool: `chart_resolve_type`

Given a natural language description of data, recommend the best chart type.

**Input Schema:**

```json
{
  "description": "monthly revenue by product category over the last year",
  "columns": ["month", "product", "revenue", "units_sold"]
}
```

**Output:**

```json
{
  "recommendedType": "bar",
  "alternatives": ["stacked_bar", "line"],
  "reasoning": "Categorical comparison -- bar chart shows values across categories.",
  "exampleSpec": {
    "type": "bar",
    "title": "Comparison",
    "series": [{ "data": [], "label": "Series" }],
    "xLabels": []
  }
}
```

**Resolution rules:**
- OHLC columns (open/high/low/close) -> `candlestick`
- 3D/surface keywords -> `surface_3d`
- Correlation/matrix -> `heatmap`
- Proportion/allocation -> `pie`
- Waterfall/flow -> `waterfall`
- Distribution/histogram -> `histogram`
- Scatter/relationship -> `scatter`
- Comparison/category -> `bar`
- Time series -> `line`
- Default -> `line`

---

### Tool: `chart_get_styles`

Returns the current theme, color palettes, and chart type catalog. No input required.

**Output:**

```json
{
  "theme": {
    "name": "flash-dark",
    "background": "#121212",
    "text": { "primary": "#ffffff", "secondary": "#8f8f8f", "muted": "#494949", "axis": "#494949" },
    "grid": { "color": "#2a2a2a", "width": 0.3 },
    "axis": { "fontFamily": "'Inter', sans-serif", "fontSize": 10, "fontWeight": 500 },
    "title": { "fontFamily": "'EB Garamond'...", "fontSize": 18, "fontWeight": 400, "color": "#ffffff" },
    "subtitle": { "fontFamily": "'Inter', sans-serif", "fontSize": 11, "color": "#555555" },
    "bar": {
      "defaultFill": "#1e1f24",
      "styles": [
        { "fill": "#EF8CFF", "gradTop": "#e586fa", "gradBottom": "#884f94", "sideGlow": "#624096", "topGlow": "#763AA4", "bottomGlow": "#7B42DD", "leftEdge": "#7432E6", "sparkle": "#E49BFF" },
        { "fill": "#8CA5FF", "gradTop": "#86bafa", "gradBottom": "#4f7194", "sideGlow": "#405A96", "topGlow": "#3A5FA4", "bottomGlow": "#427BDD", "leftEdge": "#3268E6", "sparkle": "#9BB6FF" }
      ]
    }
  },
  "availableThemes": ["flash-dark"],
  "palettes": { "line": [...], "bar": [...], "scatter": [...], "area": [...], "histogram": [...], "pie": [...] },
  "chartTypes": [
    { "type": "line", "description": "Line chart for time series and trends" },
    { "type": "bar", "description": "Bar chart for categorical comparisons" },
    "...15 types total..."
  ]
}
```

---

## HTTP API

### POST `/api/chart/render`

Accepts a ChartSpec JSON body, returns Scene JSON or SVG. Same as the `chart_render` MCP tool but over HTTP.

```bash
curl -X POST http://localhost:3000/api/chart/render \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "type": "line",
      "title": "Returns",
      "series": [{ "data": [0, 5, 12, 8, 18], "label": "Strategy" }],
      "grid": true
    },
    "format": "scene"
  }'
```

### POST `/api/chart`

Accepts matplotlib-style commands, returns SVG string.

```bash
curl -X POST http://localhost:3000/api/chart \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      { "method": "plot", "args": [[1, 5, 12, 8, 18]], "kwargs": { "label": "Returns" } },
      { "method": "set_title", "args": ["Strategy Returns"] },
      { "method": "grid", "args": [true] },
      { "method": "legend" }
    ]
  }'
```

---

## ChartSpec Examples

### Line Chart

```json
{
  "type": "line",
  "title": "Cumulative Returns",
  "subtitle": "Strategy vs Benchmark",
  "series": [
    { "data": [0, 5, 12, 8, 18, 25, 22, 30], "label": "Strategy", "color": "#d4d4d4" },
    { "data": [0, 3, 6, 4, 10, 14, 12, 18], "label": "Benchmark", "color": "#707070" }
  ],
  "xLabels": ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
  "grid": true
}
```

### Grouped Bar Chart

```json
{
  "type": "bar",
  "title": "Sector Allocation",
  "subtitle": "Portfolio weight (%)",
  "series": [
    { "data": [28, 18, 15, 12, 14, 13], "label": "Current" },
    { "data": [22, 20, 18, 10, 16, 14], "label": "Target" }
  ],
  "xLabels": ["Tech", "Health", "Finance", "Energy", "Consumer", "Industrial"],
  "grid": true
}
```

### Scatter Plot

```json
{
  "type": "scatter",
  "title": "Risk vs Return",
  "series": [
    { "data": [8, 12, 5, 15, 3, 10], "x": [5, 10, 3, 12, 2, 8], "label": "Funds", "markerSize": 6 }
  ],
  "hlines": [{ "y": 0, "lineStyle": "dashed" }],
  "grid": true
}
```

### Pie Chart

```json
{
  "type": "pie",
  "title": "Asset Allocation",
  "slices": [
    { "label": "Equities", "value": 60 },
    { "label": "Bonds", "value": 25 },
    { "label": "Cash", "value": 10 },
    { "label": "Alternatives", "value": 5 }
  ]
}
```

### Candlestick Chart

```json
{
  "type": "candlestick",
  "title": "AAPL Price Action",
  "series": [{
    "data": [150, 152, 148, 155, 153],
    "open": [148, 150, 152, 147, 155],
    "high": [153, 155, 154, 158, 157],
    "low": [146, 149, 147, 146, 151],
    "close": [150, 152, 148, 155, 153],
    "label": "AAPL"
  }],
  "xLabels": ["Mon", "Tue", "Wed", "Thu", "Fri"]
}
```

### Histogram

```json
{
  "type": "histogram",
  "title": "Return Distribution",
  "series": [{ "data": [0.5, -1.2, 0.8, -0.3, 1.5, -0.7, 2.1, -1.8, 0.2, 1.0], "label": "Returns" }],
  "bins": 15,
  "grid": true
}
```

### Waterfall

```json
{
  "type": "waterfall",
  "title": "P&L Breakdown",
  "series": [{ "data": [100, -20, 45, -10, -5, 110], "label": "P&L" }],
  "xLabels": ["Revenue", "COGS", "Gross", "OpEx", "Tax", "Total"]
}
```

### Surface 3D

```json
{
  "type": "surface_3d",
  "title": "Volatility Surface",
  "surface": {
    "z": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    "wireframe": true,
    "color": "#C084FC"
  }
}
```

### Violin Plot

```json
{
  "type": "violin",
  "title": "Return Distributions by Strategy",
  "series": [
    { "data": [1.2, -0.5, 0.8, 1.5, -0.3, 2.0, 0.1], "label": "Alpha" },
    { "data": [0.5, 0.3, -0.2, 0.8, 0.1, -0.4, 0.6], "label": "Beta" }
  ],
  "xLabels": ["Alpha", "Beta"]
}
```

---

## Python API Reference

### FlashPlot

```python
from flash_plot import FlashPlot

fig = FlashPlot(width=595, height=260)
```

#### Plotting Methods

| Method | Description |
|--------|-------------|
| `fig.plot(y, *, x=None, color=None, label=None, line_width=1.5, line_style="solid", alpha=1.0, fill_opacity=None)` | Line chart |
| `fig.bar(x_labels, y, *, color=None, label=None, alpha=1.0)` | Bar chart (auto-groups multiple series) |
| `fig.scatter(x, y, *, color=None, label=None, size=4, alpha=1.0)` | Scatter plot |
| `fig.hist(data, *, bins=10, color=None, label=None, alpha=1.0)` | Histogram |
| `fig.fill_between(x, y1, y2=0, *, color=None, alpha=0.15, label=None)` | Filled area between two curves |
| `fig.axhline(y, *, color="#494949", line_width=1, line_style="dashed")` | Horizontal reference line |
| `fig.axvline(x, *, color="#494949", line_width=1, line_style="dashed")` | Vertical reference line |
| `fig.text(x, y, content, *, color="#808080", font_size=10, anchor="start")` | Text annotation |
| `fig.annotate(text, xy, *, xytext=None, color="#808080", arrow_color="#494949")` | Annotation with optional arrow |

#### Configuration Methods

| Method | Description |
|--------|-------------|
| `fig.set_title(title)` | Set chart title (EB Garamond, 18px) |
| `fig.set_subtitle(subtitle)` | Set subtitle (Inter, 11px) |
| `fig.set_xticks(ticks)` | Set x-axis labels (string list) or tick positions (number list) |
| `fig.set_yticks(ticks)` | Set y-axis tick positions |
| `fig.grid(True)` | Show grid lines |
| `fig.legend()` | Show legend |

#### Output Methods

| Method | Description |
|--------|-------------|
| `fig.show()` | Display inline in Jupyter/Colab |
| `fig.render()` | Return SVG string |
| Auto-display | `fig` in a cell auto-renders via `_repr_html_` |

---

## Test Playground

Visit `http://localhost:3000/test2` for an interactive playground:

- JSON editor for ChartSpec input
- Example buttons for all chart types
- Toggle between local rendering and API rendering
- Chart settings dropdown (grid, axis labels, legend, theme)
- Live Scene JSON inspector
- Editable chart titles (click to edit)

Visit `http://localhost:3000/test` for 14 matplotlib-style API demos.

---

## Scrollable Bar Charts

When a bar chart has more than 12 bars, it switches to horizontal scroll mode:

- Bar content scrolls within the SVG using coordinate remapping
- Y-axis labels, title, grid lines, and legend stay fixed
- Mouse wheel scrolls horizontally
- Left/right arrow indicators appear at edges
- Bar glow effects work correctly during scroll

---

## Interactive Features (Frontend)

- **Line tooltips**: Hover shows crosshair + dot on each series + value tooltip
- **Scatter tooltips**: Hover shows exact x, y coordinates
- **Bar tooltips**: Hover shows value with series label
- **Editable titles**: Click chart title or subtitle to edit inline
- **Chart settings**: Dropdown to toggle grid, axis labels, legend, theme (dark/light/naked)
- **Viewport animation**: Charts animate when scrolled into view (IntersectionObserver)

---

## Requirements

### TypeScript

- Node.js >= 18
- Next.js >= 16
- React >= 19
- `@modelcontextprotocol/sdk` (MCP tools)
- `tsx` (dev, for running MCP server)

### Python

- Python >= 3.8
- No required dependencies (pure Python SVG)
- Optional: `ipython` (for notebook display), `numpy` (auto-converted)
