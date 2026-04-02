from setuptools import setup, find_packages

setup(
    name="flash-plot",
    version="0.1.0",
    description="Pure Python charting engine with matplotlib-like API — renders SVG inline in notebooks",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "notebook": ["ipython"],
        "numpy": ["numpy"],
    },
)
