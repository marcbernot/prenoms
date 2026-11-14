"""Break dependency cycles in the pyodide-lock.json written by `jupyter lite build`.

Pyodide's loadPackage installs a package only after all its dependencies are installed, so a
cycle never finishes: the kernel hangs (or the tab runs out of memory) while "Loading ...".
Example: panel>=1.9 depends on panel-material-ui, which depends on panel.

Removing the edge that closes each cycle is safe: both packages are still in the lock, and
the remaining edge still pulls both in (e.g. loading panel loads panel-material-ui).

Usage: python fix_lock.py ../_output/static/pyodide-lock/pyodide-lock.json
"""

import json
import sys


def break_cycles(packages: dict) -> list[tuple[str, str]]:
    """Remove back edges found by a depth-first search; return the removed (pkg, dep) pairs."""
    removed = []
    state = {}  # name -> "visiting" | "done"

    def visit(name):
        state[name] = "visiting"
        for dep in list(packages[name]["depends"]):
            if dep not in packages:
                continue
            if state.get(dep) == "visiting":
                packages[name]["depends"].remove(dep)
                removed.append((name, dep))
            elif dep not in state:
                visit(dep)
        state[name] = "done"

    for name in sorted(packages):
        if name not in state:
            visit(name)
    return removed


def main(path):
    with open(path) as f:
        lock = json.load(f)
    removed = break_cycles(lock["packages"])
    if removed:
        with open(path, "w") as f:
            json.dump(lock, f)
    for pkg, dep in removed:
        print(f"fix_lock: removed cyclic dependency {pkg} -> {dep}")


if __name__ == "__main__":
    sys.setrecursionlimit(10_000)
    main(sys.argv[1])
