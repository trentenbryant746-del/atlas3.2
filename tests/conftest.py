"""Make every engine check() discoverable to a standard runner.

Over 200 self-checks lived in check() functions that only ran when a
module was executed directly. A reviewer had to be told where to look,
which matters when independent review is the point.
"""
import importlib
import pkgutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def engine_modules():
    import engine
    return sorted(m.name for m in pkgutil.iter_modules(engine.__path__)
                  if not m.name.startswith("_"))


def pytest_generate_tests(metafunc):
    if "check_row" not in metafunc.fixturenames:
        return
    rows = []
    for name in engine_modules():
        try:
            mod = importlib.import_module(f"engine.{name}")
        except Exception as e:
            rows.append((f"{name}:import", False, f"{type(e).__name__}: {e}"))
            continue
        fn = getattr(mod, "check", None)
        if not callable(fn):
            continue
        try:
            _ok, res = fn()
        except Exception as e:
            rows.append((f"{name}:check", False, f"{type(e).__name__}: {e}"))
            continue
        for row in res:
            rows.append((f"{name}:{row[0]}", row[1], str(row[2])[:200]))
    metafunc.parametrize("check_row", rows,
                         ids=[r[0] for r in rows] or ["none"])
