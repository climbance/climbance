import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "client_graph.py"


def test_the_client_graph_is_fresh() -> None:
    """`client-modules.md` matches the TypeScript sources."""
    run = subprocess.run([sys.executable, str(TOOL), "check"], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
