"""
Flash Plot — Premium dark-themed charting for Jupyter & Colab.

Matplotlib-like API → Scene graph → Animated SVG.

    import flashplot as fp

    fig = fp.figure()
    ax = fig.subplot(1, 1, 1)
    ax.plot([1, 4, 2, 8, 5, 7], color="#d4d4d4", label="Strategy")
    ax.grid(True)
    ax.legend()
    fig.show()
"""

from ._core import (
    Point, Rect, Padding, TickMark, TextStyle,
    Theme, BarThemeStyle, FLASH_DARK,
    BoxStats, ViolinStats,
    register_theme, get_theme,
    compute_ticks, compute_linear_ticks, compute_log_ticks,
    linear_scale, log_scale, scale_value,
    compute_layout, compute_subplot_bounds,
    build_line_path, build_area_path, build_fill_between_path,
    build_bar_rects, build_scatter_points, compute_histogram_bins,
    compute_box_stats, compute_violin_kde,
    DEFAULT_WIDTH, DEFAULT_HEIGHT,
)

from ._figure import (
    Scene, SubplotScene, Figure, Axes, figure,
)

from ._render import render_svg, render_html

__version__ = "0.1.0"
__all__ = [
    "figure", "Figure", "Axes", "Scene", "SubplotScene",
    "render_svg", "render_html",
    "Point", "Rect", "Padding", "TickMark", "TextStyle",
    "Theme", "BarThemeStyle", "FLASH_DARK",
    "register_theme", "get_theme",
    "__version__",
]
