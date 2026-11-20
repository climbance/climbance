import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "module_graph.py"


def test_the_module_graph_is_fresh() -> None:
    """`modules.md` matches `src/climb`, and every package has a container."""
    run = subprocess.run([sys.executable, str(TOOL), "check"], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
