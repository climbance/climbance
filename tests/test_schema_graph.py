import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "schema_graph.py"


def test_the_schema_graph_is_fresh() -> None:
    """`database/schema.md` and each `tables` match the declared tables."""
    run = subprocess.run([sys.executable, str(TOOL), "check"], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def _tool():
    spec = importlib.util.spec_from_file_location("schema_graph", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _found(edit) -> list[str]:
    tool = _tool()
    model = tomllib.loads(tool.MODEL.read_text())
    for e in model["element"]:
        if "tables" in e:
            e["tables"] = edit(e["id"], e["tables"])
    return tool.owners(model, tool.tables())[1]


def test_a_table_no_component_owns_fails() -> None:
    """A table left out of every `tables` would be drawn in no box."""
    found = _found(lambda _, ts: [t for t in ts if t != "feedback"])
    assert found == ["`feedback` is named by no element's `tables`"]


def test_a_table_two_components_own_fails() -> None:
    """One owner per table, so the table is drawn once."""
    found = _found(lambda i, ts: [*ts, "feedback"] if i == "sitting" else ts)
    assert found == ["`feedback` is named by both `sitting` and `feedback`"]


def test_a_name_no_table_declares_fails() -> None:
    """A renamed or dropped table leaves no stale name in `model.toml`."""
    found = _found(lambda i, ts: [*ts, "pauses"] if i == "sitting" else ts)
    assert found == ["`sitting` names `pauses`, which no table declares"]
