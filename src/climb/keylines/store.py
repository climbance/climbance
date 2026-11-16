from typing import Any

from sqlalchemy import ColumnElement, insert, select, update

from climb.keylines.table import key_line_choices, key_line_items
from climb.schema import ItemStatus, KeyLineItem
from climb.storage import Database


class KeyLineStore:
    """Items are appended and never edited; a retirement moves the status."""

    def __init__(self, root: Database) -> None:
        self.root = root

    def add(self, items: list[KeyLineItem]) -> None:
        if not items:
            return
        with self.root.begin() as conn:
            conn.execute(
                insert(key_line_items), [one.model_dump(exclude={"choices"}) for one in items]
            )
            conn.execute(
                insert(key_line_choices),
                [
                    choice.model_dump() | {"item_id": one.id, "position": position}
                    for one in items
                    for position, choice in enumerate(one.choices)
                ],
            )

    def all(self) -> list[KeyLineItem]:
        return self._read()

    def served(self) -> list[KeyLineItem]:
        return self._read(key_line_items.c.status == ItemStatus.SERVED)

    def retire(self, ids: list[str]) -> None:
        if not ids:
            return
        with self.root.begin() as conn:
            conn.execute(
                update(key_line_items)
                .where(key_line_items.c.id.in_(ids))
                .values(status=ItemStatus.RETIRED)
            )

    def _read(self, *where: ColumnElement[bool]) -> list[KeyLineItem]:
        with self.root.connect() as conn:
            rows = (
                conn.execute(select(key_line_items).where(*where).order_by(key_line_items.c.id))
                .mappings()
                .all()
            )
            choices: dict[str, list[dict[str, Any]]] = {row["id"]: [] for row in rows}
            held = conn.execute(
                select(key_line_choices)
                .where(key_line_choices.c.item_id.in_(choices))
                .order_by(key_line_choices.c.position)
            ).mappings()
            for one in held:
                choices[one["item_id"]].append(dict(one))
        return [
            KeyLineItem.model_validate(dict(row) | {"choices": choices[row["id"]]}) for row in rows
        ]
