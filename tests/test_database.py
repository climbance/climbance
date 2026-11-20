from database import emptied
from sqlalchemy import func, insert, inspect, select, text

from climb.calls.table import calls
from climb.storage import metadata


def call_row(id: str) -> dict:
    return {
        "id": id,
        "created_at": "2026-09-11T08:00:00Z",
        "model": "a-model",
        "effort": "medium",
        "prompt": "a prompt",
        "prompt_hash": "0123456789ab",
        "response": "{}",
    }


def test_the_worker_s_database_is_built_by_the_migrations(database):
    """The tables a test writes to are the ones a deployment runs, rather than
    ones the metadata creates on its own."""
    with database.engine.connect() as conn:
        head = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        tables = set(
            conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            ).scalars()
        )

    assert head
    assert tables >= set(metadata.tables)


def test_the_migrations_build_the_declared_tables_and_foreign_keys(database):
    """`database/schema.md` is drawn from the declarations, so a migration
    that adds or drops a table or a key differently would make it wrong."""
    built = inspect(database.engine)
    names = set(built.get_table_names()) - {"alembic_version"}
    migrated = {(name, (), "") for name in names} | {
        (name, tuple(key["constrained_columns"]), key["referred_table"])
        for name in names
        for key in built.get_foreign_keys(name)
    }
    declared = {(name, (), "") for name in metadata.tables} | {
        (table.name, tuple(key.column_keys), key.referred_table.name)
        for table in metadata.tables.values()
        for key in table.foreign_key_constraints
    }

    assert sorted(migrated ^ declared) == []


def test_a_test_starts_on_an_empty_database(database):
    """Every table but the helper call the fixture stores for the shared
    helpers."""
    with database.engine.connect() as conn:
        ids = conn.execute(select(calls.c.id)).scalars().all()
        held = conn.execute(select(func.count()).select_from(metadata.tables["problems"]))

        assert (ids, held.scalar_one()) == (["call-1"], 0)


def test_emptying_removes_every_row_and_restarts_the_append_order(database):
    """A later test reads no row this one wrote, and numbers its first row as
    this one did."""
    with database.engine.begin() as conn:
        conn.execute(insert(calls), [call_row("c1"), call_row("c2")])

    emptied(database.engine)

    with database.engine.begin() as conn:
        assert conn.execute(select(func.count()).select_from(calls)).scalar_one() == 0
        conn.execute(insert(calls), [call_row("c3")])
        assert conn.execute(select(calls.c.appended)).scalar_one() == 1
