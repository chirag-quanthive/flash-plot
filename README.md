# Flash Plot

Premium dark-themed charting engine for Jupyter notebooks and Google Colab. Matplotlib-like API that renders animated SVG with CSS keyframe animations.

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Installation

### Python (Colab / Jupyter)

```bash
pip install git+https://github.com/quant-hive/ChartingEngine.git#subdirectory=python
```

### TypeScript (Next.js / React)

```bash
git clone https://github.com/quant-hive/ChartingEngine.git
cd ChartingEngine
npm install
npm run dev
```

## Quick Start

### Python

```python
from flash_plot import FlashPlot

fig = FlashPlot()
fig.plot([0, 5, -8, 15, 10, 25, 18, 55, 35, 80], color="#d4d4d4", label="Strategy")
fig.plot([5, 8, 10, 12, 15, 14, 16, 18, 15, 20], color="#707070", label="Benchmark")
fig.set_xticks(["Jan", "Mar", "May", "Jul", "Sep"])
fig.grid(True)
fig.legend()
fig.show()  # renders inline in Jupyter/Colab
```

### TypeScript

```typescript
import { figure, FlashChart } from "./lib/plot";

const fig = figure();
const ax = fig.subplot(1, 1, 1);
ax.plot([0, 5, 12, 8, 18, 25], { color: "#d4d4d4", label: "Strategy" });
ax.grid(true);
ax.legend();
const scene = fig.render();
// <FlashChart scene={scene} />
```

## Chart Types

### Line Chart

```python
fig = FlashPlot()
fig.plot(data, color="#d4d4d4", label="Price", line_style="solid")
fig.plot(ma50, color="#4ECDC4", label="MA 50", line_style="dashed")
fig.grid(True)
fig.legend()
fig.show()
```

Line styles: `"solid"`, `"dashed"`, `"dotted"`, `"dashdot"`

### Bar Chart

```python
fig = FlashPlot()
fig.bar(["AAPL", "MSFT", "GOOGL", "AMZN"], [18, 15, 12, 10], label="Weight %")
fig.grid(True)
fig.show()
```

Bars render with a multi-layer glow effect inspired by premium dark UI design.

### Grouped Bars

```python
fig.bar(labels, series_a, label="Momentum")
fig.bar(labels, series_b, label="S&P 500")
```

### Scatter Plot

```python
fig = FlashPlot()
fig.scatter(x_data, y_data, color="#4ECDC4", label="Assets", size=6)
fig.grid(True)
fig.show()
```

### Histogram

```python
fig = FlashPlot()
fig.hist(returns, bins=20, color="#C084FC", label="Daily Returns")
fig.grid(True)
fig.show()
```

### Area Fill

```python
x = list(range(len(data)))
fig.plot(data, color="#d4d4d4")
fig.fill_between(x, data, 0, color="#d4d4d4", alpha=0.15)
```

### Fill Between Two Curves

```python
fig.fill_between(x, upper_band, lower_band, color="#4ECDC4", alpha=0.15)
fig.plot(mean_line, color="#4ECDC4")
```

### Reference Lines

```python
fig.axhline(200, color="#FF6B6B", line_style="dashed")   # horizontal
fig.axvline(10, color="#4ECDC4", line_style="dotted")     # vertical
```

### Text & Annotations

```python
fig.text(2, 85, "Breakout zone", color="#FFD93D", font_size=9)
fig.annotate("ATH", [19, 100], xytext=[15, 110], color="#4ECDC4", font_size=10)
```

## Axes Configuration

```python
fig.set_xticks(["Q1", "Q2", "Q3", "Q4"])
fig.set_yticks([0, 25, 50, 75, 100])
fig.grid(True)
fig.legend()
```

## Figure Size

```python
fig = FlashPlot(width=800, height=400)
```

## Export

```python
svg_str = fig.render()       # SVG string
fig.show()                   # Display inline in notebook
```

## Animation (TypeScript / React)

The React `<FlashChart>` component includes CSS keyframe animations:
- Grid lines draw in sequentially
- Axis labels fade in with shimmer effect
- Lines animate with a draw effect
- Bars grow upward with glow layers
- Scatter points pop in
- Areas fade in smoothly

## Architecture

```
├── core/                    # Framework-agnostic engine
│   ├── figure.ts            # Figure & Axes classes (matplotlib-like API)
│   ├── renderChart.ts       # ChartSpec → Scene converter
│   ├── types.ts             # Type definitions
│   ├── theme.ts             # Flash Dark theme & color palettes
│   ├── scales.ts            # Linear/log scales, tick computation
│   ├── layout.ts            # Layout & subplot grid computation
│   └── paths.ts             # SVG path builders (line, area, bar, scatter)
├── react/                   # React components
│   ├── FlashChart.tsx        # Main chart renderer with animations
│   ├── PieChart.tsx          # Pie/donut chart component
│   ├── Surface3D.tsx         # 3D surface plot (WebGL)
│   └── useAnimation.ts      # Animation phase hook
├── server/                  # Server-side rendering
│   └── renderSvg.ts         # Scene → SVG string (no React/DOM)
├── src/mcp/                 # MCP server for AI agent integration
│   ├── server.ts            # stdio MCP server (3 tools)
│   └── tools/
│       ├── chartRender.ts   # chart_render — ChartSpec → Scene JSON
│       ├── chartResolve.ts  # chart_resolve_type — recommend chart type
│       └── chartStyles.ts   # chart_get_styles — theme & palettes
├── src/app/api/chart/       # HTTP API endpoints
│   ├── route.ts             # POST /api/chart — command-based rendering
│   └── render/route.ts      # POST /api/chart/render — ChartSpec rendering
├── python/                  # Pure Python package
│   └── flash_plot/          # pip installable for Colab/Jupyter
└── notebooks/               # Demo notebook
    └── flash_plot_demo.ipynb
```

## MCP Integration

The charting engine exposes 3 tools via MCP (Model Context Protocol) for AI agent integration:

- **`chart_render`** — Render a ChartSpec to Scene JSON (or SVG)
- **`chart_resolve_type`** — Recommend chart type based on data description
- **`chart_get_styles`** — Get theme, color palettes, and supported chart types

```bash
npx tsx src/mcp/server.ts    # Start MCP server (stdio)
```

## HTTP API

```bash
# Command-based rendering
curl -X POST http://localhost:3000/api/chart \
  -H "Content-Type: application/json" \
  -d '{"commands": [{"method": "plot", "args": [[1,5,3,8,6]], "kwargs": {"color": "#d4d4d4"}}]}'

# ChartSpec rendering
curl -X POST http://localhost:3000/api/chart/render \
  -H "Content-Type: application/json" \
  -d '{"spec": {"type": "line", "series": [{"data": [1,5,3,8,6]}]}}'
```

## Theme

Flash Plot ships with a dark theme (`flash-dark`) designed for financial dashboards. The default color palette:

| Color | Hex | Use |
|-------|-----|-----|
| Primary | `#d4d4d4` | Main data series |
| Secondary | `#707070` | Benchmarks, secondary |
| Teal | `#4ECDC4` | Highlights |
| Yellow | `#FFD93D` | Warnings, secondary highlights |
| Red | `#FF6B6B` | Drawdowns, alerts |
| Purple | `#C084FC` | Distributions |
| Cyan | `#67E8F9` | Tertiary data |

Bar styles use multi-layer glow effects with per-series color palettes:

| Series | Fill | Style |
|--------|------|-------|
| 1 | `#4aaaba` | Teal glow |
| 2 | `#d8b4fe` | Purple glow |
| 3 | `#fbbf24` | Gold glow |
| 4 | `#f9a8d4` | Pink glow |
| 5 | `#6dd5c8` | Mint glow |

## Requirements

### Python
- Python 3.8+
- No external dependencies (numpy optional)

### TypeScript
- Node.js 18+
- Next.js 16+
- React 19+

## License

MIT
