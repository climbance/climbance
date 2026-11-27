"""Transports over the subscription CLIs, `claude -p` and `codex exec`, each
run prompt-only in an empty directory: `cli/calls.md`, The subscription
backends."""

import json
import os
import subprocess
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from climb.calls.openrouter import UNSENT
from climb.calls.transport import MAX_TOKENS, ProviderError, Reply, Transport

CLAUDE = "claude-code"
CODEX = "codex-cli"
BACKENDS = (CLAUDE, CODEX)

# a generator call on a flash model took 168 s; a CLI holding past this is
# hung rather than thinking
TIMEOUT = 900

# the Codex events a prompt-only answer emits: anything else read or ran
# something, and the prompt hash would no longer name what the model saw
ANSWERING = frozenset({"agent_message", "reasoning"})

# Codex's features that offer the model a tool; the rest of its harness has
# no switch. `cli/calls.md`, The subscription backends
CODEX_TOOLS = (
    "apps",
    "browser_use",
    "browser_use_external",
    "computer_use",
    "goals",
    "hooks",
    "image_generation",
    "in_app_browser",
    "multi_agent",
    "plugins",
    "remote_plugin",
    "shell_tool",
    "skill_search",
    "sleep_tool",
    "tool_suggest",
    "unified_exec",
    "view_image",
)

Run = Callable[[list[str], str, Path], subprocess.CompletedProcess[str]]


# an API key in the environment wins over the subscription login, and `climb`
# loads `.env`, which holds one: a call would be billed per token. A parent
# Claude Code session's own variables would reach its child too
UNINHERITED = ("ANTHROPIC_", "OPENAI_", "CLAUDE_CODE_", "CLAUDECODE")


def inherited() -> dict[str, str]:
    return {name: value for name, value in os.environ.items() if not name.startswith(UNINHERITED)}


def run(argv: list[str], stdin: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        input=stdin,
        cwd=cwd,
        env=inherited(),
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
    )


def backend(pin: str) -> str | None:
    """The CLI a pin names, as `claude-code 2.1.332` names Claude Code."""
    name = pin.split(" ", 1)[0]
    return name if name in BACKENDS else None


def version(name: str, runner: Run | None = None) -> str:
    """The pin a backend resolves to now: the CLI and its version."""
    binary = {CLAUDE: "claude", CODEX: "codex"}[name]
    done = (runner or run)([binary, "--version"], "", Path.cwd())
    if done.returncode != 0:
        raise ProviderError(f"{binary} --version: {done.stderr.strip()}")
    # `2.1.332 (Claude Code)`, or `codex-cli 0.171.0`
    words = done.stdout.split()
    number = words[0] if name == CLAUDE else words[-1]
    return f"{name} {number}"


@dataclass(frozen=True)
class Subscription:
    """Sends a prompt through the CLI its pin names. A pin naming another
    version than the one installed is refused, or the record would name a
    build that did not answer."""

    # looked up per call, so a test replacing `run` reaches every instance
    runner: Run | None = None
    installed: dict[str, str] = field(default_factory=dict[str, str])

    def __call__(
        self,
        *,
        system: str,
        content: str,
        model: str,
        effort: str,
        pin: str,
        temperature: float | None = None,
        schema: dict[str, Any] | None = None,
        max_tokens: int = MAX_TOKENS,
    ) -> Reply:
        name = backend(pin)
        if name is None:
            raise ProviderError(f"{pin!r} names no subscription CLI")
        if temperature is not None:
            raise ProviderError(f"{name} takes no temperature")
        runner = self.runner or run
        now = self.installed.setdefault(name, version(name, runner))
        if pin != now:
            raise ProviderError(f"pinned to {pin!r}, and {now!r} is installed")
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="climb-call-") as held:
            # the run's directory empty, and the schema file beside it
            empty = Path(held) / "run"
            empty.mkdir()
            ask = claude if name == CLAUDE else codex
            reply = ask(runner, empty, system, content, model, effort, schema)
        return Reply(
            **reply,
            cost=0.0,
            requests=1,
            request_ms=round((time.monotonic() - started) * 1000),
        )


def claude(
    runner: Run,
    cwd: Path,
    system: str,
    content: str,
    model: str,
    effort: str,
    schema: dict[str, Any] | None,
) -> dict[str, Any]:
    # `--setting-sources ""`: the user's own CLAUDE.md and hooks stay out of
    # the prompt
    argv = [
        "claude",
        "-p",
        "--model",
        model,
        *(["--effort", effort] if effort != UNSENT else []),
        "--tools",
        "",
        "--system-prompt",
        system,
        "--setting-sources",
        "",
        "--no-session-persistence",
        "--output-format",
        "json",
    ]
    if schema is not None:
        argv += ["--json-schema", json.dumps(schema)]
    done = runner(argv, content, cwd)
    try:
        body: dict[str, Any] = json.loads(done.stdout)
    except json.JSONDecodeError:
        raise ProviderError(f"claude: {(done.stderr or done.stdout).strip()[:500]}") from None
    if body.get("is_error") or done.returncode != 0:
        raise ProviderError(f"claude: {body.get('result') or body.get('subtype')}")
    structured = body.get("structured_output")
    text = json.dumps(structured) if schema is not None and structured is not None else None
    usage: dict[str, Any] = body.get("usage") or {}
    details: dict[str, Any] = usage.get("output_tokens_details") or {}
    return {
        "text": text if schema is not None else body.get("result") or None,
        "stop_reason": body.get("terminal_reason") or body.get("stop_reason"),
        "input_tokens": sum(
            usage.get(one) or 0
            for one in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
        ),
        "output_tokens": usage.get("output_tokens"),
        "reasoning_tokens": details.get("thinking_tokens"),
        "provider": "anthropic",
    }


def codex(
    runner: Run,
    cwd: Path,
    system: str,
    content: str,
    model: str,
    effort: str,
    schema: dict[str, Any] | None,
) -> dict[str, Any]:
    instructions = cwd.parent / "instructions.md"
    instructions.write_text(system)
    argv = [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--json",
        "-m",
        model,
        *(["-c", f"model_reasoning_effort={effort}"] if effort != UNSENT else []),
        # the system prompt in place of Codex's own instructions
        "-c",
        f"model_instructions_file={instructions}",
        "-c",
        "include_environment_context=false",
        "-c",
        "web_search=disabled",
        *(arg for name in CODEX_TOOLS for arg in ("-c", f"features.{name}=false")),
        "-C",
        str(cwd),
    ]
    if schema is not None:
        written = cwd.parent / "schema.json"
        written.write_text(json.dumps(schema))
        argv += ["--output-schema", str(written)]
    done = runner([*argv, "-"], content, cwd)
    events: list[dict[str, Any]] = [
        json.loads(line) for line in done.stdout.splitlines() if line.startswith("{")
    ]
    items = [one["item"] for one in events if one.get("type") == "item.completed"]
    # an error item is Codex's notice, such as a reconnect, and read nothing
    acted = sorted({one.get("type") for one in items} - ANSWERING - {"error"})
    if acted:
        raise ProviderError(f"codex: the model used {', '.join(map(str, acted))}")
    completed = [one for one in events if one.get("type") == "turn.completed"]
    # a reconnect the turn recovered from is an error event too
    failed = [one for one in events if one.get("type") in ("error", "turn.failed")]
    if not completed or done.returncode != 0:
        said = failed[-1] if failed else done.stderr.strip()[:500]
        raise ProviderError(f"codex: {said}")
    said = [one.get("text") for one in items if one.get("type") == "agent_message"]
    usage: dict[str, Any] = completed[-1].get("usage") or {}
    return {
        "text": said[-1] if said else None,
        "stop_reason": "completed" if said else "no answer",
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "reasoning_tokens": usage.get("reasoning_output_tokens"),
        "provider": "openai",
    }


@dataclass(frozen=True)
class Routed:
    """A subscription pin to its CLI, any other to the router."""

    subscription: Transport
    router: Callable[[], Transport]

    def __call__(self, **request: Any) -> Reply:  # noqa: ANN401 - the Transport's own keywords
        pin: str = request["pin"]
        send = self.subscription if backend(pin) else self.router()
        return send(**request)
