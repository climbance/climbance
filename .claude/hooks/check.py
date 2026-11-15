"""Claude Code hooks: catch at edit time what CI would otherwise fail on.

`edit` runs after an Edit or Write, and runs the tests covering the file.
`commit` runs before a Bash call. It refuses a `git commit -m` subject the
commit-msg hook would refuse, before pre-commit spends its run, and runs the
tests covering every changed file, since an edit made through Bash has no hook.
Exit 2 hands stderr to the model.
"""

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = re.compile(r"^(feat|fix|refactor|test|build|ci|docs|chore|perf|style)(\([^)]+\))?: [a-z]")
LIMIT = 50

# a path pattern, the tests covering it, and what to do when they fail
COVERED = [
    (r"^(docs/.*|README|CLAUDE)\.md$", ["tests/test_prose.py"], "rewrap or split the line"),
    (
        r"^(web/src/App\.tsx|native/src/app/.*|docs/architecture/pages\.md)$",
        ["tests/test_pages_inventory.py"],
        "update the inventory in pages.md or the test's route table",
    ),
    (r"^src/climb/.*\.py$", ["tests/test_api_openapi.py"], "run `just types`"),
]


def covered(paths: list[str]) -> int:
    failed = []
    for pattern, tests, remedy in COVERED:
        hits = [p for p in paths if re.match(pattern, p)]
        if not hits:
            continue
        run = subprocess.run(
            ["uv", "run", "pytest", "-q", "-n", "0", "--no-header", *tests],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if run.returncode != 0:
            tail = "\n".join(run.stdout.splitlines()[-15:])
            failed.append(f"{' '.join(tests)} fails after changing {hits[0]}; {remedy}.\n{tail}")
    if failed:
        sys.stderr.write("\n\n".join(failed) + "\n")
        return 2
    return 0


def edit(event: dict) -> int:
    path = event.get("tool_input", {}).get("file_path", "")
    try:
        return covered([Path(path).resolve().relative_to(ROOT).as_posix()])
    except ValueError:
        return 0


def changed() -> list[str]:
    # unstaged too: `git add x && git commit` stages them in the same call
    status = ["git", "status", "--porcelain"]
    out = subprocess.run(status, cwd=ROOT, capture_output=True, text=True).stdout
    return [line[3:].split(" -> ")[-1] for line in out.splitlines()]


def subject_problems(command: str) -> str | None:
    try:
        words = shlex.split(command)
    except ValueError:
        return None
    messages = [words[i + 1] for i, w in enumerate(words[:-1]) if w in ("-m", "--message")]
    if not messages:
        return None
    subject = messages[0].splitlines()[0] if messages[0] else ""
    if subject.startswith(("Merge ", "Revert ")):
        return None
    problems = []
    if not SUBJECT.match(subject):
        problems.append("the subject is '<type>(<scope>)?: <imperative, lowercase>'")
    if len(subject) > LIMIT:
        problems.append(f"the subject is {len(subject)} characters; the limit is {LIMIT}")
    return f"{'; '.join(problems)}: {subject!r}" if problems else None


def commit(event: dict) -> int:
    command = event.get("tool_input", {}).get("command", "")
    if "git commit" not in command or "git -C" in command:
        return 0
    if problem := subject_problems(command):
        sys.stderr.write(f"commit refused before running: {problem}\n")
        return 2
    return covered(changed())


if __name__ == "__main__":
    event = json.load(sys.stdin)
    sys.exit({"edit": edit, "commit": commit}[sys.argv[1]](event))
