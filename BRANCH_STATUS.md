# Branch `xeus`: status

**Status: abandoned for now (2026-11-15). Not pushed, not merged. `main` stays on the Pyodide kernel.**

Goal: replace the JupyterLite Pyodide kernel (`jupyterlite-pyodide-kernel-with-lock` + `PyodideLockAddon`)
with the xeus-python kernel (`jupyterlite-xeus`), hoping for:

1. browser package versions closer to the local pixi environment,
2. one packaging world (conda/emscripten-forge) instead of uv resolving against the Pyodide lock,
3. no more dependency-cycle hang (panel <-> panel-material-ui), so no `lite/fix_lock.py`,
4. maybe a faster kernel start.

## What changed on this branch

| File | Change |
|---|---|
| `pixi.toml` | lite env: `jupyterlite-pyodide-kernel-with-lock` replaced by `jupyterlite-xeus = "6.*"` (6.0.0) + `pip` (used by jupyterlite-xeus to install `prenoms`); `wheel` task removed; `build-lite` no longer runs `fix_lock.py` |
| `lite/environment.yml` | new: browser environment, channels `https://prefix.dev/emscripten-forge-4x` + `https://prefix.dev/conda-forge`; `xeus-python numpy pandas pyarrow hvplot panel`, plus `pip: [..]` (this project, installed with `pip --no-deps`) |
| `lite/jupyter_lite_config.json` | `PyodideLockAddon` section removed; `XeusAddon.mount_jupyterlite_content = true` (site files mounted so `nat2020.pq` is found next to the notebook) |
| `lite/fix_lock.py` | removed (not needed: no runtime package loader) |

## What was tried, in order

1. **Package availability check** (`pixi search -p emscripten-wasm32` on emscripten-forge-4x):
   the channel *has* recent builds (python 3.14.3, numpy 2.5.4, pandas 3.1.0, pyarrow 23, bokeh 3.10.0,
   panel 1.10.0). This looked like a big win, but see step 3.
2. **First build** failed: micromamba downloads and unpacks into `$TMPDIR`, and `/tmp` on this machine
   is a 1.9 GB tmpfs → `Disk quota exceeded`. Worked around with
   `TMPDIR=$PWD/.pixi/tmp pixi run build-lite` (not yet put into the task).
3. **Solve result** (from the build log): `xeus-python` 0.19.0 on emscripten-forge is built for
   **Python 3.13 only**, so the solver picks Python 3.13.1 and whatever is compatible with it:

   | Package | local (default env) | Pyodide kernel (main) | xeus kernel (this branch) |
   |---|---|---|---|
   | Python | 3.14.10 | 3.14.2 | 3.13.1 |
   | numpy | 2.5.4 | 2.4.6 | 2.5.4 |
   | pandas | 3.1.1 | 3.0.2 | 3.1.0 |
   | pyarrow | 26.0.1 | 22.0.0 | 23.0.0 |
   | bokeh | 3.10.0 | 3.9.0 | 3.9.2 |
   | panel | 1.10.0 | 1.9.4 | 1.8.10 |

   The newer versions found in step 1 exist, but not in builds that install together with xeus-python.
4. **Second build** succeeded: ~9 min (Pyodide build: ~1 min), 258 packages (incl. boost, matplotlib,
   openblas pulled in by pyarrow/holoviews), `_output/` = 220 MB of which 178 MB is the packed
   environment (`_output/xeus/`). `prenoms` is in the packed env (`prenoms-0.0.1-pip.tar.gz`).
5. **Browser test** (headless Firefox 159 via Selenium, headless Chromium via Playwright; same scripts
   as for the Pyodide fix): kernel starts, no kernel-selection prompt, all cells execute in ~35 s,
   but the first cell fails and everything after it raises `NameError: df`.
6. **Step-by-step import test** in the kernel: `numpy`, `pandas`, `pyarrow`, `bokeh` import fine;
   `import panel` fails:

   ```
   File ".../bokeh/server/server.py", line 46, in <module>
       from tornado import netutil, version as tornado_version
   ImportError: cannot import name 'netutil' from 'tornado' (unknown location)
   ```

   The real tornado package is installed and complete (`/lib/python3.13/site-packages/tornado/netutil.py`
   exists), but xeus-python puts a **stub module** in `sys.modules` before user code runs:
   `sys.modules["tornado"]` is `<module 'tornado'>` with no `__file__`/`__path__`, plus `tornado.gen`.
   Panel imports bokeh's server code at import time, which needs the real tornado.
7. **Workaround attempt**: a first cell removing the stub
   (`sys.modules.pop("tornado.gen"); sys.modules.pop("tornado")`) before importing panel. Panel then
   gets further but the kernel hits asyncio conflicts (`Cannot enter into task <Task-4 ...
   XPythonLoopRunner ...> while another task <Task-2 ...> is running`), cells stay busy (`[*]`), and on a
   second run the Chromium tab crashed. The stub is presumably there because real tornado's IOLoop
   conflicts with xeus-python's own asyncio loop runner.

## Assessment

The xeus kernel does **not** work for this project today, and the expected benefits mostly did not
materialise:

| Hoped-for benefit | Result |
|---|---|
| Versions closer to local | **No.** Python 3.13 instead of 3.14; panel and bokeh *older* than with Pyodide. Only numpy/pandas/pyarrow are newer. |
| One packaging world | Partly: `environment.yml` is conda-style, but it is still a second dependency list to keep in sync, and `prenoms` goes in through an experimental `pip --no-deps` path. |
| No dependency-cycle hang | **Yes**: the environment is solved and unpacked at build time, no runtime loader. |
| Faster start | Not measurable, since the notebook fails; the kernel itself started in a few seconds. |
| Panel / hvPlot work | **No**: stub `tornado` breaks `import panel`; removing it breaks the kernel's event loop. |

Costs on top: build 9× slower, a 220 MB site (Pages limit is 1 GB, so OK but heavy), `TMPDIR` workaround
needed on machines with a small `/tmp`.

The Pyodide kernel on `main` (with `lite/fix_lock.py`) runs the whole notebook, figures and Panel
widget included, in Firefox and Chromium, locally and on GitHub Pages. Staying on Pyodide is the right
call.

## When to look again

Retry this branch if **both** become true:

- emscripten-forge publishes `xeus-python` for Python 3.14 (check:
  `pixi search -c https://repo.prefix.dev/emscripten-forge-4x -p emscripten-wasm32 xeus-python`, look at
  the build string: `py314...`),
- xeus-python no longer stubs `tornado`, or Panel no longer needs bokeh's server modules at import time
  (check in a xeus kernel: `import sys; sys.modules.get("tornado")` should be `None` before any import,
  and `import panel` should succeed).

Or if the project drops Panel (hvPlot alone also imports panel via holoviews, so this means dropping
the hvPlot/HoloViews stack too).

To retry:

```bash
git switch xeus
git rebase main            # pick up later changes; fix_lock.py removal may conflict
mkdir -p .pixi/tmp && TMPDIR=$PWD/.pixi/tmp pixi run build-lite
pixi run serve-lite        # open prenoms.ipynb and Run All
```

If it works, also move `TMPDIR` into the `build-lite` task (`env = { TMPDIR = "..." }`) and check CI
(the GitHub runner's `/tmp` is on disk, so the quota issue should not appear there).
