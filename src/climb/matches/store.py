from sqlalchemy import select

from climb.matches.table import template_matches
from climb.schema import MatchHead, MatchSource, TemplateMatch
from climb.storage import Database, Log


class MatchLog(Log[TemplateMatch]):
    """Template matches, one row per pair and writer."""

    def __init__(self, root: Database) -> None:
        super().__init__(root, template_matches, TemplateMatch)

    def matches(self) -> list[TemplateMatch]:
        return self.all()

    def verdicts(self) -> list[MatchHead]:
        """Every match without its provenance, in the order appended, so a
        tie on `created_at` stands as it does over the whole records."""
        t = template_matches
        query = select(t.c.created_at, t.c.template_id, t.c.solution_id, t.c.matched, t.c.source)
        with self.root.connect() as conn:
            return [
                MatchHead.model_validate(dict(row))
                for row in conn.execute(query.order_by(t.c.appended)).mappings()
            ]

    def by_hand(self) -> list[TemplateMatch]:
        return self.where(template_matches.c.source == MatchSource.USER)
