"""`fill build`: the key-line items, built from the seeded templates."""

import argparse
from datetime import UTC, datetime

from climb.cards import CardStore
from climb.judging import build_key_lines
from climb.keylines import KeyLineStore
from climb.storage import Database


def fill(args: argparse.Namespace, root: Database) -> None:
    store = KeyLineStore(root)
    cards = CardStore(root).all()
    added, retired = build_key_lines(cards, store.all(), now=datetime.now(UTC))
    store.retire(retired)
    store.add(added)
    templates = {one.template_id for one in added}
    print(
        f"{len(added)} item(s) over {len(templates)} template(s); "
        f"{len(retired)} retired; {len(store.served())} served"
    )
