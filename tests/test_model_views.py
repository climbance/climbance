import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "model_views.py"


def test_the_model_views_are_fresh() -> None:
    """The views, the citations and each file's owner all match `model.toml`."""
    run = subprocess.run([sys.executable, str(TOOL), "check"], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def _tool():
    spec = importlib.util.spec_from_file_location("model_views", TOOL)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _found(files: list[str], edit) -> list[str]:
    tool = _tool()
    model = tomllib.loads(tool.MODEL.read_text())
    for e in model["element"]:
        e["src"] = edit(e["id"], e.get("src", []))
    return tool.owner_problems(model, files)


def test_a_file_no_element_owns_fails() -> None:
    """A new file outside every `src` leads to no box on the map."""
    found = _found(["src/climb/caps.py", "src/climb/new.py"], lambda _, gs: gs)
    assert "`src/climb/new.py` is named by no element's `src`" in found


def test_a_file_two_elements_own_fails() -> None:
    """One owner per file, so a diff maps to one element per file."""
    files = ["src/climb/caps.py"]
    found = _found(files, lambda i, gs: [*gs, "src/climb/caps.py"] if i == "pick" else gs)
    assert "`src/climb/caps.py` is named by the `src` of `submission`, `pick`" in found


def test_a_glob_matching_nothing_fails() -> None:
    """A stale glob would claim the next file to land at its path."""
    added = {"submission": ["src/climb/caps.py", "src/climb/gone.py"]}
    found = _found(["src/climb/caps.py"], lambda i, _: added.get(i, []))
    assert found == ["`submission` names `src/climb/gone.py` in `src`, which matches no file"]


def test_a_relation_between_containers_without_technology_fails() -> None:
    """At the container level a relation says what it runs over."""
    tool = _tool()
    model = tomllib.loads(tool.MODEL.read_text())
    for r in model["relation"]:
        if (r["from"], r["to"]) in {("proxy", "api"), ("seed", "content-repo")}:
            r.pop("technology", None)
    ids = [model["engine"]["id"], *(e["id"] for e in model["element"])]
    assert tool.relation_problems(model, ids) == [
        "the relation from `proxy` to `api` lacks `technology`"
    ]
