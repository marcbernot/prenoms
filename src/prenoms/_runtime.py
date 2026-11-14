"""Small helpers for code that must run both locally and in the browser."""

import asyncio
import sys
import urllib.request

IN_BROWSER = sys.platform == "emscripten"


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
