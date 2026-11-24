import argparse

from climb.log import account_deleted, erased, whole_log
from climb.storage import Database

# the action's warning, its past tense and what it runs
ACTIONS = {
    "erase": ("every record of {user}'s log is erased", "erased", erased),
    "delete": ("{user}'s log is erased and the account deleted", "deleted", account_deleted),
}


def user_log(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    """One user's whole log: printed as JSON, or erased, or erased with the
    account, once the user id is typed back."""
    if args.action == "export":
        print(whole_log(root, args.user).model_dump_json(indent=2))
        return
    # typed back rather than a flag: the erasure cannot be undone, and a flag
    # carries over from a shell's history
    warning, done, act = ACTIONS[args.action]
    typed = input(f"{warning.format(user=args.user)}; type {args.user} to confirm: ")
    if typed.strip() != args.user:
        parser.exit(1, f"log: nothing {done}\n")
    counted = act(root, args.user)
    print(f"{done} " + ", ".join(f"{count} {table}" for table, count in counted.items()))
