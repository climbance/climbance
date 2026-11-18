"""The helpers each command's parser is built from."""

import argparse
import os
from typing import TypedDict

from climb.cli.rows import Rows
from climb.runs import CONCURRENCY

# a parser or one of its groups: both take `add_argument`
Flags = argparse._ActionsContainer  # pyright: ignore[reportPrivateUsage]


class Defaults(argparse.ArgumentDefaultsHelpFormatter):
    """`None` and `False` are the absence of a flag, so no default is shown for
    them."""

    def _get_help_string(self, action: argparse.Action) -> str | None:
        if action.default is None or action.default is False:
            return action.help
        return super()._get_help_string(action)


def command(
    sub: argparse._SubParsersAction[argparse.ArgumentParser],  # pyright: ignore[reportPrivateUsage]
    name: str,
    help: str,
) -> argparse.ArgumentParser:
    return sub.add_parser(name, help=help, formatter_class=Defaults)


def user_argument(parser: Flags) -> None:
    parser.add_argument(
        "--user",
        # the user the dev login signs in as, so the terminal and the local
        # pages read one log
        default=os.environ.get("CLIMB_DEV_LOGIN", "local"),
        help="whose attempts to read",
    )


def run_arguments(parser: Flags, *, record: str, question: str = "prompt", per: str = "") -> None:
    """The flags every run over a backlog takes."""
    parser.add_argument(
        "--concurrency",
        type=int,
        default=CONCURRENCY,
        help=f"calls in flight at once{per}; one at a time otherwise",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help=f"ask again even where a stored {record} answers the same {question}",
    )


SETTINGS = ("--model", "--effort", "--provider", "--temperature")


class RowKeywords(TypedDict):
    dest: str
    action: type[argparse.Action]
    opener: str
    fills: list[str]
    opens_by_default: str | None


def rows(dest: str, opener: str, *, opens_by_default: str | None = None) -> RowKeywords:
    """The `add_argument` keywords that put a flag into the rows `opener`
    begins. One destination for all of them, so which setting followed which
    opener survives."""
    fills = [flag for flag in SETTINGS if flag != opener]
    return RowKeywords(
        dest=dest, action=Rows, opener=opener, fills=fills, opens_by_default=opens_by_default
    )


def configuration_arguments(parser: Flags, rows: RowKeywords, opener: str, **help: str) -> None:
    """`--model`, `--effort`, `--provider` and `--temperature`, each filling the
    row the `opener` before it began. `help` overrides the wording of one flag,
    keyed by its name."""
    wording = {
        "model": f"the model writing the {opener} before it",
        "effort": f"the effort of the {opener} before it",
        "provider": f"the backend to pin the {opener} before it to",
        "temperature": f"what the {opener} before it samples at; 'default' for the provider's own",
    } | help
    for flag in SETTINGS:
        name = flag[2:]
        parser.add_argument(flag, metavar=name.upper(), help=wording[name], **rows)
