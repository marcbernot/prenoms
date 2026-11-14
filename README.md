# prenoms

Exploration of the INSEE national first-names file (`nat2020.pq`: births per first name, sex and year,
France 1900–2020). The data file is attached to the [`data` release](https://github.com/marcbernot/prenoms/releases/tag/data),
not stored in git; `pixi run get-data` downloads it next to the notebooks.

[![Try it in your browser](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://marcbernot.github.io/prenoms/lab/index.html?path=prenoms.ipynb)

## Run locally

```bash
git clone https://github.com/marcbernot/prenoms && cd prenoms
pixi run lab        # installs the environment on first run
```

The notebooks in `notebooks/` run unchanged in the browser (JupyterLite, link above) and locally.
Use the browser for a quick look; install locally for heavy work.
