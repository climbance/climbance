import argparse
import os
import sys
from collections.abc import Callable

from climb.calls import BASE_URL, OpenRouter, Retry, Transport
from climb.calls.subscription import Routed, Subscription, backend, version
from climb.cli.display import held
from climb.generation import Bench
from climb.schema import Configuration

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


def resolving(
    configurations: dict[str, Configuration],
) -> tuple[dict[str, Configuration], Subscription]:
    """Each configuration on a bare backend resolved to the CLI version
    installed, and the transport holding those versions."""
    installed: dict[str, str] = {}
    named: dict[str, Configuration] = {}
    for key, configuration in configurations.items():
        name = backend(configuration.pin)
        if name is None or configuration.pin != name:
            named[key] = configuration
            continue
        pin = installed.setdefault(name, version(name))
        named[key] = configuration.model_copy(update={"pin": pin})
    return named, Subscription(installed=installed)


def subscribed(bench: Bench) -> tuple[Bench, Subscription]:
    named, subscription = resolving({site: getattr(bench, site) for site in Bench.model_fields})
    return bench.model_copy(update=named), subscription


def routed_transport(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    configurations: dict[str, Configuration],
) -> tuple[dict[str, Configuration], Transport]:
    """The subscription CLIs for the configurations pinned to one, and the
    router for the rest. The router's key is checked only where one needs it."""
    resolved, subscription = resolving(configurations)
    if all(backend(one.pin) for one in resolved.values()):
        return resolved, subscription
    router = transport(args, parser)
    return resolved, Routed(subscription, lambda: router)


def generation_transport(
    args: argparse.Namespace, parser: argparse.ArgumentParser, bench: Bench
) -> tuple[Bench, Transport]:
    sites = {site: getattr(bench, site) for site in Bench.model_fields}
    resolved, send = routed_transport(args, parser, sites)
    return bench.model_copy(update=resolved), send
