"""Small helpers for code that must run both locally and in the browser."""

import asyncio
import importlib.util
import sys
import urllib.request

IN_BROWSER = sys.platform == "emscripten"
# The browser kernel is xeus-python (packages from emscripten-forge) when pyjs is present.
IN_XEUS = IN_BROWSER and importlib.util.find_spec("pyjs") is not None


def _restore_real_tornado() -> None:
    """Undo the placeholder ``tornado`` that emscripten-forge's IPython installs at start-up.

    That placeholder (a module without ``__file__``) breaks ``import panel``, which needs
    ``tornado.netutil`` through Bokeh's server code. The real tornado is installed, so dropping
    the placeholder lets the next ``import tornado`` find it. Must run before panel/hvplot are
    imported: ``import prenoms`` first in the notebook.
    """
    stub = sys.modules.get("tornado")
    if stub is not None and getattr(stub, "__file__", None) is None:
        for name in [m for m in sys.modules if m == "tornado" or m.startswith("tornado.")]:
            del sys.modules[name]


if IN_XEUS:
    _restore_real_tornado()


def panel_extension(*args, **kwargs):
    """Call ``pn.extension`` with the settings the current runtime needs; return ``panel``.

    In the xeus-python kernel, comms opened from the browser are rejected, so Panel must talk
    through ipywidgets (needs ipywidgets + jupyter_bokeh in the kernel and in the Lite site).
    """
    import panel as pn

    if IN_XEUS:
        kwargs.setdefault("comms", "ipywidgets")
    pn.extension(*args, **kwargs)
    return pn


def fetch(url: str) -> bytes:
    """Download ``url`` (local Python only).

    Notebooks that must also run in JupyterLite should use ``await afetch(url)``.
    """
    if IN_BROWSER:
        raise RuntimeError("fetch() is not available in the browser; use `await afetch(url)`.")
    with urllib.request.urlopen(url) as resp:
        return resp.read()


async def afetch(url: str) -> bytes:
    """Download ``url`` in both runtimes; keeps data in memory.

    In the browser the server must send CORS headers (GitHub raw, Zenodo and most data
    APIs do). Top-level ``await`` works in both IPython and the Pyodide kernel.
    """
    if IN_BROWSER:
        from pyodide.http import pyfetch

        resp = await pyfetch(url)
        if not resp.ok:
            raise OSError(f"HTTP {resp.status} for {url}")
        return await resp.bytes()
    return await asyncio.to_thread(fetch, url)
