import json
import subprocess

import pytest

from climb.calls import ProviderError
from climb.calls.subscription import Routed, Subscription, backend, inherited, version

SCHEMA = {"type": "object", "properties": {"answer": {"type": "integer"}}}


class Runner:
    """Answers each CLI as a script says, and keeps what it was sent."""

    def __init__(self, stdout: str, returncode: int = 0):
        self.stdout, self.returncode = stdout, returncode
        self.sent: list[tuple[list[str], str]] = []

    def __call__(self, argv, stdin, _cwd):
        self.sent.append((argv, stdin))
        if argv[1:] == ["--version"]:
            out = "2.1.332 (Claude Code)" if argv[0] == "claude" else "codex-cli 0.171.0"
            return subprocess.CompletedProcess(argv, 0, out, "")
        return subprocess.CompletedProcess(argv, self.returncode, self.stdout, "")


def claude_said(**body) -> str:
    return json.dumps(
        {
            "is_error": False,
            "result": '{"answer":5}',
            "structured_output": {"answer": 5},
            "terminal_reason": "completed",
            "usage": {"input_tokens": 2, "cache_creation_input_tokens": 676, "output_tokens": 9},
            "total_cost_usd": 0.001,
        }
        | body
    )


def codex_said(*items: dict) -> str:
    events = [
        {"type": "thread.started"},
        *({"type": "item.completed", "item": one} for one in items),
        {"type": "turn.completed", "usage": {"input_tokens": 17726, "output_tokens": 15}},
    ]
    return "\n".join(json.dumps(one) for one in events)


def asked(transport, pin: str, **overrides):
    request = {
        "system": "You answer arithmetic.",
        "content": "2+3?",
        "model": "a-model",
        "effort": "medium",
        "pin": pin,
        "temperature": None,
        "schema": SCHEMA,
    } | overrides
    return transport(**request)


def test_a_backend_resolves_to_its_cli_and_version():
    """An upgraded CLI wraps the prompt in other instructions, so the pin says
    which one answered."""
    runner = Runner("")

    assert version("claude-code", runner) == "claude-code 2.1.332"
    assert version("codex-cli", runner) == "codex-cli 0.171.0"
    assert backend("claude-code 2.1.332") == "claude-code"
    assert backend("google-ai-studio") is None


def test_a_claude_answer_is_its_structured_output_at_no_cost():
    """The notional price is not stored: the spend page would count money
    never paid."""
    reply = asked(Subscription(Runner(claude_said())), "claude-code 2.1.332")

    assert json.loads(reply.text) == {"answer": 5}
    assert reply.cost == 0.0
    assert reply.input_tokens == 678


def test_claude_runs_with_no_tools_and_none_of_the_users_settings():
    """The user's CLAUDE.md would otherwise be part of what the model sees."""
    runner = Runner(claude_said())

    asked(Subscription(runner), "claude-code 2.1.332")

    argv, stdin = runner.sent[-1]
    assert argv[argv.index("--tools") + 1] == ""
    assert argv[argv.index("--setting-sources") + 1] == ""
    assert argv[argv.index("--system-prompt") + 1] == "You answer arithmetic."
    assert stdin == "2+3?"


def test_a_codex_call_that_ran_a_command_is_refused():
    """It read more than the prompt the hash names."""
    said = codex_said({"type": "command_execution"}, {"type": "agent_message", "text": "{}"})

    with pytest.raises(ProviderError, match="command_execution"):
        asked(Subscription(Runner(said)), "codex-cli 0.171.0")


def test_codex_runs_with_its_shell_tool_off():
    """With the tool on, the model ran a command in 2 of 29 generation calls."""
    runner = Runner(codex_said({"type": "agent_message", "text": '{"answer":5}'}))

    asked(Subscription(runner), "codex-cli 0.171.0")

    argv, _ = runner.sent[-1]
    assert "features.shell_tool=false" in argv


def test_a_codex_answer_is_its_last_message():
    said = codex_said({"type": "reasoning"}, {"type": "agent_message", "text": '{"answer":5}'})

    reply = asked(Subscription(Runner(said)), "codex-cli 0.171.0")

    assert json.loads(reply.text) == {"answer": 5}
    assert reply.input_tokens == 17726


def test_a_pin_naming_another_version_is_refused():
    """The record would name a build that did not answer."""
    with pytest.raises(ProviderError, match="installed"):
        asked(Subscription(Runner(claude_said())), "claude-code 2.0.0")


def test_a_temperature_is_refused():
    """Neither CLI takes one, so a record carrying it would be false."""
    with pytest.raises(ProviderError, match="temperature"):
        asked(Subscription(Runner(claude_said())), "claude-code 2.1.332", temperature=0.0)


def test_a_claude_error_is_raised():
    said = claude_said(is_error=True, result="usage limit reached")

    with pytest.raises(ProviderError, match="usage limit"):
        asked(Subscription(Runner(said, returncode=1)), "claude-code 2.1.332")


def test_a_router_pin_goes_to_the_router():
    sent: list[str] = []

    def router(**request):
        sent.append(request["pin"])

    routed = Routed(Subscription(Runner(claude_said())), lambda: router)
    asked(routed, "google-ai-studio")

    assert sent == ["google-ai-studio"]


def test_no_api_key_reaches_a_cli(monkeypatch):
    """A key in the environment wins over the subscription login, and the call
    would be billed per token."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "a-key")
    monkeypatch.setenv("OPENAI_API_KEY", "a-key")
    monkeypatch.setenv("CLAUDE_CODE_SESSION_ID", "a-session")

    assert not {"ANTHROPIC_API_KEY", "OPENAI_API_KEY", "CLAUDE_CODE_SESSION_ID"} & set(inherited())
    assert "PATH" in inherited()


def test_codex_reads_the_system_prompt_in_place_of_its_own_instructions():
    """Codex's coding-agent prompt and its tools would be part of what the
    model sees."""
    runner = Runner(codex_said({"type": "agent_message", "text": '{"answer":5}'}))

    asked(Subscription(runner), "codex-cli 0.171.0")

    argv, stdin = runner.sent[-1]
    settings = [argv[i + 1] for i, one in enumerate(argv) if one == "-c"]
    held = next(one for one in settings if one.startswith("model_instructions_file="))
    assert held.endswith("instructions.md")
    assert {"include_environment_context=false", "features.shell_tool=false"} <= set(settings)
    assert stdin == "2+3?"


def test_the_default_effort_sends_no_effort_flag():
    """A claim about a model as it answers by default names no effort."""
    claude = Runner(claude_said())
    codex = Runner(codex_said({"type": "agent_message", "text": "{}"}))

    asked(Subscription(claude), "claude-code 2.1.332", effort="default")
    asked(Subscription(codex), "codex-cli 0.171.0", effort="default")

    assert "--effort" not in claude.sent[-1][0]
    assert not any(one.startswith("model_reasoning_effort") for one in codex.sent[-1][0])


def test_a_codex_turn_that_recovered_from_a_reconnect_is_answered():
    """A reconnect notice is no tool use, and the turn still completed."""
    said = codex_said(
        {"type": "error", "message": "Reconnecting... 1/5"},
        {"type": "agent_message", "text": '{"answer":5}'},
    )
    noticed = '{"type": "error", "message": "Reconnecting... 1/5"}\n' + said

    reply = asked(Subscription(Runner(noticed)), "codex-cli 0.171.0")

    assert json.loads(reply.text) == {"answer": 5}


def test_a_codex_turn_that_never_completed_is_refused():
    said = '{"type": "error", "message": "Reconnecting... 5/5"}\n{"type": "turn.failed"}'

    with pytest.raises(ProviderError, match="codex"):
        asked(Subscription(Runner(said)), "codex-cli 0.171.0")
