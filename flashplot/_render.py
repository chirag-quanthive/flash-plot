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


# ── CSS Animation Keyframes ─────────────────────────────────────────────

_CSS_ANIMATIONS = """
@keyframes fp-gridDraw { from { stroke-dashoffset: var(--fp-len); } to { stroke-dashoffset: 0; } }
@keyframes fp-labelFadeY { from { opacity: 0; transform: translate(8px, 0); } to { opacity: 1; transform: translate(0, 0); } }
@keyframes fp-labelFadeX { from { opacity: 0; transform: translate(0, -6px); } to { opacity: 1; transform: translate(0, 0); } }
@keyframes fp-lineDraw { from { stroke-dashoffset: 2000; } to { stroke-dashoffset: 0; } }
@keyframes fp-areaFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes fp-barGrow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@keyframes fp-scatterPop { from { opacity: 0; r: 0; } to { opacity: 1; } }
@keyframes fp-refFade { from { opacity: 0; } to { opacity: 1; } }
"""


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ── Subplot Renderer ────────────────────────────────────────────────────

def _render_subplot(sp: SubplotScene, animate: bool, uid: str) -> str:
    pa = sp.plot_area
    lines: List[str] = []
    w, h = sp.bounds.w, sp.bounds.h

    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" '
                 f'style="width:100%;height:auto;display:block;font-family:\'Inter\',sans-serif;">')

    # Defs
    lines.append("<defs>")
    grad_id = f"areaGrad-{uid}"
    lines.append(f'<linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">')
    lines.append(f'  <stop offset="0%" stop-color="#d4d4d4" stop-opacity="0.15"/>')
    lines.append(f'  <stop offset="100%" stop-color="#1F1F1F" stop-opacity="0.05"/>')
    lines.append("</linearGradient>")

    # Bar filters
    bar_series = set()
    for el in sp.elements:
        if isinstance(el, BarPlotElement):
            bar_series.add(el.series_index)
    theme = get_theme()
    for si in bar_series:
        st = theme.bar_styles[si % len(theme.bar_styles)]
        for name, sigma in [("SideGlow", 5), ("TopHL", 4), ("BotGlow", 5), ("LeftEdge", 5), ("BotWhite", 2.25), ("TopWhite", 2.25)]:
            fid = f"bar{name}-{uid}-{si}"
            lines.append(f'<filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">')
            lines.append(f'  <feGaussianBlur in="SourceGraphic" stdDeviation="{sigma}"/>')
            lines.append("</filter>")
    lines.append("</defs>")

    # ── Grid ────────────────────────────────────────────────────────────
    for i, gl in enumerate(sp.grid.lines):
        ln = math.sqrt((gl.x2 - gl.x1) ** 2 + (gl.y2 - gl.y1) ** 2)
        anim = ""
        if animate:
            anim = (f' style="--fp-len:{ln:.1f};stroke-dasharray:{ln:.1f};'
                    f'animation:fp-gridDraw 0.675s cubic-bezier(0.22,1,0.36,1) {i*0.08:.2f}s both"')
        else:
            anim = ""
        lines.append(f'<line x1="{gl.x1:.1f}" y1="{gl.y1:.1f}" x2="{gl.x2:.1f}" y2="{gl.y2:.1f}" '
                     f'stroke="{gl.color}" stroke-width="{gl.width}"{anim}/>')

    # ── Y labels ────────────────────────────────────────────────────────
    for i, t in enumerate(sp.y_axis.ticks):
        ts = sp.y_axis.tick_style
        anim_style = ""
        if animate:
            anim_style = f'animation:fp-labelFadeY 0.35s ease {0.675 + i*0.04:.2f}s both;'
        lines.append(f'<text x="{pa.x - 4:.1f}" y="{t.position + 3:.1f}" text-anchor="end" '
                     f'font-size="{ts.font_size}" font-weight="{ts.font_weight}" '
                     f'font-family="{_esc(ts.font_family)}" letter-spacing="{ts.letter_spacing}" '
                     f'fill="{ts.color}" style="{anim_style}">{_esc(t.label)}</text>')

    # ── X labels ────────────────────────────────────────────────────────
    for i, t in enumerate(sp.x_axis.ticks):
        ts = sp.x_axis.tick_style
        anim_style = ""
        if animate:
            anim_style = f'animation:fp-labelFadeX 0.35s ease {0.675 + i*0.03:.2f}s both;'
        lines.append(f'<text x="{t.position:.1f}" y="{h - 4:.1f}" text-anchor="middle" '
                     f'font-size="{ts.font_size}" font-weight="{ts.font_weight}" '
                     f'font-family="{_esc(ts.font_family)}" letter-spacing="{ts.letter_spacing}" '
                     f'fill="{ts.color}" style="{anim_style}">{_esc(t.label)}</text>')

    # ── Plot elements ───────────────────────────────────────────────────
    line_idx = 0
    area_idx = 0
    for el in sp.elements:
        if isinstance(el, AreaPlotElement):
            anim_style = ""
            if animate:
                anim_style = f'animation:fp-areaFade 1.08s ease {1.28 + area_idx*0.135:.2f}s both;'
            lines.append(f'<path d="{el.path}" fill="url(#{grad_id})" opacity="{el.alpha}" style="{anim_style}"/>')
            area_idx += 1

        elif isinstance(el, LinePlotElement):
            da = dash_array(el.line_style)
            if animate:
                lines.append(f'<path d="{el.path}" fill="none" stroke="{el.color}" '
                             f'stroke-width="{el.line_width}" stroke-linejoin="round" '
                             f'stroke-dasharray="2000" opacity="{el.alpha}" '
                             f'style="animation:fp-lineDraw 1.89s cubic-bezier(0.22,1,0.36,1) {1.28 + line_idx*0.2:.2f}s both"/>')
                if da and el.line_style != "solid":
                    # After draw-in, overlay the actual dash pattern
                    lines.append(f'<path d="{el.path}" fill="none" stroke="{el.color}" '
                                 f'stroke-width="{el.line_width}" stroke-linejoin="round" '
                                 f'stroke-dasharray="{da}" opacity="{el.alpha}" '
                                 f'style="animation:fp-areaFade 0.3s ease {1.28 + line_idx*0.2 + 1.89:.2f}s both"/>')
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
                delay = 1.28 + bar.index * 0.054
                grow_style = ""
                if animate:
                    grow_style = f'transform-origin:{bar.x + bar.width/2:.1f}px {pa.y + pa.h:.1f}px;animation:fp-barGrow 0.81s cubic-bezier(0.22,1,0.36,1) {delay:.2f}s both;'

                # Base rect
                lines.append(f'<rect x="{bar.x:.1f}" y="{bar.y:.1f}" width="{bar.width:.1f}" height="{bar.height:.1f}" '
                             f'fill="{theme.bar_default_fill}" style="{grow_style}"/>')

                # Hover color layer (always visible in static output)
                clip_id = f"bc-{uid}-{si}-{bar.index}"
                lines.append(f'<clipPath id="{clip_id}"><rect x="{bar.x:.1f}" y="{bar.y:.1f}" width="{bar.width:.1f}" height="{bar.height:.1f}" style="{grow_style}"/></clipPath>')
                lines.append(f'<g clip-path="url(#{clip_id})" opacity="1">')
                lines.append(f'  <rect x="{bar.x:.1f}" y="{bar.y:.1f}" width="{bar.width:.1f}" height="{bar.height:.1f}" fill="{st.fill}" style="{grow_style}"/>')

                # Glow layers
                sc = lambda h: (h / 134) * bar.height
                bx, bw = bar.x, bar.width
                ay, ah = bar.y, bar.height

                lines.append(f'  <g filter="url(#barSideGlow-{uid}-{si})">')
                lines.append(f'    <path d="M{bx} {ay+ah+sc(11)} V{ay+ah-sc(0.5)} C{bx} {ay+ah-sc(0.5)} {bx+bw*0.85} {ay+ah-sc(15)} {bx+bw*0.85} {ay+ah-sc(26)} V{ay+sc(21)} C{bx+bw*0.85} {ay+sc(14)} {bx+bw*0.275} {ay+sc(7.69)} {bx} {ay+sc(7.5)} V{ay-sc(4)} C{bx} {ay-sc(4)} {bx+bw*1.225} {ay+sc(4.5)} {bx+bw*1.225} {ay+sc(21)} V{ay+ah-sc(40.5)} C{bx+bw*1.225} {ay+ah-sc(8)} {bx+bw*0.85} {ay+ah-sc(9.5)} {bx} {ay+ah+sc(11)} Z" fill="{st.side_glow}"/>')
                lines.append("  </g>")

                lines.append(f'  <g filter="url(#barTopHL-{uid}-{si})">')
                lines.append(f'    <rect x="{bx+bw*0.05:.1f}" y="{ay+sc(1):.1f}" width="{bw*0.9:.1f}" height="{sc(8):.1f}" rx="2" fill="{st.top_glow}"/>')
                lines.append("  </g>")

                # Bottom / left / white edges
                lines.append(f'  <g filter="url(#barBotGlow-{uid}-{si})">')
                lines.append(f'    <path d="M{bx+bw*0.05} {ay+ah-sc(8.2)} C{bx+bw*0.05} {ay+ah-sc(9.2)} {bx+bw*0.05} {ay+ah-sc(4)} {bx+bw*0.17} {ay+ah-sc(1.5)} C{bx+bw*0.28} {ay+ah+sc(0.8)} {bx+bw*0.72} {ay+ah+sc(0.8)} {bx+bw*0.83} {ay+ah-sc(1.5)} C{bx+bw*0.95} {ay+ah-sc(4)} {bx+bw*0.95} {ay+ah-sc(9.2)} {bx+bw*0.95} {ay+ah-sc(8.2)} V{ay+ah} H{bx+bw*0.05} V{ay+ah-sc(8.2)}Z" fill="{st.bottom_glow}"/>')
                lines.append("  </g>")

                lines.append(f'  <g filter="url(#barBotWhite-{uid}-{si})">')
                lines.append(f'    <path d="M{bx} {ay+ah-sc(3.5)} L{bx+bw*0.5} {ay+ah-sc(1.5)} L{bx+bw} {ay+ah-sc(3.5)} V{ay+ah} H{bx} V{ay+ah-sc(3.5)}Z" fill="white" fill-opacity="0.8"/>')
                lines.append("  </g>")
                lines.append(f'  <g filter="url(#barTopWhite-{uid}-{si})">')
                lines.append(f'    <path d="M{bx} {ay+sc(3.5)} L{bx+bw*0.5} {ay+sc(1.5)} L{bx+bw} {ay+sc(3.5)} V{ay} H{bx} V{ay+sc(3.5)}Z" fill="white" fill-opacity="0.8"/>')
                lines.append("  </g>")

                lines.append("</g>")

        elif isinstance(el, ScatterPlotElement):
            for i, (px, py, sz) in enumerate(el.points):
                anim_style = ""
                if animate:
                    anim_style = f'animation:fp-scatterPop 0.5s ease {1.28 + i*0.02:.2f}s both;'
                lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{math.sqrt(sz):.1f}" '
                             f'fill="{el.color}" opacity="{el.alpha}" style="{anim_style}"/>')

        elif isinstance(el, HLinePlotElement):
            da = dash_array(el.line_style)
            extra = f' stroke-dasharray="{da}"' if da else ""
            anim_style = ""
            if animate:
                anim_style = f' style="animation:fp-refFade 0.5s ease 1.28s both"'
            lines.append(f'<line x1="{el.x_min:.1f}" y1="{el.y:.1f}" x2="{el.x_max:.1f}" y2="{el.y:.1f}" '
                         f'stroke="{el.color}" stroke-width="{el.line_width}"{extra}{anim_style}/>')

        elif isinstance(el, VLinePlotElement):
            da = dash_array(el.line_style)
            extra = f' stroke-dasharray="{da}"' if da else ""
            anim_style = ""
            if animate:
                anim_style = f' style="animation:fp-refFade 0.5s ease 1.28s both"'
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

    lines.append("</svg>")
    return "\n".join(lines)


# ── Public API ──────────────────────────────────────────────────────────

def render_svg(scene: Scene, animate: bool = True) -> str:
    parts = []
    if animate:
        parts.append(f'<style>{_CSS_ANIMATIONS}</style>')
    for i, sp in enumerate(scene.subplots):
        parts.append(_render_subplot(sp, animate, f"sp{i}"))
    return "\n".join(parts)


def render_html(scene: Scene, animate: bool = True) -> str:
    theme = get_theme(scene.theme_name)
    svg = render_svg(scene, animate)
    return f"""<div style="background:{theme.background};padding:16px;border-radius:8px;max-width:660px;">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
{_CSS_ANIMATIONS}
</style>
{svg}
</div>"""
