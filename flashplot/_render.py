"""
SVG and HTML renderers for Flash plot scenes.
Generates animated SVG with CSS keyframes for Jupyter/Colab display.
"""

from __future__ import annotations
import math
from typing import List

from ._core import dash_array, get_theme
from ._figure import (
    Scene, SubplotScene, PlotElement,
    LinePlotElement, AreaPlotElement, BarPlotElement, ScatterPlotElement,
    HLinePlotElement, VLinePlotElement, TextPlotElement, AnnotationPlotElement,
)


# ── Sparkle dot positions (from Figma) ─────────────────────────────────

SPARKLE_DOTS = [
    (0.75, 0.761, 1), (0.315, 0.843, 1), (0.675, 0.780, 0.5),
    (0.459, 0.846, 0.5), (0.238, 0.685, 0.75), (0.45, 0.649, 1),
    (0.509, 0.870, 1), (0.558, 0.106, 1), (0.225, 0.623, 0.5),
    (0.331, 0.132, 0.5), (0.475, 0.668, 0.5), (0.626, 0.862, 0.5),
    (0.685, 0.107, 0.5), (0.138, 0.632, 0.75), (0.368, 0.147, 0.75),
]


# ── CSS Animation Keyframes ─────────────────────────────────────────────

_CSS_ANIMATIONS = """
/* Phase 1: Grid draw-in */
@keyframes fp-gridDraw { from { stroke-dashoffset: var(--fp-len); } to { stroke-dashoffset: 0; } }

/* Phase 2: Label appear */
@keyframes fp-labelFadeY { from { opacity: 0; transform: translate(8px, 0); } to { opacity: 1; transform: translate(0, 0); } }
@keyframes fp-labelFadeX { from { opacity: 0; transform: translate(0, -6px); } to { opacity: 1; transform: translate(0, 0); } }

/* Phase 3: Data elements */
@keyframes fp-lineDraw { from { stroke-dashoffset: 2000; } to { stroke-dashoffset: 0; } }
@keyframes fp-areaFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes fp-barGrow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@keyframes fp-scatterPop { from { opacity: 0; r: 0; } to { opacity: 1; } }
@keyframes fp-refFade { from { opacity: 0; } to { opacity: 1; } }

/* Shimmer: brightness wave across labels */
@keyframes fp-shimmer {
  0%, 100% { fill: var(--fp-base); }
  30% { fill: #787878; }
  50% { fill: #c4c4c4; }
  70% { fill: #787878; }
}

/* Bar sweep: sequential highlight pulse */
@keyframes fp-barSweep {
  0% { opacity: 0; }
  30% { opacity: 1; }
  100% { opacity: 0; }
}

/* Glow drift animations for bar layers */
@keyframes fp-glowDrift1 {
  0%, 100% { transform: translate(0, 0); }
  30% { transform: translate(0.5px, -0.4px); }
  60% { transform: translate(-0.4px, 0.5px); }
  80% { transform: translate(0.3px, 0.2px); }
}
@keyframes fp-glowDrift2 {
  0%, 100% { transform: translate(0, 0); }
  35% { transform: translate(-0.4px, 0.4px); }
  65% { transform: translate(0.5px, -0.3px); }
  85% { transform: translate(-0.2px, -0.4px); }
}
@keyframes fp-glowDrift3 {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(0.2px, 0.5px); }
  55% { transform: translate(-0.5px, -0.2px); }
  80% { transform: translate(0.4px, -0.4px); }
}

/* Sparkle float animations for bar dots */
@keyframes fp-sparkleFloat1 {
  0%, 100% { transform: translate(0, 0); opacity: 0.85; }
  35% { transform: translate(0.5px, -0.8px); opacity: 1; }
  65% { transform: translate(-0.3px, -1.2px); opacity: 0.7; }
  85% { transform: translate(0.4px, -0.4px); opacity: 0.95; }
}
@keyframes fp-sparkleFloat2 {
  0%, 100% { transform: translate(0, 0); opacity: 0.8; }
  30% { transform: translate(-0.6px, -1px); opacity: 1; }
  60% { transform: translate(0.4px, -1.5px); opacity: 0.65; }
  80% { transform: translate(-0.2px, -0.5px); opacity: 0.9; }
}
@keyframes fp-sparkleFloat3 {
  0%, 100% { transform: translate(0, 0); opacity: 0.9; }
  25% { transform: translate(0.3px, -1.2px); opacity: 0.7; }
  50% { transform: translate(-0.5px, -0.6px); opacity: 1; }
  75% { transform: translate(0.4px, -1px); opacity: 0.75; }
}

/* ── Bar hover interactions ─────────────────────────────────────────── */
.fp-bar { cursor: pointer; }
.fp-bar-glow { opacity: 0; transition: opacity 0.35s ease-out; }
.fp-bar:hover .fp-bar-glow { opacity: 1; transition: opacity 0.15s ease-in; }
.fp-bar .fp-drift { animation: none !important; }
.fp-bar:hover .fp-drift1 { animation: fp-glowDrift1 4s ease-in-out infinite !important; }
.fp-bar:hover .fp-drift2 { animation: fp-glowDrift2 3.5s ease-in-out 0.3s infinite !important; }
.fp-bar:hover .fp-drift3 { animation: fp-glowDrift3 3.8s ease-in-out 0.2s infinite !important; }
.fp-bar:hover .fp-drift1b { animation: fp-glowDrift1 4.2s ease-in-out 0.5s infinite !important; }
.fp-bar .fp-sparkle { animation: none !important; }
.fp-bar:hover .fp-sparkle { animation: var(--fp-sparkle-anim) !important; }

/* ── Hover tooltips ─────────────────────────────────────────────────── */
.fp-tip { pointer-events: all; }
.fp-tip-content { opacity: 0; pointer-events: none; transition: opacity 0.12s ease; }
.fp-tip:hover .fp-tip-content { opacity: 1; }
.fp-bar:hover .fp-tip-content { opacity: 1; }
"""


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _fmt_val(v: float) -> str:
    """Format a value for tooltip display."""
    if abs(v) >= 1e6:
        return f"{v:.2e}"
    if abs(v) >= 100:
        return f"{v:,.0f}"
    if abs(v) >= 1:
        return f"{v:,.2f}"
    if v == 0:
        return "0"
    return f"{v:.4g}"


# ── Tooltip Builder ────────────────────────────────────────────────────

def _build_tooltip_box(
    header: str, entries: list, tx: float, ty: float,
    w: float, bounds_w: float, pa_y: float,
) -> str:
    """Build a tooltip SVG group.
    entries: list of (color, label, value_str)
    """
    row_h = 18
    header_h = 22
    pad = 8
    total_h = pad + header_h + len(entries) * row_h + pad

    # Flip left if tooltip would overflow right
    if tx + w + 12 > bounds_w:
        tx = tx - w - 10
    else:
        tx = tx + 10

    # Keep tooltip in vertical bounds
    if ty + total_h > pa_y + 200:
        ty = max(pa_y, ty - total_h - 10)

    lines = []
    lines.append(f'<g transform="translate({tx:.1f},{ty:.1f})">')
    lines.append(f'  <rect width="{w}" height="{total_h}" rx="5" fill="#1a1a1a" stroke="#2a2a2a" stroke-width="0.5"/>')
    lines.append(f'  <text x="8" y="{pad + 11}" fill="#808080" font-size="9" font-weight="500" '
                 f'font-family="\'Inter\',sans-serif">{_esc(header)}</text>')
    lines.append(f'  <line x1="8" y1="{pad + header_h - 4}" x2="{w - 8}" y2="{pad + header_h - 4}" '
                 f'stroke="#2a2a2a" stroke-width="0.5"/>')

    for idx, (color, label, val_str) in enumerate(entries):
        ry = pad + header_h + idx * row_h + 12
        lines.append(f'  <circle cx="14" cy="{ry - 3}" r="3" fill="{color}"/>')
        lines.append(f'  <text x="22" y="{ry}" fill="#a0a0a0" font-size="9" '
                     f'font-family="\'Inter\',sans-serif">{_esc(label)}</text>')
        lines.append(f'  <text x="{w - 8}" y="{ry}" text-anchor="end" fill="#e0e0e0" '
                     f'font-size="9" font-weight="600" font-family="\'Inter\',sans-serif">{_esc(val_str)}</text>')

    lines.append("</g>")
    return "\n".join(lines)


# ── Hover Overlay Builders ─────────────────────────────────────────────

def _build_line_hover_overlay(sp: SubplotScene, uid: str) -> str:
    """Build hover overlay for line charts — one tooltip per x-position showing all series."""
    pa = sp.plot_area
    w, h = sp.bounds.w, sp.bounds.h
    line_els = [el for el in sp.elements if isinstance(el, LinePlotElement) and el.points]
    if not line_els:
        return ""

    n_points = len(line_els[0].points)
    if n_points == 0:
        return ""

    # Build x labels from ticks
    tick_labels = {round(t.position, 1): t.label for t in sp.x_axis.ticks}

    lines = []
    for i in range(n_points):
        px = line_els[0].points[i].x

        # Compute strip boundaries (midpoint between adjacent points)
        if n_points == 1:
            strip_l, strip_r = pa.x, pa.x + pa.w
        else:
            strip_l = px - (px - line_els[0].points[i - 1].x) / 2 if i > 0 else pa.x
            strip_r = px + (line_els[0].points[i + 1].x - px) / 2 if i < n_points - 1 else pa.x + pa.w

        # Find closest x-tick label
        x_label = str(i)
        best_dist = float("inf")
        for tp, tl in tick_labels.items():
            d = abs(tp - px)
            if d < best_dist:
                best_dist = d
                x_label = tl

        # Build entries for all line series at this index
        entries = []
        for el in line_els:
            if i < len(el.data_values):
                label = el.label or el.color
                entries.append((el.color, label, _fmt_val(el.data_values[i])))

        tooltip_w = 120

        lines.append(f'<g class="fp-tip">')
        # Hit area strip
        lines.append(f'  <rect x="{strip_l:.1f}" y="{pa.y:.1f}" width="{strip_r - strip_l:.1f}" '
                     f'height="{pa.h:.1f}" fill="transparent"/>')

        lines.append(f'  <g class="fp-tip-content">')
        # Crosshair
        lines.append(f'    <line x1="{px:.1f}" y1="{pa.y:.1f}" x2="{px:.1f}" y2="{pa.y + pa.h:.1f}" '
                     f'stroke="#3a3a3a" stroke-width="0.5" stroke-dasharray="3 2"/>')
        # Dots on each line
        for el in line_els:
            if i < len(el.points):
                py = el.points[i].y
                lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#121212" '
                             f'stroke="{el.color}" stroke-width="1.2"/>')
                lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="1.5" fill="{el.color}"/>')
        # Tooltip
        lines.append(_build_tooltip_box(x_label, entries, px, pa.y + 4, tooltip_w, w, pa.y))
        lines.append("  </g>")
        lines.append("</g>")

    return "\n".join(lines)


def _build_bar_tooltip(bar, label, x_label, value, color, uid, pa, bounds_w) -> str:
    """Build a tooltip that appears on bar hover."""
    entries = [(color, label or "Value", _fmt_val(value))]
    tx = bar.x + bar.width / 2
    ty = bar.y - 8
    tooltip_w = 110

    lines = []
    lines.append(f'<g class="fp-tip-content">')
    lines.append(_build_tooltip_box(x_label, entries, tx, ty, tooltip_w, bounds_w, pa.y))
    lines.append("</g>")
    return "\n".join(lines)


def _build_scatter_hover_overlay(sp: SubplotScene, uid: str) -> str:
    """Build hover overlay for scatter plots — one tooltip per point."""
    pa = sp.plot_area
    w = sp.bounds.w
    scatter_els = [el for el in sp.elements if isinstance(el, ScatterPlotElement)]
    if not scatter_els:
        return ""

    lines = []
    for el in scatter_els:
        for i, (px, py, sz) in enumerate(el.points):
            r = max(math.sqrt(sz), 4)
            x_val, y_val = el.data_xy[i] if i < len(el.data_xy) else (0, 0)
            label = el.label or "Point"
            entries = [
                (el.color, "x", _fmt_val(x_val)),
                (el.color, "y", _fmt_val(y_val)),
            ]
            tooltip_w = 100

            lines.append(f'<g class="fp-tip">')
            lines.append(f'  <circle cx="{px:.1f}" cy="{py:.1f}" r="{r + 3:.1f}" fill="transparent"/>')
            lines.append(f'  <g class="fp-tip-content">')
            # Highlight ring
            lines.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="{r + 1:.1f}" '
                         f'fill="none" stroke="{el.color}" stroke-width="1.5" stroke-opacity="0.6"/>')
            lines.append(_build_tooltip_box(label, entries, px, py - 8, tooltip_w, w, pa.y))
            lines.append("  </g>")
            lines.append("</g>")

    return "\n".join(lines)


# ── Subplot Renderer ────────────────────────────────────────────────────

def _render_subplot(sp: SubplotScene, animate: bool, uid: str, hover: bool = True) -> str:
    pa = sp.plot_area
    lines: List[str] = []
    w, h = sp.bounds.w, sp.bounds.h
    theme = get_theme()

    # Timing constants
    T_LABELS = 0.675
    T_DATA = 1.28
    T_SHIMMER = 2.5
    SHIMMER_STEP = 0.08
    SHIMMER_DUR = 0.24

    bar_count = 0
    for el in sp.elements:
        if isinstance(el, BarPlotElement):
            bar_count = max(bar_count, len(el.bars))
    bar_sweep_start = T_DATA + 0.81 + bar_count * 0.054
    bar_sweep_step = 0.12

    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
                 f'style="width:100%;height:auto;display:block;font-family:\'Inter\',sans-serif;">')

    # Inline styles for hover (ensures they work inside SVG in all contexts)
    if hover:
        lines.append("<style>")
        lines.append(".fp-tip-content{opacity:0;pointer-events:none;transition:opacity .12s ease}")
        lines.append(".fp-tip:hover .fp-tip-content{opacity:1}")
        lines.append(".fp-bar:hover .fp-tip-content{opacity:1}")
        lines.append("</style>")

    # Defs
    lines.append("<defs>")

    # Per-area gradients using each area's own color
    area_grad_ids = {}
    for a_idx, el in enumerate(e for e in sp.elements if isinstance(e, AreaPlotElement)):
        gid = f"areaGrad-{uid}-{a_idx}"
        area_grad_ids[id(el)] = gid
        lines.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">')
        lines.append(f'  <stop offset="0%" stop-color="{el.color}" stop-opacity="0.15"/>')
        lines.append(f'  <stop offset="100%" stop-color="{el.color}" stop-opacity="0.05"/>')
        lines.append("</linearGradient>")

    bar_series = set()
    for el in sp.elements:
        if isinstance(el, BarPlotElement):
            bar_series.add(el.series_index)
    for si in bar_series:
        for name, sigma in [("SideGlow", 5), ("TopHL", 4), ("BotGlow", 5), ("LeftEdge", 5), ("BotWhite", 2.25), ("TopWhite", 2.25)]:
            fid = f"bar{name}-{uid}-{si}"
            lines.append(f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">')
            lines.append(f'  <feGaussianBlur in="SourceGraphic" stdDeviation="{sigma}"/>')
            lines.append("</filter>")
    lines.append("</defs>")

    # ── Title & Subtitle ─────────────────────────────────────────────────
    if sp.title and sp.title_style:
        ty = pa.y - 8
        if sp.subtitle:
            ty -= 16
        anim_style = ""
        if animate:
            anim_style = f' style="animation:fp-refFade 0.5s ease 0.2s both"'
        lines.append(f'<text x="{pa.x:.1f}" y="{ty:.1f}" '
                     f'font-size="{sp.title_style.font_size}" font-weight="{sp.title_style.font_weight}" '
                     f'font-family="{_esc(sp.title_style.font_family)}" '
                     f'fill="{sp.title_style.color}"{anim_style}>{_esc(sp.title)}</text>')
    if sp.subtitle and sp.subtitle_style:
        sy = pa.y - 6
        anim_style = ""
        if animate:
            anim_style = f' style="animation:fp-refFade 0.5s ease 0.35s both"'
        lines.append(f'<text x="{pa.x:.1f}" y="{sy:.1f}" '
                     f'font-size="{sp.subtitle_style.font_size}" font-weight="{sp.subtitle_style.font_weight}" '
                     f'font-family="{_esc(sp.subtitle_style.font_family)}" '
                     f'fill="{sp.subtitle_style.color}"{anim_style}>{_esc(sp.subtitle)}</text>')

    # ── Grid ────────────────────────────────────────────────────────────
    for i, gl in enumerate(sp.grid.lines):
        ln = math.sqrt((gl.x2 - gl.x1) ** 2 + (gl.y2 - gl.y1) ** 2)
        anim = ""
        if animate:
            anim = (f' style="--fp-len:{ln:.1f};stroke-dasharray:{ln:.1f};'
                    f'animation:fp-gridDraw 0.675s cubic-bezier(0.22,1,0.36,1) {i*0.08:.2f}s both"')
        lines.append(f'<line x1="{gl.x1:.1f}" y1="{gl.y1:.1f}" x2="{gl.x2:.1f}" y2="{gl.y2:.1f}" '
                     f'stroke="{gl.color}" stroke-width="{gl.width}"{anim}/>')

    # ── Y labels (with shimmer) ────────────────────────────────────────
    for i, t in enumerate(sp.y_axis.ticks):
        ts = sp.y_axis.tick_style
        anim_style = ""
        if animate:
            fade = f'fp-labelFadeY 0.35s ease {T_LABELS + i*0.04:.2f}s both'
            shimmer_delay = T_SHIMMER + i * SHIMMER_STEP
            shimmer = f'fp-shimmer {SHIMMER_DUR}s ease {shimmer_delay:.2f}s 1'
            anim_style = f'--fp-base:{ts.color};animation:{fade},{shimmer};'
        lines.append(f'<text x="{pa.x - 4:.1f}" y="{t.position + 3:.1f}" text-anchor="end" '
                     f'font-size="{ts.font_size}" font-weight="{ts.font_weight}" '
                     f'font-family="{_esc(ts.font_family)}" letter-spacing="{ts.letter_spacing}" '
                     f'fill="{ts.color}" style="{anim_style}">{_esc(t.label)}</text>')

    # ── X labels (with shimmer) ────────────────────────────────────────
    for i, t in enumerate(sp.x_axis.ticks):
        ts = sp.x_axis.tick_style
        anim_style = ""
        if animate:
            fade = f'fp-labelFadeX 0.35s ease {T_LABELS + i*0.03:.2f}s both'
            shimmer_delay = T_SHIMMER + i * SHIMMER_STEP
            shimmer = f'fp-shimmer {SHIMMER_DUR}s ease {shimmer_delay:.2f}s 1'
            anim_style = f'--fp-base:{ts.color};animation:{fade},{shimmer};'
        lines.append(f'<text x="{t.position:.1f}" y="{h - 4:.1f}" text-anchor="middle" '
                     f'font-size="{ts.font_size}" font-weight="{ts.font_weight}" '
                     f'font-family="{_esc(ts.font_family)}" letter-spacing="{ts.letter_spacing}" '
                     f'fill="{ts.color}" style="{anim_style}">{_esc(t.label)}</text>')

    # ── Plot elements ───────────────────────────────────────────────────
    line_idx = 0
    area_idx = 0
    # Collect bar tooltip data to render in a top-layer overlay (z-index fix)
    for el in sp.elements:
        if isinstance(el, AreaPlotElement):
            anim_style = ""
            if animate:
                anim_style = f'animation:fp-areaFade 1.08s ease {T_DATA + area_idx*0.135:.2f}s both;'
            gid = area_grad_ids.get(id(el), f"areaGrad-{uid}-0")
            lines.append(f'<path d="{el.path}" fill="url(#{gid})" opacity="{el.alpha}" style="{anim_style}"/>')
            area_idx += 1

        elif isinstance(el, LinePlotElement):
            da = dash_array(el.line_style)
            if animate:
                lines.append(f'<path d="{el.path}" fill="none" stroke="{el.color}" '
                             f'stroke-width="{el.line_width}" stroke-linejoin="round" '
                             f'stroke-dasharray="2000" opacity="{el.alpha}" '
                             f'style="animation:fp-lineDraw 1.89s cubic-bezier(0.22,1,0.36,1) {T_DATA + line_idx*0.2:.2f}s both"/>')
                if da and el.line_style != "solid":
                    lines.append(f'<path d="{el.path}" fill="none" stroke="{el.color}" '
                                 f'stroke-width="{el.line_width}" stroke-linejoin="round" '
                                 f'stroke-dasharray="{da}" opacity="{el.alpha}" '
                                 f'style="animation:fp-areaFade 0.3s ease {T_DATA + line_idx*0.2 + 1.89:.2f}s both"/>')
            else:
                extra = f' stroke-dasharray="{da}"' if da else ""
                lines.append(f'<path d="{el.path}" fill="none" stroke="{el.color}" '
                             f'stroke-width="{el.line_width}" stroke-linejoin="round" '
                             f'opacity="{el.alpha}"{extra}/>')
            line_idx += 1

        elif isinstance(el, BarPlotElement):
            si = el.series_index
            st = theme.bar_styles[si % len(theme.bar_styles)]
            for bar in el.bars:
                delay = T_DATA + bar.index * 0.054
                grow_style = ""
                if animate:
                    grow_style = f'transform-origin:{bar.x + bar.width/2:.1f}px {pa.y + pa.h:.1f}px;animation:fp-barGrow 0.81s cubic-bezier(0.22,1,0.36,1) {delay:.2f}s both;'

                lines.append(f'<g class="fp-bar">')
                lines.append(f'  <rect x="{bar.x:.1f}" y="{bar.y:.1f}" width="{bar.width:.1f}" height="{bar.height:.1f}" '
                             f'fill="{theme.bar_default_fill}" style="{grow_style}"/>')

                clip_id = f"bc-{uid}-{si}-{bar.index}"
                lines.append(f'  <clipPath id="{clip_id}"><rect x="{bar.x:.1f}" y="{bar.y:.1f}" width="{bar.width:.1f}" height="{bar.height:.1f}" style="{grow_style}"/></clipPath>')

                sweep_style = ""
                if animate:
                    sweep_delay = bar_sweep_start + bar.index * bar_sweep_step
                    sweep_style = f' style="animation:fp-barSweep 0.4s ease {sweep_delay:.2f}s 1"'

                lines.append(f'  <g class="fp-bar-glow" clip-path="url(#{clip_id})"{sweep_style}>')

                lines.append(f'    <rect x="{bar.x:.1f}" y="{bar.y:.1f}" width="{bar.width:.1f}" height="{bar.height:.1f}" fill="{st.fill}" style="{grow_style}"/>')

                sc = lambda hv: (hv / 134) * bar.height
                bx, bw = bar.x, bar.width
                ay, ah = bar.y, bar.height

                lines.append(f'    <g class="fp-drift fp-drift1" filter="url(#barSideGlow-{uid}-{si})">')
                lines.append(f'      <ellipse cx="{bx + bw * 0.5:.1f}" cy="{ay + ah * 0.5:.1f}" rx="{bw * 0.55:.1f}" ry="{ah * 0.45:.1f}" fill="{st.side_glow}"/>')
                lines.append("    </g>")

                lines.append(f'    <g class="fp-drift fp-drift2" filter="url(#barTopHL-{uid}-{si})">')
                lines.append(f'      <rect x="{bx+bw*0.05:.1f}" y="{ay+sc(1):.1f}" width="{bw*0.9:.1f}" height="{sc(8):.1f}" rx="2" fill="{st.top_glow}"/>')
                lines.append("    </g>")

                lines.append(f'    <g class="fp-drift fp-drift3" filter="url(#barBotGlow-{uid}-{si})">')
                lines.append(f'      <path d="M{bx+bw*0.05} {ay+ah-sc(8.2)} C{bx+bw*0.05} {ay+ah-sc(9.2)} {bx+bw*0.05} {ay+ah-sc(4)} {bx+bw*0.17} {ay+ah-sc(1.5)} C{bx+bw*0.28} {ay+ah+sc(0.8)} {bx+bw*0.72} {ay+ah+sc(0.8)} {bx+bw*0.83} {ay+ah-sc(1.5)} C{bx+bw*0.95} {ay+ah-sc(4)} {bx+bw*0.95} {ay+ah-sc(9.2)} {bx+bw*0.95} {ay+ah-sc(8.2)} V{ay+ah} H{bx+bw*0.05} V{ay+ah-sc(8.2)}Z" fill="{st.bottom_glow}"/>')
                lines.append("    </g>")

                lines.append(f'    <g class="fp-drift fp-drift1b" filter="url(#barLeftEdge-{uid}-{si})">')
                lines.append(f'      <path d="M{bx-bw*0.01} {ay+sc(4)} C{bx+bw*0.045} {ay+sc(4)} {bx+bw*0.045} {ay+sc(4)} {bx+bw*0.045} {ay+sc(8)} V{ay+ah-sc(8)} C{bx+bw*0.045} {ay+ah-sc(4)} {bx-bw*0.01} {ay+ah-sc(2)} {bx-bw*0.01} {ay+ah} V{ay+sc(4)}Z" fill="{st.left_edge}"/>')
                lines.append("    </g>")

                for d_idx, (dcx, dcy, dr) in enumerate(SPARKLE_DOTS):
                    float_name = ["fp-sparkleFloat1", "fp-sparkleFloat2", "fp-sparkleFloat3"][d_idx % 3]
                    dur = 2.5 + (d_idx % 5) * 0.5
                    sp_delay = (d_idx * 0.2) % 1.5
                    sp_var = f'--fp-sparkle-anim:{float_name} {dur}s ease-in-out {sp_delay:.1f}s infinite;'
                    lines.append(f'    <circle class="fp-sparkle" cx="{bx + dcx * bw:.1f}" cy="{ay + dcy * ah:.1f}" r="{dr}" '
                                 f'fill="{st.sparkle}" style="{sp_var}"/>')

                lines.append(f'    <g filter="url(#barBotWhite-{uid}-{si})">')
                lines.append(f'      <path d="M{bx} {ay+ah-sc(3.5)} L{bx+bw*0.5} {ay+ah-sc(1.5)} L{bx+bw} {ay+ah-sc(3.5)} V{ay+ah} H{bx} V{ay+ah-sc(3.5)}Z" fill="white" fill-opacity="0.8"/>')
                lines.append("    </g>")
                lines.append(f'    <g filter="url(#barTopWhite-{uid}-{si})">')
                lines.append(f'      <path d="M{bx} {ay+sc(3.5)} L{bx+bw*0.5} {ay+sc(1.5)} L{bx+bw} {ay+sc(3.5)} V{ay} H{bx} V{ay+sc(3.5)}Z" fill="white" fill-opacity="0.8"/>')
                lines.append("    </g>")

                lines.append("  </g>")  # close fp-bar-glow

                # Hit area for hover
                lines.append(f'  <rect x="{bar.x - 2:.1f}" y="{bar.y - 2:.1f}" width="{bar.width + 4:.1f}" height="{bar.height + 4:.1f}" '
                             f'fill="transparent" opacity="0"/>')

                # Tooltip inside fp-bar so hover triggers both glow + tooltip
                if hover:
                    x_label = el.x_labels[bar.index] if bar.index < len(el.x_labels) else str(bar.index)
                    title_text = f"{x_label}: {_fmt_val(bar.value)}"
                    lines.append(f'  <g class="fp-tip-content" style="pointer-events:none">')
                    lines.append(_build_tooltip_box(
                        x_label, [(el.color, el.label or "Value", _fmt_val(bar.value))],
                        bar.x + bar.width / 2, bar.y - 8, 110, w, pa.y,
                    ))
                    lines.append("  </g>")

                lines.append("</g>")  # close fp-bar

        elif isinstance(el, ScatterPlotElement):
            for i, (px, py, sz) in enumerate(el.points):
                anim_style = ""
                if animate:
                    anim_style = f'animation:fp-scatterPop 0.5s ease {T_DATA + i*0.02:.2f}s both;'
                lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{math.sqrt(sz):.1f}" '
                             f'fill="{el.color}" opacity="{el.alpha}" style="{anim_style}"/>')

        elif isinstance(el, HLinePlotElement):
            da = dash_array(el.line_style)
            extra = f' stroke-dasharray="{da}"' if da else ""
            anim_style = ""
            if animate:
                anim_style = f' style="animation:fp-refFade 0.5s ease {T_DATA}s both"'
            lines.append(f'<line x1="{el.x_min:.1f}" y1="{el.y:.1f}" x2="{el.x_max:.1f}" y2="{el.y:.1f}" '
                         f'stroke="{el.color}" stroke-width="{el.line_width}"{extra}{anim_style}/>')

        elif isinstance(el, VLinePlotElement):
            da = dash_array(el.line_style)
            extra = f' stroke-dasharray="{da}"' if da else ""
            anim_style = ""
            if animate:
                anim_style = f' style="animation:fp-refFade 0.5s ease {T_DATA}s both"'
            lines.append(f'<line x1="{el.x:.1f}" y1="{el.y_min:.1f}" x2="{el.x:.1f}" y2="{el.y_max:.1f}" '
                         f'stroke="{el.color}" stroke-width="{el.line_width}"{extra}{anim_style}/>')

        elif isinstance(el, TextPlotElement):
            rot = f' transform="rotate({el.rotation} {el.x:.1f} {el.y:.1f})"' if el.rotation else ""
            anim_style = ""
            if animate:
                anim_style = f' style="animation:fp-refFade 0.5s ease 1.5s both"'
            lines.append(f'<text x="{el.x:.1f}" y="{el.y:.1f}" text-anchor="{el.anchor}" '
                         f'font-size="{el.style.font_size}" font-weight="{el.style.font_weight}" '
                         f'font-family="{_esc(el.style.font_family)}" fill="{el.style.color}"{rot}{anim_style}>'
                         f'{_esc(el.content)}</text>')

        elif isinstance(el, AnnotationPlotElement):
            anim_style = ""
            if animate:
                anim_style = f' style="animation:fp-refFade 0.5s ease 1.5s both"'
            g = f'<g{anim_style}>'
            if el.xy_text:
                ac = el.arrow_color or el.style.color
                aw = el.arrow_width or 1
                g += (f'<line x1="{el.xy_text.x:.1f}" y1="{el.xy_text.y:.1f}" '
                      f'x2="{el.xy.x:.1f}" y2="{el.xy.y:.1f}" stroke="{ac}" stroke-width="{aw}"/>')
            tx = el.xy_text.x if el.xy_text else el.xy.x
            ty = el.xy_text.y if el.xy_text else el.xy.y
            g += (f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{el.style.font_size}" '
                  f'font-family="{_esc(el.style.font_family)}" fill="{el.style.color}">'
                  f'{_esc(el.text)}</text>')
            g += "</g>"
            lines.append(g)

    # ── Hover overlay (rendered last so it's on top of all elements) ───
    if hover:
        lines.append(_build_line_hover_overlay(sp, uid))
        lines.append(_build_scatter_hover_overlay(sp, uid))


    lines.append("</svg>")
    return "\n".join(lines)


# ── Public API ──────────────────────────────────────────────────────────

def render_svg(scene: Scene, animate: bool = True, hover: bool = True) -> str:
    parts = []
    if animate or hover:
        parts.append(f'<style>{_CSS_ANIMATIONS}</style>')
    for i, sp in enumerate(scene.subplots):
        parts.append(_render_subplot(sp, animate, f"sp{i}", hover=hover))
    return "\n".join(parts)


def render_html(scene: Scene, animate: bool = True, hover: bool = True) -> str:
    theme = get_theme(scene.theme_name)
    svg = render_svg(scene, animate, hover=hover)
    return f"""<div style="background:{theme.background};padding:16px;border-radius:8px;max-width:660px;">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=EB+Garamond:wght@400;500&display=swap');
{_CSS_ANIMATIONS}
</style>
{svg}
</div>"""
