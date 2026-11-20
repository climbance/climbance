import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "module_graph.py"


def test_the_module_graph_is_fresh() -> None:
    """`modules.md` and each `runs` match `src/climb`."""
    run = subprocess.run([sys.executable, str(TOOL), "check"], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def _tool():
    spec = importlib.util.spec_from_file_location("module_graph", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _with_runs(tool, container: str, edit) -> dict:
    model = tomllib.loads(tool.MODEL.read_text())
    for e in model["element"]:
        if e["id"] == container:
            e["runs"] = edit(e["runs"])
    return model


def test_a_package_a_container_reaches_undeclared_fails() -> None:
    """A package the code reaches and `runs` omits is named."""
    tool = _tool()
    model = _with_runs(tool, "cli", lambda runs: [p for p in runs if p != "climb.generation"])
    _, found = tool.graph(model)
    assert found == ["`climb.generation` runs in `cli`, whose `runs` omits it"]


def test_a_declared_package_no_longer_reached_fails() -> None:
    """A package `runs` names and the code no longer reaches is named too."""
    tool = _tool()
    model = _with_runs(tool, "broker", lambda runs: [*runs, "climb.pick"])
    _, found = tool.graph(model)
    assert found == ["`climb.pick` is in `broker`'s `runs`, which its `code` does not reach"]
