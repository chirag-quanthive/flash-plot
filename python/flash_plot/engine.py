"""Pure Python Flash Plot engine — renders SVG charts locally, no server needed."""

from __future__ import annotations

import math
import html as _html
from typing import List, Optional, Tuple, Union, Any

# ── Constants ──────────────────────────────────────────────────────────────

DEFAULT_WIDTH = 595
DEFAULT_HEIGHT = 280
DEFAULT_PADDING = {"top": 4, "right": 16, "bottom": 28, "left": 32}
DEFAULT_INSET = 16

DEFAULT_COLORS = [
    "#d4d4d4", "#707070", "#4ECDC4", "#C084FC", "#FFD93D",
    "#FF6B6B", "#67E8F9", "#F9A8D4", "#A5F3D8", "#FBBF24",
]

BAR_STYLES = [
    {"fill": "#4aaaba", "grad_top": "#5ecede", "grad_bottom": "#2a8a9a"},
    {"fill": "#d8b4fe", "grad_top": "#e4ccff", "grad_bottom": "#b888ee"},
    {"fill": "#fbbf24", "grad_top": "#fcd34d", "grad_bottom": "#d99b06"},
    {"fill": "#f9a8d4", "grad_top": "#fbc8e4", "grad_bottom": "#e87ab4"},
    {"fill": "#6dd5c8", "grad_top": "#8eeae0", "grad_bottom": "#4cb8aa"},
]


# ── Helpers ────────────────────────────────────────────────────────────────

def _esc(s: str) -> str:
    return _html.escape(s, quote=True)


def _convert(obj: Any) -> Any:
    """Convert numpy arrays and scalars to plain Python types."""
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
    except ImportError:
        pass
    if isinstance(obj, (list, tuple)):
        return [_convert(x) for x in obj]
    return obj


def _nice_num(x: float, round_: bool) -> float:
    exp = math.floor(math.log10(abs(x))) if x != 0 else 0
    frac = x / (10 ** exp)
    if round_:
        if frac < 1.5:
            nice = 1
        elif frac < 3:
            nice = 2
        elif frac < 7:
            nice = 5
        else:
            nice = 10
    else:
        if frac <= 1:
            nice = 1
        elif frac <= 2:
            nice = 2
        elif frac <= 5:
            nice = 5
        else:
            nice = 10
    return nice * (10 ** exp)


def _compute_ticks(dmin: float, dmax: float, max_ticks: int = 6) -> List[float]:
    if dmin == dmax:
        return [dmin]
    range_ = _nice_num(dmax - dmin, False)
    step = _nice_num(range_ / max(max_ticks - 1, 1), True)
    lo = math.floor(dmin / step) * step
    hi = math.ceil(dmax / step) * step
    ticks = []
    t = lo
    while t <= hi + step * 0.5:
        ticks.append(round(t, 10))
        t += step
    return ticks


def _fmt_val(v: float) -> str:
    if abs(v) >= 1e6:
        return f"{v:.2e}"
    if abs(v) >= 100:
        return f"{v:,.0f}"
    if abs(v) >= 1:
        return f"{v:.2f}"
    if v == 0:
        return "0"
    return f"{v:.4g}"


def _dash_array(style: str) -> Optional[str]:
    if style == "dashed":
        return "8 4"
    if style == "dotted":
        return "2 3"
    if style == "dashdot":
        return "8 3 2 3"
    return None


# ── Command types ──────────────────────────────────────────────────────────

class _PlotCmd:
    def __init__(self, kind: str, **kw):
        self.kind = kind
        self.__dict__.update(kw)


# ── FlashPlot ──────────────────────────────────────────────────────────────

class FlashPlot:
    """Matplotlib-like API that renders to SVG. Works in Colab, Jupyter, or any Python env."""

    def __init__(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
        self.width = width
        self.height = height
        self._commands: List[_PlotCmd] = []
        self._title: Optional[str] = None
        self._subtitle: Optional[str] = None
        self._xticks: Optional[list] = None
        self._yticks: Optional[list] = None
        self._grid = False
        self._show_legend = False
        self._legend_kwargs: dict = {}
        self._series_idx = 0
        self._bar_series_idx = 0

    # ── Plotting methods ───────────────────────────────────────────────

    def plot(self, y_data, *, x=None, color=None, label=None, line_width=1.5,
             line_style="solid", alpha=1.0, fill_opacity=None):
        y = _convert(y_data)
        xd = _convert(x) if x is not None else None
        c = color or DEFAULT_COLORS[self._series_idx % len(DEFAULT_COLORS)]
        self._commands.append(_PlotCmd("line", y=y, x=xd, color=c, label=label,
                                        line_width=line_width, line_style=line_style,
                                        alpha=alpha, fill_opacity=fill_opacity))
        self._series_idx += 1
        return self

    def bar(self, x_labels, y_data, *, color=None, label=None, alpha=1.0):
        y = _convert(y_data)
        xl = _convert(x_labels)
        c = color or BAR_STYLES[self._bar_series_idx % len(BAR_STYLES)]["fill"]
        self._commands.append(_PlotCmd("bar", y=y, x_labels=xl, color=c, label=label,
                                        alpha=alpha, series_idx=self._bar_series_idx))
        self._bar_series_idx += 1
        self._series_idx += 1
        return self

    def scatter(self, x_data, y_data, *, color=None, label=None, size=4, alpha=1.0):
        xd = _convert(x_data)
        yd = _convert(y_data)
        c = color or DEFAULT_COLORS[self._series_idx % len(DEFAULT_COLORS)]
        self._commands.append(_PlotCmd("scatter", x=xd, y=yd, color=c, label=label,
                                        size=size, alpha=alpha))
        self._series_idx += 1
        return self

    def hist(self, data, *, bins=10, color=None, label=None, alpha=1.0):
        d = _convert(data)
        c = color or BAR_STYLES[self._bar_series_idx % len(BAR_STYLES)]["fill"]
        self._commands.append(_PlotCmd("hist", data=d, bins=bins, color=c, label=label,
                                        alpha=alpha, series_idx=self._bar_series_idx))
        self._bar_series_idx += 1
        self._series_idx += 1
        return self

    def fill_between(self, x, y1, y2=0, *, color=None, alpha=0.15, label=None):
        xd = _convert(x)
        y1d = _convert(y1)
        y2d = _convert(y2)
        c = color or DEFAULT_COLORS[max(0, self._series_idx - 1) % len(DEFAULT_COLORS)]
        self._commands.append(_PlotCmd("fill_between", x=xd, y1=y1d, y2=y2d, color=c,
                                        alpha=alpha, label=label))
        return self

    def axhline(self, y, *, color="#707070", line_width=1, line_style="dashed", alpha=1.0):
        self._commands.append(_PlotCmd("hline", y=y, color=color, line_width=line_width,
                                        line_style=line_style, alpha=alpha))
        return self

    def axvline(self, x, *, color="#707070", line_width=1, line_style="dashed", alpha=1.0):
        self._commands.append(_PlotCmd("vline", x=x, color=color, line_width=line_width,
                                        line_style=line_style, alpha=alpha))
        return self

    def text(self, x, y, content, *, color="#d4d4d4", font_size=10, anchor="start"):
        self._commands.append(_PlotCmd("text", x=x, y=y, content=content, color=color,
                                        font_size=font_size, anchor=anchor))
        return self

    def annotate(self, text, xy, *, xytext=None, color="#d4d4d4", font_size=9, arrow_color="#707070"):
        self._commands.append(_PlotCmd("annotate", text=text, xy=xy, xytext=xytext,
                                        color=color, font_size=font_size, arrow_color=arrow_color))
        return self

    # ── Config methods ─────────────────────────────────────────────────

    def set_title(self, title: str):
        self._title = title
        return self

    def set_subtitle(self, subtitle: str):
        self._subtitle = subtitle
        return self

    def set_xticks(self, ticks):
        self._xticks = _convert(ticks)
        return self

    def set_yticks(self, ticks):
        self._yticks = _convert(ticks)
        return self

    def grid(self, visible: bool = True):
        self._grid = visible
        return self

    def legend(self, **kwargs):
        self._show_legend = True
        self._legend_kwargs = kwargs
        return self

    # ── Rendering ──────────────────────────────────────────────────────

    def render(self) -> str:
        """Render to SVG string."""
        return self._build_svg()

    def show(self):
        """Display inline in Jupyter/Colab."""
        svg = self.render()
        dark_html = f'<div style="background:#121212;padding:16px 8px;border-radius:8px">{svg}</div>'
        try:
            from IPython.display import HTML, display
            display(HTML(dark_html))
        except ImportError:
            print(svg)

    def _repr_html_(self):
        """Auto-display in Jupyter."""
        svg = self.render()
        return f'<div style="background:#121212;padding:16px 8px;border-radius:8px">{svg}</div>'

    # ── SVG Builder ────────────────────────────────────────────────────

    def _build_svg(self) -> str:
        pad = DEFAULT_PADDING
        inset = DEFAULT_INSET
        w, h = self.width, self.height

        pa_x = pad["left"] + inset
        pa_y = pad["top"] + inset
        pa_w = w - pad["left"] - pad["right"] - inset * 2
        pa_h = h - pad["top"] - pad["bottom"] - inset * 2

        # ── Collect data ranges ────────────────────────────────────────
        y_vals: List[float] = []
        x_nums: List[float] = []
        bar_cmds = [c for c in self._commands if c.kind in ("bar", "hist")]
        line_cmds = [c for c in self._commands if c.kind == "line"]
        scatter_cmds = [c for c in self._commands if c.kind == "scatter"]
        fill_cmds = [c for c in self._commands if c.kind == "fill_between"]
        hist_cmds = [c for c in self._commands if c.kind == "hist"]

        # Histogram bin computation
        hist_bars: List[dict] = []
        for cmd in hist_cmds:
            edges, counts = self._compute_hist_bins(cmd.data, cmd.bins)
            hist_bars.append({"edges": edges, "counts": counts, "cmd": cmd})
            y_vals.extend(counts)

        for cmd in line_cmds:
            y_vals.extend(cmd.y)
            if cmd.x:
                x_nums.extend(cmd.x)
        for cmd in scatter_cmds:
            y_vals.extend(cmd.y)
            x_nums.extend(cmd.x)
        for cmd in fill_cmds:
            if isinstance(cmd.y1, list):
                y_vals.extend(cmd.y1)
            if isinstance(cmd.y2, list):
                y_vals.extend(cmd.y2)
            elif isinstance(cmd.y2, (int, float)):
                y_vals.append(cmd.y2)
        for cmd in bar_cmds:
            if cmd.kind == "bar":
                y_vals.extend(cmd.y)

        if not y_vals:
            y_vals = [0, 1]
        y_min_data, y_max_data = min(y_vals), max(y_vals)
        if y_min_data == y_max_data:
            y_min_data -= 1
            y_max_data += 1

        # Y ticks
        if self._yticks:
            y_ticks = [float(t) for t in self._yticks]
            y_min = min(y_min_data, min(y_ticks))
            y_max = max(y_max_data, max(y_ticks))
        else:
            y_ticks = _compute_ticks(y_min_data, y_max_data)
            y_min = y_ticks[0]
            y_max = y_ticks[-1]

        y_range = y_max - y_min if y_max != y_min else 1

        def y_px(v: float) -> float:
            return pa_y + pa_h - ((v - y_min) / y_range) * pa_h

        # X range for numeric axes
        has_numeric_x = bool(x_nums) or bool(hist_bars)
        if x_nums:
            x_min_data, x_max_data = min(x_nums), max(x_nums)
        elif hist_bars:
            x_min_data = min(hb["edges"][0] for hb in hist_bars)
            x_max_data = max(hb["edges"][-1] for hb in hist_bars)
        else:
            x_min_data, x_max_data = 0, 1

        if has_numeric_x:
            if self._xticks and all(isinstance(t, (int, float)) for t in self._xticks):
                x_ticks_num = [float(t) for t in self._xticks]
                x_min = min(x_min_data, min(x_ticks_num))
                x_max = max(x_max_data, max(x_ticks_num))
            else:
                x_ticks_num = _compute_ticks(x_min_data, x_max_data)
                x_min = x_min_data
                x_max = x_max_data
        else:
            x_min, x_max = 0, 1
            x_ticks_num = []

        x_range = x_max - x_min if x_max != x_min else 1

        def x_px(v: float) -> float:
            return pa_x + ((v - x_min) / x_range) * pa_w

        # ── SVG parts ─────────────────────────────────────────────────
        parts: List[str] = []

        # Legend collection
        legend_entries: List[Tuple[str, str, str]] = []  # (color, label, type)

        # Title / Subtitle
        cur_y_top = 0.0
        if self._title:
            cur_y_top = 14
            parts.append(f'<text x="{pa_x}" y="{cur_y_top}" font-size="14" font-weight="500" '
                         f'font-family="\'EB Garamond\',Georgia,serif" letter-spacing="0.3" '
                         f'fill="#ffffff">{_esc(self._title)}</text>')
        if self._subtitle:
            cur_y_top += 14
            parts.append(f'<text x="{pa_x}" y="{cur_y_top}" font-size="10" font-weight="400" '
                         f'font-family="\'Inter\',sans-serif" letter-spacing="0.2" '
                         f'fill="#494949">{_esc(self._subtitle)}</text>')

        # Grid
        if self._grid:
            for yt in y_ticks:
                yp = y_px(yt)
                if pa_y <= yp <= pa_y + pa_h:
                    parts.append(f'<line x1="{pa_x}" y1="{yp:.1f}" x2="{pa_x + pa_w}" '
                                 f'y2="{yp:.1f}" stroke="rgba(255,255,255,0.06)" stroke-width="0.5"/>')

        # Y-axis labels
        for yt in y_ticks:
            yp = y_px(yt)
            parts.append(f'<text x="{pa_x - 4}" y="{yp + 3:.1f}" text-anchor="end" '
                         f'font-size="8" font-weight="500" font-family="\'Inter\',sans-serif" '
                         f'fill="#494949">{_esc(_fmt_val(yt))}</text>')

        # ── Render elements ────────────────────────────────────────────

        # Area / fill_between
        for cmd in fill_cmds:
            y1 = cmd.y1 if isinstance(cmd.y1, list) else [cmd.y1] * len(cmd.x)
            y2 = cmd.y2 if isinstance(cmd.y2, list) else [cmd.y2] * len(cmd.x)
            n = len(cmd.x)
            pts_top = []
            pts_bot = []
            for i in range(n):
                if has_numeric_x:
                    xp = x_px(cmd.x[i])
                else:
                    xp = pa_x + (i / max(n - 1, 1)) * pa_w
                pts_top.append(f"{xp:.1f},{y_px(y1[i]):.1f}")
                pts_bot.append(f"{xp:.1f},{y_px(y2[i]):.1f}")
            fwd = " ".join(f"{'M' if i == 0 else 'L'}{p}" for i, p in enumerate(pts_top))
            bwd = " ".join(f"L{p}" for p in reversed(pts_bot))
            parts.append(f'<path d="{fwd} {bwd} Z" fill="{cmd.color}" opacity="{cmd.alpha}"/>')
            if cmd.label:
                legend_entries.append((cmd.color, cmd.label, "line"))

        # Lines
        for cmd in line_cmds:
            n = len(cmd.y)
            pts = []
            for i in range(n):
                if cmd.x:
                    xp = x_px(cmd.x[i])
                elif self._xticks and isinstance(self._xticks[0], str):
                    xp = pa_x + (i / max(n - 1, 1)) * pa_w
                else:
                    xp = pa_x + (i / max(n - 1, 1)) * pa_w
                yp = y_px(cmd.y[i])
                pts.append(f"{'M' if i == 0 else 'L'}{xp:.1f},{yp:.1f}")

            path_d = " ".join(pts)
            da = _dash_array(cmd.line_style)
            da_attr = f' stroke-dasharray="{da}"' if da else ""
            parts.append(f'<path d="{path_d}" fill="none" stroke="{cmd.color}" '
                         f'stroke-width="{cmd.line_width}" stroke-linejoin="round"{da_attr} '
                         f'opacity="{cmd.alpha}"/>')

            # Optional area fill under line
            if cmd.fill_opacity and cmd.fill_opacity > 0:
                base_y = y_px(0) if y_min <= 0 <= y_max else pa_y + pa_h
                last_pt = pts[-1].split(",")
                first_pt = pts[0][1:].split(",")
                area_d = f"{path_d} L{last_pt[0][1:]},{base_y:.1f} L{first_pt[0]},{base_y:.1f} Z"
                parts.append(f'<path d="{area_d}" fill="{cmd.color}" opacity="{cmd.fill_opacity}"/>')

            if cmd.label:
                legend_entries.append((cmd.color, cmd.label, "line"))

        # Bars (grouped)
        if bar_cmds and not hist_bars:
            num_series = len([c for c in bar_cmds if c.kind == "bar"])
            all_labels = bar_cmds[0].x_labels if bar_cmds[0].kind == "bar" else []
            n_bars = len(all_labels) if all_labels else (len(bar_cmds[0].y) if bar_cmds else 0)
            bar_w = 20
            pair_gap = 3
            group_w = pa_w / max(n_bars, 1)
            pair_w = bar_w * num_series + pair_gap * (num_series - 1) if num_series > 1 else bar_w

            si = 0
            for cmd in bar_cmds:
                if cmd.kind != "bar":
                    continue
                style = BAR_STYLES[si % len(BAR_STYLES)]
                grad_id = f"bg-{si}"
                parts.append(f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
                             f'<stop offset="0%" stop-color="{style["grad_top"]}"/>'
                             f'<stop offset="100%" stop-color="{style["grad_bottom"]}"/>'
                             f'</linearGradient></defs>')

                for i, val in enumerate(cmd.y):
                    group_pad = (group_w - pair_w) / 2
                    bx = pa_x + i * group_w + group_pad + si * (bar_w + pair_gap)
                    bot = max(y_min, 0)
                    top_val = val
                    by_top = y_px(top_val)
                    by_bot = y_px(bot)
                    by = min(by_top, by_bot)
                    bh = max(1, abs(by_top - by_bot))
                    parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w}" '
                                 f'height="{bh:.1f}" fill="{style["fill"]}"/>')
                    parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w}" '
                                 f'height="{bh:.1f}" fill="url(#{grad_id})" opacity="0.4"/>')

                if cmd.label:
                    legend_entries.append((cmd.color, cmd.label, "bar"))
                si += 1

            # X-axis labels for bars
            if all_labels:
                for i, lbl in enumerate(all_labels):
                    cx = pa_x + (i + 0.5) * group_w
                    parts.append(f'<text x="{cx:.1f}" y="{h - 4}" text-anchor="middle" '
                                 f'font-size="8" font-weight="500" font-family="\'Inter\',sans-serif" '
                                 f'fill="#494949">{_esc(str(lbl))}</text>')

        # Histogram bars
        for hb in hist_bars:
            edges = hb["edges"]
            counts = hb["counts"]
            cmd = hb["cmd"]
            style = BAR_STYLES[cmd.series_idx % len(BAR_STYLES)]
            grad_id = f"hg-{cmd.series_idx}"
            parts.append(f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
                         f'<stop offset="0%" stop-color="{style["grad_top"]}"/>'
                         f'<stop offset="100%" stop-color="{style["grad_bottom"]}"/>'
                         f'</linearGradient></defs>')

            for i in range(len(counts)):
                bx_l = x_px(edges[i])
                bx_r = x_px(edges[i + 1])
                bw = bx_r - bx_l
                by_top = y_px(counts[i])
                by_bot = y_px(0) if y_min <= 0 else pa_y + pa_h
                by = min(by_top, by_bot)
                bh = max(0.5, abs(by_top - by_bot))
                parts.append(f'<rect x="{bx_l:.1f}" y="{by:.1f}" width="{bw:.1f}" '
                             f'height="{bh:.1f}" fill="{style["fill"]}"/>')
                parts.append(f'<rect x="{bx_l:.1f}" y="{by:.1f}" width="{bw:.1f}" '
                             f'height="{bh:.1f}" fill="url(#{grad_id})" opacity="0.4"/>')

            if cmd.label:
                legend_entries.append((cmd.color, cmd.label, "bar"))

        # Scatter
        for cmd in scatter_cmds:
            for i in range(len(cmd.x)):
                xp = x_px(cmd.x[i])
                yp = y_px(cmd.y[i])
                r = math.sqrt(cmd.size) if isinstance(cmd.size, (int, float)) else 2
                parts.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="{r:.1f}" '
                             f'fill="{cmd.color}" opacity="{cmd.alpha}"/>')
            if cmd.label:
                legend_entries.append((cmd.color, cmd.label, "scatter"))

        # HLine / VLine
        for cmd in self._commands:
            if cmd.kind == "hline":
                yp = y_px(cmd.y)
                da = _dash_array(cmd.line_style)
                da_attr = f' stroke-dasharray="{da}"' if da else ""
                parts.append(f'<line x1="{pa_x}" y1="{yp:.1f}" x2="{pa_x + pa_w}" '
                             f'y2="{yp:.1f}" stroke="{cmd.color}" stroke-width="{cmd.line_width}"{da_attr}/>')
            elif cmd.kind == "vline":
                xp = x_px(cmd.x)
                da = _dash_array(cmd.line_style)
                da_attr = f' stroke-dasharray="{da}"' if da else ""
                parts.append(f'<line x1="{xp:.1f}" y1="{pa_y}" x2="{xp:.1f}" '
                             f'y2="{pa_y + pa_h}" stroke="{cmd.color}" stroke-width="{cmd.line_width}"{da_attr}/>')
            elif cmd.kind == "text":
                parts.append(f'<text x="{cmd.x}" y="{cmd.y}" text-anchor="{cmd.anchor}" '
                             f'font-size="{cmd.font_size}" font-family="\'Inter\',sans-serif" '
                             f'fill="{cmd.color}">{_esc(cmd.content)}</text>')
            elif cmd.kind == "annotate":
                if cmd.xytext:
                    parts.append(f'<line x1="{cmd.xytext[0]}" y1="{cmd.xytext[1]}" '
                                 f'x2="{cmd.xy[0]}" y2="{cmd.xy[1]}" stroke="{cmd.arrow_color}" stroke-width="1"/>')
                tx = cmd.xytext[0] if cmd.xytext else cmd.xy[0]
                ty = cmd.xytext[1] if cmd.xytext else cmd.xy[1]
                parts.append(f'<text x="{tx}" y="{ty}" font-size="{cmd.font_size}" '
                             f'font-family="\'Inter\',sans-serif" fill="{cmd.color}">{_esc(cmd.text)}</text>')

        # X-axis labels (for non-bar charts)
        if not bar_cmds or hist_bars:
            if self._xticks and isinstance(self._xticks[0], str):
                # String labels
                n = len(self._xticks)
                for i, lbl in enumerate(self._xticks):
                    xp = pa_x + (i / max(n - 1, 1)) * pa_w
                    parts.append(f'<text x="{xp:.1f}" y="{h - 4}" text-anchor="middle" '
                                 f'font-size="8" font-weight="500" font-family="\'Inter\',sans-serif" '
                                 f'fill="#494949">{_esc(str(lbl))}</text>')
            elif has_numeric_x:
                # Use histogram edges or computed ticks
                if hist_bars:
                    edges = hist_bars[0]["edges"]
                    max_labels = 8
                    if len(edges) <= max_labels:
                        tick_vals = edges
                    else:
                        step = math.ceil(len(edges) / max_labels)
                        tick_vals = [e for i, e in enumerate(edges) if i % step == 0]
                        if tick_vals[-1] != edges[-1]:
                            tick_vals.append(edges[-1])
                else:
                    tick_vals = x_ticks_num

                for tv in tick_vals:
                    xp = x_px(tv)
                    if pa_x - 2 <= xp <= pa_x + pa_w + 2:
                        parts.append(f'<text x="{xp:.1f}" y="{h - 4}" text-anchor="middle" '
                                     f'font-size="8" font-weight="500" font-family="\'Inter\',sans-serif" '
                                     f'fill="#494949">{_esc(_fmt_val(tv))}</text>')

        # Legend
        legend_extra_h = 0
        if self._show_legend and legend_entries:
            font_size = 9
            gap_x = font_size * 2.5
            item_h = font_size + 4
            total_w = sum(font_size + 4 + len(e[1]) * font_size * 0.55 + gap_x for e in legend_entries) - gap_x
            lx = pa_x + (pa_w - total_w) / 2
            ly = pa_y + pa_h + 56
            legend_extra_h = font_size + 72
            cx = lx
            for color, label, typ in legend_entries:
                sw = font_size
                if typ == "bar":
                    parts.append(f'<rect x="{cx:.1f}" y="{ly + 2:.1f}" width="{sw}" '
                                 f'height="{item_h - 4}" rx="2" fill="{color}"/>')
                else:
                    parts.append(f'<line x1="{cx:.1f}" y1="{ly + item_h / 2:.1f}" '
                                 f'x2="{cx + sw:.1f}" y2="{ly + item_h / 2:.1f}" '
                                 f'stroke="{color}" stroke-width="2"/>')
                label_x = cx + sw + 4
                parts.append(f'<text x="{label_x:.1f}" y="{ly + item_h / 2 + 1:.1f}" '
                             f'dominant-baseline="middle" font-size="{font_size}" '
                             f'font-family="\'Inter\',sans-serif" fill="#8f8f8f">{_esc(label)}</text>')
                cx += sw + 4 + len(label) * font_size * 0.55 + gap_x

        total_h = h + legend_extra_h
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {total_h}" '
               f'width="{w}" height="{total_h}" style="font-family:\'Inter\',sans-serif">\n'
               + "\n".join(parts) + "\n</svg>")
        return svg

    @staticmethod
    def _compute_hist_bins(data: list, bins: Union[int, list] = 10):
        sorted_data = sorted(data)
        d_min, d_max = sorted_data[0], sorted_data[-1]
        if isinstance(bins, list):
            edges = bins
        else:
            step = (d_max - d_min) / bins
            edges = [d_min + i * step for i in range(bins + 1)]
        counts = [0] * (len(edges) - 1)
        for v in data:
            for i in range(len(edges) - 1):
                if v >= edges[i] and (v < edges[i + 1] or (i == len(edges) - 2 and v == edges[i + 1])):
                    counts[i] += 1
                    break
        return edges, counts
