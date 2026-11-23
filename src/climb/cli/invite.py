import argparse

from climb.log import Role, invitations_held, invite, withdraw
from climb.storage import Database


def invitation(args: argparse.Namespace, parser: argparse.ArgumentParser, root: Database) -> None:
    """The emails allowed to sign in: added, removed, or listed."""
    if args.action == "list":
        held = [f"{email}  {role}" for email, role in invitations_held(root)]
        print("\n".join(held) if held else "no email is invited")
    elif args.action == "add":
        role = Role.AUTHOR if args.author else Role.LEARNER
        invite(root, args.email, role)
        print(f"invited {args.email.lower()} as {role}")
    elif withdraw(root, args.email):
        print(f"withdrew {args.email.lower()}")
    else:
        parser.exit(1, f"invite: {args.email.lower()} was never invited\n")
