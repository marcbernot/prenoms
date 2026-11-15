"""prenoms: the same code runs in a local Python and in JupyterLite (Pyodide)."""

from ._runtime import IN_BROWSER, IN_XEUS, afetch, fetch, panel_extension
from .data import load_example, load_nat2020

__version__ = "0.0.1"
__all__ = [
    "IN_BROWSER",
    "IN_XEUS",
    "afetch",
    "fetch",
    "load_example",
    "load_nat2020",
    "panel_extension",
]
