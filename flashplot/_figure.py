"""
Figure and Axes classes — matplotlib-like API for building charts.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from ._core import (
    Point, Rect, TickMark, TextStyle, Theme, BarGeometry, BarThemeStyle,
    get_theme,
    compute_ticks, generate_tick_marks, scale_value,
    compute_layout, compute_subplot_bounds,
    build_line_path, build_area_path, build_fill_between_path,
    build_bar_rects, build_scatter_points, compute_histogram_bins,
    DEFAULT_WIDTH, DEFAULT_HEIGHT,
)

# ── Scene Graph (output of figure.render()) ─────────────────────────────

@dataclass
class GridLine:
    x1: float; y1: float; x2: float; y2: float
    color: str; width: float

@dataclass
class GridScene:
    visible: bool
    axis: str  # "x" | "y" | "both"
    lines: List[GridLine]

@dataclass
class AxisScene:
    visible: bool
    label: Optional[str]
    ticks: List[TickMark]
    tick_style: TextStyle
    scale: str
    lo: float; hi: float; span: float

@dataclass
class LegendEntry:
    label: str; color: str; kind: str
    line_style: Optional[str] = None
    line_width: Optional[float] = None
    bar_gradient: Optional[Tuple[str, str]] = None

@dataclass
class LegendScene:
    entries: List[LegendEntry]
    position: str = "best"

# ── Plot Elements ───────────────────────────────────────────────────────

@dataclass
class LinePlotElement:
    kind: str = "line"
    points: List[Point] = field(default_factory=list)
    path: str = ""
    color: str = "#d4d4d4"
    line_width: float = 1
    line_style: str = "solid"
    alpha: float = 1
    label: Optional[str] = None
    zorder: int = 0
    data_values: List[float] = field(default_factory=list)

@dataclass
class AreaPlotElement:
    kind: str = "area"
    points: List[Point] = field(default_factory=list)
    path: str = ""
    color: str = "#d4d4d4"
    alpha: float = 0.15
    label: Optional[str] = None
    zorder: int = 0

@dataclass
class BarPlotElement:
    kind: str = "bar"
    bars: List[BarGeometry] = field(default_factory=list)
    series_index: int = 0
    color: str = "#EF8CFF"
    label: Optional[str] = None
    zorder: int = 0
    x_labels: List[str] = field(default_factory=list)

@dataclass
class ScatterPlotElement:
    kind: str = "scatter"
    points: List[Tuple[float, float, float]] = field(default_factory=list)
    color: str = "#4ECDC4"
    marker: str = "o"
    alpha: float = 1
    label: Optional[str] = None
    zorder: int = 0
    data_xy: List[Tuple[float, float]] = field(default_factory=list)

@dataclass
class HLinePlotElement:
    kind: str = "hline"
    y: float = 0
    x_min: float = 0; x_max: float = 0
    color: str = "#707070"; line_width: float = 1; line_style: str = "dashed"
    zorder: int = 0

@dataclass
class VLinePlotElement:
    kind: str = "vline"
    x: float = 0
    y_min: float = 0; y_max: float = 0
    color: str = "#707070"; line_width: float = 1; line_style: str = "dashed"
    zorder: int = 0

@dataclass
class TextPlotElement:
    kind: str = "text"
    x: float = 0; y: float = 0
    content: str = ""
    style: TextStyle = field(default_factory=TextStyle)
    anchor: str = "start"
    rotation: Optional[float] = None
    zorder: int = 0

@dataclass
class AnnotationPlotElement:
    kind: str = "annotation"
    text: str = ""
    xy: Point = field(default_factory=lambda: Point(0, 0))
    xy_text: Optional[Point] = None
    style: TextStyle = field(default_factory=TextStyle)
    arrow_color: Optional[str] = None
    arrow_width: Optional[float] = None
    zorder: int = 0

PlotElement = Union[
    LinePlotElement, AreaPlotElement, BarPlotElement, ScatterPlotElement,
    HLinePlotElement, VLinePlotElement, TextPlotElement, AnnotationPlotElement,
]

@dataclass
class SubplotScene:
    row: int; col: int
    bounds: Rect
    plot_area: Rect
    title: Optional[str]
    title_style: Optional[TextStyle]
    x_axis: AxisScene
    y_axis: AxisScene
    grid: GridScene
    elements: List[PlotElement]
    legend: Optional[LegendScene] = None

@dataclass
class Scene:
    width: float; height: float
    theme_name: str
    subplots: List[SubplotScene]


# ── Internal command types ──────────────────────────────────────────────

@dataclass
class _PlotCmd:
    kind: str = "line"
    x_data: Optional[List[float]] = None
    y_data: List[float] = field(default_factory=list)
    opts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class _BarCmd:
    kind: str = "bar"
    x_data: Any = None  # List[float] | List[str]
    y_data: List[float] = field(default_factory=list)
    opts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class _ScatterCmd:
    kind: str = "scatter"
    x_data: List[float] = field(default_factory=list)
    y_data: List[float] = field(default_factory=list)
    opts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class _FillCmd:
    kind: str = "fill_between"
    x_data: List[float] = field(default_factory=list)
    y1_data: List[float] = field(default_factory=list)
    y2_data: Any = 0  # float | List[float]
    opts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class _HistCmd:
    kind: str = "hist"
    data: List[float] = field(default_factory=list)
    opts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class _HLineCmd:
    kind: str = "hline"
    y: float = 0
    opts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class _VLineCmd:
    kind: str = "vline"
    x: float = 0
    opts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class _TextCmd:
    kind: str = "text"
    x: float = 0; y: float = 0
    content: str = ""
    opts: Dict[str, Any] = field(default_factory=dict)

@dataclass
class _AnnotateCmd:
    kind: str = "annotate"
    text: str = ""
    xy: Tuple[float, float] = (0, 0)
    xy_text: Optional[Tuple[float, float]] = None
    opts: Dict[str, Any] = field(default_factory=dict)


# ── Axes Class ──────────────────────────────────────────────────────────

class Axes:
    def __init__(self, row: int, col: int, theme: Theme):
        self._row = row
        self._col = col
        self._theme = theme
        self._commands: List[Any] = []
        self._title: Optional[str] = None
        self._xlabel: Optional[str] = None
        self._ylabel: Optional[str] = None
        self._xlim: Optional[Tuple[float, float]] = None
        self._ylim: Optional[Tuple[float, float]] = None
        self._xscale = "linear"
        self._yscale = "linear"
        self._xticks: Optional[Union[List[float], List[str]]] = None
        self._yticks: Optional[List[float]] = None
        self._grid_opts: Dict[str, Any] = {"visible": True, "axis": "y"}
        self._legend_opts: Optional[Dict[str, Any]] = None
        self._color_idx = 0

    def _next_color(self) -> str:
        c = self._theme.default_colors[self._color_idx % len(self._theme.default_colors)]
        self._color_idx += 1
        return c

    # ── Matplotlib-like API ─────────────────────────────────────────────

    def plot(self, *args, **kwargs) -> "Axes":
        """plot(y, **kw) or plot(x, y, **kw)"""
        if len(args) >= 2 and isinstance(args[0], (list, tuple)) and isinstance(args[1], (list, tuple)):
            x_data, y_data = list(args[0]), list(args[1])
            opts = args[2] if len(args) > 2 and isinstance(args[2], dict) else kwargs
        else:
            x_data, y_data = None, list(args[0])
            opts = args[1] if len(args) > 1 and isinstance(args[1], dict) else kwargs
        if "color" not in opts:
            opts["color"] = self._next_color()
        self._commands.append(_PlotCmd(x_data=x_data, y_data=y_data, opts=dict(opts)))
        return self

    def bar(self, x_data, y_data, **kwargs) -> "Axes":
        self._commands.append(_BarCmd(x_data=list(x_data), y_data=list(y_data), opts=kwargs))
        return self

    def scatter(self, x_data, y_data, **kwargs) -> "Axes":
        if "color" not in kwargs:
            kwargs["color"] = self._next_color()
        self._commands.append(_ScatterCmd(x_data=list(x_data), y_data=list(y_data), opts=kwargs))
        return self

    def fill_between(self, x, y1, y2=0, **kwargs) -> "Axes":
        y2_val = list(y2) if isinstance(y2, (list, tuple)) else y2
        self._commands.append(_FillCmd(x_data=list(x), y1_data=list(y1), y2_data=y2_val, opts=kwargs))
        return self

    def hist(self, data, **kwargs) -> "Axes":
        self._commands.append(_HistCmd(data=list(data), opts=kwargs))
        return self

    def axhline(self, y, **kwargs) -> "Axes":
        self._commands.append(_HLineCmd(y=y, opts=kwargs))
        return self

    def axvline(self, x, **kwargs) -> "Axes":
        self._commands.append(_VLineCmd(x=x, opts=kwargs))
        return self

    def text(self, x, y, content, **kwargs) -> "Axes":
        self._commands.append(_TextCmd(x=x, y=y, content=content, opts=kwargs))
        return self

    def annotate(self, text, xy, xytext=None, **kwargs) -> "Axes":
        self._commands.append(_AnnotateCmd(text=text, xy=tuple(xy), xy_text=tuple(xytext) if xytext else None, opts=kwargs))
        return self

    def set_title(self, title: str) -> "Axes":
        self._title = title; return self

    def set_xlabel(self, label: str) -> "Axes":
        self._xlabel = label; return self

    def set_ylabel(self, label: str) -> "Axes":
        self._ylabel = label; return self

    def set_xlim(self, lo: float, hi: float) -> "Axes":
        self._xlim = (lo, hi); return self

    def set_ylim(self, lo: float, hi: float) -> "Axes":
        self._ylim = (lo, hi); return self

    def set_xscale(self, scale: str) -> "Axes":
        self._xscale = scale; return self

    def set_yscale(self, scale: str) -> "Axes":
        self._yscale = scale; return self

    def set_xticks(self, ticks, labels=None) -> "Axes":
        self._xticks = list(ticks)
        return self

    def set_yticks(self, ticks) -> "Axes":
        self._yticks = list(ticks); return self

    def grid(self, visible=True, **kwargs) -> "Axes":
        if isinstance(visible, bool):
            self._grid_opts = {"visible": visible, **kwargs}
        else:
            self._grid_opts = visible
        return self

    def legend(self, **kwargs) -> "Axes":
        self._legend_opts = kwargs; return self

    # ── Render ──────────────────────────────────────────────────────────

    def _render(self, bounds: Rect) -> SubplotScene:
        pa = compute_layout(bounds.w, bounds.h)  # plot area relative to (0,0)

        # Pre-compute histograms
        hist_results: Dict[int, Tuple[List[float], List[int]]] = {}
        for idx, cmd in enumerate(self._commands):
            if isinstance(cmd, _HistCmd):
                hist_results[idx] = compute_histogram_bins(cmd.data, cmd.opts.get("bins", 10))

        # Data bounds
        x_lo, x_hi, y_lo, y_hi = float("inf"), float("-inf"), float("inf"), float("-inf")
        has_bar = False
        bar_series_count = 0

        for idx, cmd in enumerate(self._commands):
            if isinstance(cmd, _PlotCmd):
                for v in cmd.y_data:
                    y_lo, y_hi = min(y_lo, v), max(y_hi, v)
                if cmd.x_data:
                    for v in cmd.x_data:
                        x_lo, x_hi = min(x_lo, v), max(x_hi, v)
                else:
                    x_lo, x_hi = min(x_lo, 0), max(x_hi, len(cmd.y_data) - 1)
            elif isinstance(cmd, _BarCmd):
                has_bar = True
                bar_series_count += 1
                for v in cmd.y_data:
                    y_lo, y_hi = min(y_lo, v), max(y_hi, v)
                if cmd.x_data and isinstance(cmd.x_data[0], (int, float)):
                    for v in cmd.x_data:
                        x_lo, x_hi = min(x_lo, v), max(x_hi, v)
            elif isinstance(cmd, _ScatterCmd):
                for v in cmd.x_data:
                    x_lo, x_hi = min(x_lo, v), max(x_hi, v)
                for v in cmd.y_data:
                    y_lo, y_hi = min(y_lo, v), max(y_hi, v)
            elif isinstance(cmd, _FillCmd):
                for v in cmd.y1_data:
                    y_lo, y_hi = min(y_lo, v), max(y_hi, v)
                if isinstance(cmd.y2_data, list):
                    for v in cmd.y2_data:
                        y_lo, y_hi = min(y_lo, v), max(y_hi, v)
                else:
                    y_lo, y_hi = min(y_lo, cmd.y2_data), max(y_hi, cmd.y2_data)
            elif isinstance(cmd, _HistCmd):
                edges, counts = hist_results[idx]
                x_lo, x_hi = min(x_lo, edges[0]), max(x_hi, edges[-1])
                y_lo = min(y_lo, 0)
                y_hi = max(y_hi, max(counts) * 1.1)

        if has_bar:
            y_lo = min(y_lo, 0)

        if self._xlim:
            x_lo, x_hi = self._xlim
        if self._ylim:
            y_lo, y_hi = self._ylim

        # Compute ticks
        y_tick_lo, y_tick_hi, y_step, y_tick_vals = compute_ticks(self._yscale, y_lo, y_hi, 5)
        if not self._ylim:
            y_lo, y_hi = y_tick_lo, y_tick_hi
        y_range = (y_hi - y_lo) or 1

        # If x bounds are still infinite (all categorical data), default to index range
        if x_lo == float("inf") or x_hi == float("-inf"):
            x_lo, x_hi = 0, 1
        x_range = (x_hi - x_lo) or 1

        if self._xscale != "category" and math.isfinite(x_lo) and math.isfinite(x_hi):
            _, _, _, x_tick_vals = compute_ticks(self._xscale, x_lo, x_hi, 8)
        else:
            x_tick_vals = []

        y_ticks = self._yticks or y_tick_vals
        y_tick_marks = generate_tick_marks(y_ticks, y_lo, y_hi, pa.y + pa.h, pa.y, self._yscale)

        # X tick marks
        if self._xticks and isinstance(self._xticks[0], str):
            labels = self._xticks
            if has_bar:
                bar_cmd = next((c for c in self._commands if isinstance(c, _BarCmd)), None)
                n = len(bar_cmd.y_data) if bar_cmd else len(labels)
                gw = pa.w / n
                x_tick_marks = [TickMark(i, lbl, pa.x + i * gw + gw / 2) for i, lbl in enumerate(labels)]
            else:
                x_tick_marks = [
                    TickMark(i, lbl, pa.x + (pa.w / 2 if len(labels) <= 1 else (i / (len(labels) - 1)) * pa.w))
                    for i, lbl in enumerate(labels)
                ]
        elif has_bar:
            bar_cmd = next((c for c in self._commands if isinstance(c, _BarCmd)), None)
            if bar_cmd and isinstance(bar_cmd.x_data[0], str):
                labels = bar_cmd.x_data
                gw = pa.w / len(labels)
                x_tick_marks = [TickMark(i, lbl, pa.x + i * gw + gw / 2) for i, lbl in enumerate(labels)]
            else:
                use_ticks = (self._xticks if self._xticks and isinstance(self._xticks[0], (int, float)) else None) or x_tick_vals
                x_tick_marks = generate_tick_marks(use_ticks, x_lo, x_hi, pa.x, pa.x + pa.w, self._xscale)
        else:
            use_ticks = (self._xticks if self._xticks and isinstance(self._xticks[0], (int, float)) else None) or x_tick_vals
            x_tick_marks = generate_tick_marks(use_ticks, x_lo, x_hi, pa.x, pa.x + pa.w, self._xscale)

        tick_style = TextStyle(
            font_family=self._theme.axis_font_family,
            font_size=self._theme.axis_font_size,
            font_weight=self._theme.axis_font_weight,
            letter_spacing=self._theme.axis_letter_spacing,
            color=self._theme.text_muted,
        )

        x_axis = AxisScene(True, self._xlabel, x_tick_marks, tick_style, self._xscale, x_lo, x_hi, x_range)
        y_axis = AxisScene(True, self._ylabel, y_tick_marks, tick_style, self._yscale, y_lo, y_hi, y_range)

        # Grid
        grid_visible = self._grid_opts.get("visible", True)
        grid_axis = self._grid_opts.get("axis", "y")
        grid_lines: List[GridLine] = []
        if grid_visible:
            gc = self._grid_opts.get("color", self._theme.grid_color)
            gw = self._grid_opts.get("linewidth", self._theme.grid_width)
            if grid_axis in ("y", "both"):
                for t in y_tick_marks:
                    grid_lines.append(GridLine(pa.x, t.position, pa.x + pa.w, t.position, gc, gw))
            if grid_axis in ("x", "both"):
                for t in x_tick_marks:
                    grid_lines.append(GridLine(t.position, pa.y, t.position, pa.y + pa.h, gc, gw))

        # Elements
        elements: List[PlotElement] = []
        legend_entries: List[LegendEntry] = []
        z = 0
        bar_si = 0

        for cmd_idx, cmd in enumerate(self._commands):
            z += 1
            if isinstance(cmd, _PlotCmd):
                if cmd.x_data:
                    pts = [
                        Point(
                            pa.x + scale_value(self._xscale, cmd.x_data[i], x_lo, x_hi, 0, pa.w),
                            pa.y + pa.h - scale_value(self._yscale, v, y_lo, y_hi, 0, pa.h),
                        )
                        for i, v in enumerate(cmd.y_data)
                    ]
                    path = " ".join(f"{'M' if i == 0 else 'L'}{p.x:.1f},{p.y:.1f}" for i, p in enumerate(pts))
                else:
                    path, pts = build_line_path(cmd.y_data, pa, y_lo, y_hi, self._yscale)
                color = cmd.opts.get("color", self._theme.default_colors[0])
                el = LinePlotElement(
                    points=pts, path=path, color=color,
                    line_width=cmd.opts.get("linewidth", 1),
                    line_style=cmd.opts.get("linestyle", "solid"),
                    alpha=cmd.opts.get("alpha", 1),
                    label=cmd.opts.get("label"), zorder=cmd.opts.get("zorder", z),
                    data_values=list(cmd.y_data),
                )
                elements.append(el)
                if el.label:
                    legend_entries.append(LegendEntry(el.label, color, "line", el.line_style, el.line_width))

            elif isinstance(cmd, _BarCmd):
                bw = cmd.opts.get("width", 20)
                color = cmd.opts.get("color", self._theme.bar_styles[bar_si % len(self._theme.bar_styles)].fill)
                if isinstance(color, list):
                    color = color[0]
                bars = build_bar_rects(cmd.y_data, bar_si, bar_series_count, pa, y_lo, y_hi, bw, 3, cmd.opts.get("bottom"))
                xlbls = [str(x) for x in cmd.x_data] if cmd.x_data else [str(i) for i in range(len(cmd.y_data))]
                el = BarPlotElement(bars=bars, series_index=bar_si, color=color, label=cmd.opts.get("label"), zorder=cmd.opts.get("zorder", z), x_labels=xlbls)
                elements.append(el)
                if el.label:
                    st = self._theme.bar_styles[bar_si % len(self._theme.bar_styles)]
                    legend_entries.append(LegendEntry(el.label, color, "bar", bar_gradient=(st.grad_top, st.grad_bottom)))
                bar_si += 1

            elif isinstance(cmd, _ScatterCmd):
                color = cmd.opts.get("color", self._theme.default_colors[0])
                pts = build_scatter_points(cmd.x_data, cmd.y_data, pa, x_lo, x_hi, y_lo, y_hi, cmd.opts.get("s"), self._xscale, self._yscale)
                raw_xy = list(zip(cmd.x_data, cmd.y_data))
                el = ScatterPlotElement(points=pts, color=color, marker=cmd.opts.get("marker", "o"), alpha=cmd.opts.get("alpha", 1), label=cmd.opts.get("label"), zorder=cmd.opts.get("zorder", z), data_xy=raw_xy)
                elements.append(el)
                if el.label:
                    legend_entries.append(LegendEntry(el.label, color, "scatter"))

            elif isinstance(cmd, _FillCmd):
                if isinstance(cmd.y2_data, list):
                    # Two-curve fill_between
                    n = len(cmd.y1_data)
                    if cmd.x_data:
                        top = [
                            Point(
                                pa.x + scale_value(self._xscale, cmd.x_data[i], x_lo, x_hi, 0, pa.w),
                                pa.y + pa.h - scale_value(self._yscale, v, y_lo, y_hi, 0, pa.h),
                            )
                            for i, v in enumerate(cmd.y1_data)
                        ]
                        bot = [
                            Point(
                                pa.x + scale_value(self._xscale, cmd.x_data[i], x_lo, x_hi, 0, pa.w),
                                pa.y + pa.h - scale_value(self._yscale, v, y_lo, y_hi, 0, pa.h),
                            )
                            for i, v in enumerate(cmd.y2_data)
                        ]
                        fwd = " ".join(f"{'M' if i == 0 else 'L'}{p.x:.1f},{p.y:.1f}" for i, p in enumerate(top))
                        bwd = " ".join(f"L{p.x:.1f},{p.y:.1f}" for p in reversed(bot))
                        path = f"{fwd} {bwd} Z"
                        pts = top
                    else:
                        path, pts = build_fill_between_path(cmd.y1_data, cmd.y2_data, pa, y_lo, y_hi, self._yscale)
                else:
                    # Area fill down to baseline
                    baseline = cmd.y2_data
                    base_y = pa.y + pa.h  # always close at bottom of plot area
                    if cmd.x_data:
                        pts = [
                            Point(
                                pa.x + scale_value(self._xscale, cmd.x_data[i], x_lo, x_hi, 0, pa.w),
                                pa.y + pa.h - scale_value(self._yscale, v, y_lo, y_hi, 0, pa.h),
                            )
                            for i, v in enumerate(cmd.y1_data)
                        ]
                    else:
                        pts = [map_point(i, v, len(cmd.y1_data), pa, y_lo, y_hi, self._yscale) for i, v in enumerate(cmd.y1_data)]
                    line = " ".join(f"{'M' if i == 0 else 'L'}{p.x:.1f},{p.y:.1f}" for i, p in enumerate(pts))
                    path = f"{line} L{pts[-1].x:.1f},{base_y:.1f} L{pts[0].x:.1f},{base_y:.1f} Z"
                color = cmd.opts.get("color", self._theme.default_colors[0])
                el = AreaPlotElement(points=pts, path=path, color=color, alpha=cmd.opts.get("alpha", 0.15), label=cmd.opts.get("label"), zorder=cmd.opts.get("zorder", z))
                elements.append(el)
                if el.label:
                    legend_entries.append(LegendEntry(el.label, color, "area"))

            elif isinstance(cmd, _HistCmd):
                edges, counts = hist_results[cmd_idx]
                color = cmd.opts.get("color", self._theme.default_colors[0])
                bars = []
                for i, count in enumerate(counts):
                    bx = pa.x + ((edges[i] - x_lo) / x_range) * pa.w
                    bw = ((edges[i + 1] - edges[i]) / x_range) * pa.w * 0.92
                    by = pa.y + pa.h - ((count - y_lo) / y_range) * pa.h
                    bh = max(1, ((count - y_lo) / y_range) * pa.h)
                    bars.append(BarGeometry(bx, by, bw, bh, count, i))
                xlbls = [f"{edges[i]:.1f}–{edges[i+1]:.1f}" for i in range(len(counts))]
                el = BarPlotElement(bars=bars, series_index=0, color=color, label=cmd.opts.get("label"), zorder=cmd.opts.get("zorder", z), x_labels=xlbls)
                elements.append(el)

            elif isinstance(cmd, _HLineCmd):
                py = pa.y + pa.h - ((cmd.y - y_lo) / y_range) * pa.h
                el = HLinePlotElement(y=py, x_min=pa.x, x_max=pa.x + pa.w, color=cmd.opts.get("color", self._theme.text_secondary), line_width=cmd.opts.get("linewidth", 1), line_style=cmd.opts.get("linestyle", "dashed"), zorder=cmd.opts.get("zorder", z))
                elements.append(el)

            elif isinstance(cmd, _VLineCmd):
                px = pa.x + ((cmd.x - x_lo) / x_range) * pa.w
                el = VLinePlotElement(x=px, y_min=pa.y, y_max=pa.y + pa.h, color=cmd.opts.get("color", self._theme.text_secondary), line_width=cmd.opts.get("linewidth", 1), line_style=cmd.opts.get("linestyle", "dashed"), zorder=cmd.opts.get("zorder", z))
                elements.append(el)

            elif isinstance(cmd, _TextCmd):
                px = pa.x + ((cmd.x - x_lo) / x_range) * pa.w
                py = pa.y + pa.h - ((cmd.y - y_lo) / y_range) * pa.h
                ha_map = {"left": "start", "center": "middle", "right": "end"}
                el = TextPlotElement(x=px, y=py, content=cmd.content, style=TextStyle(
                    font_family=cmd.opts.get("fontfamily", self._theme.axis_font_family),
                    font_size=cmd.opts.get("fontsize", 12),
                    font_weight=cmd.opts.get("fontweight", 400),
                    color=cmd.opts.get("color", self._theme.text_primary),
                ), anchor=ha_map.get(cmd.opts.get("ha", "left"), "start"), rotation=cmd.opts.get("rotation"), zorder=cmd.opts.get("zorder", z))
                elements.append(el)

            elif isinstance(cmd, _AnnotateCmd):
                ax_, ay = cmd.xy
                px = pa.x + ((ax_ - x_lo) / x_range) * pa.w
                py = pa.y + pa.h - ((ay - y_lo) / y_range) * pa.h
                tx, ty = px, py
                if cmd.xy_text:
                    tx = pa.x + ((cmd.xy_text[0] - x_lo) / x_range) * pa.w
                    ty = pa.y + pa.h - ((cmd.xy_text[1] - y_lo) / y_range) * pa.h
                el = AnnotationPlotElement(text=cmd.text, xy=Point(px, py), xy_text=Point(tx, ty) if cmd.xy_text else None, style=TextStyle(
                    font_family=self._theme.axis_font_family,
                    font_size=cmd.opts.get("fontsize", 11),
                    font_weight=cmd.opts.get("fontweight", 400),
                    color=cmd.opts.get("color", self._theme.text_primary),
                ), arrow_color=cmd.opts.get("arrowprops", {}).get("color"), arrow_width=cmd.opts.get("arrowprops", {}).get("lw"), zorder=cmd.opts.get("zorder", z))
                elements.append(el)

        elements.sort(key=lambda e: e.zorder)

        legend = None
        if self._legend_opts is not None and legend_entries:
            legend = LegendScene(legend_entries, self._legend_opts.get("loc", "best"))

        return SubplotScene(
            row=self._row, col=self._col, bounds=bounds, plot_area=pa,
            title=self._title,
            title_style=TextStyle(
                font_family=self._theme.title_font_family,
                font_size=self._theme.title_font_size,
                font_weight=400, color=self._theme.title_color,
            ) if self._title else None,
            x_axis=x_axis, y_axis=y_axis, grid=GridScene(grid_visible, grid_axis, grid_lines),
            elements=elements, legend=legend,
        )


# ── Figure Class ────────────────────────────────────────────────────────

class Figure:
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, theme="flash-dark", hover=True):
        self._width = width
        self._height = height
        self._theme = get_theme(theme)
        self._nrows = 1
        self._ncols = 1
        self._axes: Dict[str, Axes] = {}
        self._hover = hover

    def subplot(self, nrows: int, ncols: int, index: int) -> Axes:
        self._nrows = max(self._nrows, nrows)
        self._ncols = max(self._ncols, ncols)
        r = (index - 1) // ncols
        c = (index - 1) % ncols
        key = f"{r}-{c}"
        if key not in self._axes:
            self._axes[key] = Axes(r, c, self._theme)
        return self._axes[key]

    def gca(self) -> Axes:
        return self.subplot(1, 1, 1)

    def add_subplot(self, nrows: int, ncols: int, index: int) -> Axes:
        return self.subplot(nrows, ncols, index)

    def set_size(self, width: float, height: float) -> "Figure":
        self._width = width
        self._height = height
        return self

    def render(self) -> Scene:
        bounds = compute_subplot_bounds(self._nrows, self._ncols, self._width, self._height)
        subplots = []
        for ax in self._axes.values():
            subplots.append(ax._render(bounds[ax._row][ax._col]))
        return Scene(self._width, self._height, self._theme.name, subplots)

    # ── Display methods ─────────────────────────────────────────────────

    def hover(self, enabled: bool = True) -> "Figure":
        """Enable or disable hover tooltips."""
        self._hover = enabled
        return self

    def to_svg(self, animate: bool = True, hover: Optional[bool] = None) -> str:
        from ._render import render_svg
        h = hover if hover is not None else self._hover
        return render_svg(self.render(), animate=animate, hover=h)

    def to_html(self, animate: bool = True, hover: Optional[bool] = None) -> str:
        from ._render import render_html
        h = hover if hover is not None else self._hover
        return render_html(self.render(), animate=animate, hover=h)

    def show(self, hover: Optional[bool] = None) -> None:
        """Display in Jupyter/Colab."""
        try:
            from IPython.display import display, HTML
            display(HTML(self.to_html(hover=hover)))
        except ImportError:
            print(self.to_svg(animate=False, hover=False))

    def savefig(self, path: str, animate: bool = False) -> None:
        if path.endswith(".html"):
            with open(path, "w") as f:
                f.write(self.to_html(animate=animate))
        else:
            with open(path, "w") as f:
                f.write(self.to_svg(animate=animate))

    def _repr_html_(self) -> str:
        """Auto-display in Jupyter."""
        return self.to_html()


def figure(width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, theme="flash-dark", hover=True) -> Figure:
    return Figure(width, height, theme, hover=hover)
