# Flash Plot

Premium dark-themed charting engine for Jupyter notebooks and Google Colab. Matplotlib-like API that renders animated SVG with CSS keyframe animations.

![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Installation

```bash
pip install flash-plot
```

Or install from source:

```bash
git clone https://github.com/quanthive/flash-plot.git
cd flash-plot
pip install -e .
```

## Quick Start

```python
import flashplot as fp

fig = fp.figure()
ax = fig.subplot(1, 1, 1)
ax.plot([0, 5, -8, 15, 10, 25, 18, 55, 35, 80], color="#d4d4d4", label="Strategy")
ax.plot([5, 8, 10, 12, 15, 14, 16, 18, 15, 20], color="#707070", label="Benchmark")
ax.set_xticks(["Jan", "Mar", "May", "Jul", "Sep"])
ax.grid(True)
ax.legend()
fig.show()  # renders inline in Jupyter/Colab
```

In Jupyter and Colab, figures render automatically — just put `fig` as the last expression in a cell.

## Chart Types

### Line Chart

```python
fig = fp.figure()
ax = fig.subplot(1, 1, 1)
ax.plot(data, color="#d4d4d4", label="Price", linestyle="solid")
ax.plot(ma50, color="#4ECDC4", label="MA 50", linestyle="dashed")
ax.grid(True)
ax.legend()
fig.show()
```

Line styles: `"solid"`, `"dashed"`, `"dotted"`, `"dashdot"`

### Bar Chart

```python
fig = fp.figure()
ax = fig.subplot(1, 1, 1)
ax.bar(["AAPL", "MSFT", "GOOGL", "AMZN"], [18, 15, 12, 10], label="Weight %")
ax.grid(True)
fig.show()
```

Bars render with a multi-layer glow effect inspired by premium dark UI design.

### Grouped Bars

```python
ax.bar(labels, series_a, label="Momentum")
ax.bar(labels, series_b, label="S&P 500")
```

### Scatter Plot

```python
fig = fp.figure()
ax = fig.subplot(1, 1, 1)
ax.scatter(x_data, y_data, s=sizes, color="#4ECDC4", label="Assets")
ax.grid(True)
fig.show()
```

### Histogram

```python
fig = fp.figure()
ax = fig.subplot(1, 1, 1)
ax.hist(returns, bins=20, color="#C084FC", label="Daily Returns")
ax.grid(True)
fig.show()
```

### Area Fill

```python
x = list(range(len(data)))
ax.plot(data, color="#d4d4d4")
ax.fill_between(x, data, 0, color="#d4d4d4", alpha=0.15)
```

### Fill Between Two Curves

```python
ax.fill_between(x, upper_band, lower_band, color="#4ECDC4", alpha=0.15)
ax.plot(mean_line, color="#4ECDC4")
```

### Reference Lines

```python
ax.axhline(200, color="#FF6B6B", linestyle="dashed")   # horizontal
ax.axvline(10, color="#4ECDC4", linestyle="dotted")     # vertical
```

### Text & Annotations

```python
ax.text(2, 85, "Breakout zone", color="#FFD93D", fontsize=9)
ax.annotate("ATH", [19, 100], [15, 110],
    color="#4ECDC4", fontsize=10,
    arrowprops={"color": "#4ECDC4", "lw": 1})
```

## Axes Configuration

```python
ax.set_xticks(["Q1", "Q2", "Q3", "Q4"])
ax.set_xscale("log")       # "linear" (default) or "log"
ax.set_yscale("log")
ax.set_xlim(0, 100)
ax.set_ylim(-50, 200)
ax.grid(True)
ax.legend()
```

## Figure Size

```python
fig = fp.figure()
fig.set_size(800, 400)      # width, height in pixels
```

## Saving Charts

```python
fig.savefig("chart.svg")    # SVG file
fig.savefig("chart.html")   # HTML file with dark background
```

## Export as String

```python
svg_str = fig.to_svg()
html_str = fig.to_html()
```

## Animation

All charts include CSS keyframe animations by default:
- Grid lines draw in sequentially
- Axis labels fade in
- Lines animate with a draw effect
- Bars grow upward
- Scatter points pop in
- Areas fade in smoothly

To disable animation:

```python
svg_str = fig.to_svg(animate=False)
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

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT
