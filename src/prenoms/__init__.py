"""prenoms: the same code runs in a local Python and in JupyterLite (Pyodide)."""

from ._runtime import IN_BROWSER, afetch, fetch
from .data import load_example, load_nat2020

__version__ = "0.0.1"
__all__ = ["IN_BROWSER", "afetch", "fetch", "load_example", "load_nat2020"]
