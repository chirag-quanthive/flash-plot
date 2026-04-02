"""Flash Plot — Pure Python charting engine with matplotlib-like API.

Usage:
    from flash_plot import FlashPlot

    fig = FlashPlot()
    fig.plot([0, 5, 12, 8, 18], color="#d4d4d4", label="Strategy")
    fig.set_title("Returns")
    fig.grid(True)
    fig.legend()
    fig.show()
"""

from .engine import FlashPlot

__version__ = "0.1.0"
__all__ = ["FlashPlot"]
