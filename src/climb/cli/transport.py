import argparse
import os
import sys
from collections.abc import Callable

from climb.calls import BASE_URL, OpenRouter, Retry, Transport
from climb.calls.subscription import Routed, Subscription, backend, version
from climb.cli.display import held
from climb.generation import Bench

# Checked before the run: an unset key fails a whole backlog identically.
CREDENTIALS = ("OPENROUTER_API_KEY",)


def warn(retry: Retry) -> None:
    # One `write` of a whole line: this runs on the requesting thread while
    # others print, and `print` emits in several writes.
    sys.stderr.write(held(retry) + "\n")


def transport(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    *,
    on_retry: Callable[[Retry], None] = warn,
) -> OpenRouter:
    key = next((os.environ[name] for name in CREDENTIALS if os.environ.get(name)), None)
    if key is None:
        parser.exit(2, f"{args.command}: {' or '.join(CREDENTIALS)} unset\n")
    # imported on use: the import takes a quarter second, which every command
    # and every test worker paid
    from openai import OpenAI  # noqa: PLC0415

    # A command drawing a board passes its own `on_retry`, or the line scrolls
    # the block.
    return OpenRouter(OpenAI(api_key=key, base_url=BASE_URL), on_retry=on_retry)


def subscribed(bench: Bench) -> tuple[Bench, Subscription]:
    """The bench with each bare backend resolved to the CLI version installed,
    and the transport holding those versions."""
    installed: dict[str, str] = {}
    named: dict[str, object] = {}
    for site in Bench.model_fields:
        configuration = getattr(bench, site)
        name = backend(configuration.pin)
        if name is None or configuration.pin != name:
            continue
        pin = installed.setdefault(name, version(name))
        named[site] = configuration.model_copy(update={"pin": pin})
    return bench.model_copy(update=named), Subscription(installed=installed)


def generation_transport(
    args: argparse.Namespace, parser: argparse.ArgumentParser, bench: Bench
) -> tuple[Bench, Transport]:
    """The subscription CLIs for the sites pinned to one, and the router for
    the rest. The router's key is checked only where a site needs it."""
    resolved, subscription = subscribed(bench)
    routed = [
        getattr(resolved, site).pin
        for site in Bench.model_fields
        if backend(getattr(resolved, site).pin) is None
    ]
    if not routed:
        return resolved, subscription
    router = transport(args, parser)
    return resolved, Routed(subscription, lambda: router)
