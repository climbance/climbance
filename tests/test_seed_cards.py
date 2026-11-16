import json
from pathlib import Path

import pytest
from commands import connected
from helpers import own
from test_seed_knowledge import authored

from climb import cli
from climb.cards import CardStore, seed_cards
from climb.knowledge import read_module, seed_module, seeded_modules, seeded_subtopics

CONTENT = Path(__file__).parents[1] / "content" / "cards"
MODULE_CONTENT = CONTENT.parent / "modules"
# the primary module every card here names, as if seeded
MODULES = {"algo"}


def template(slug: str = "predicate-first-true", **overrides) -> dict:
    return {
        "slug": slug,
        "title": slug,
        "trigger": "a monotone predicate over the range",
        "code": "def f(): pass",
    } | overrides


def record(slug: str = "binary-search", *, technique: str = "binary-search", **overrides) -> dict:
    return {
        "slug": slug,
        "technique": technique,
        "module": "algo",
        "title": "Binary search",
        "trigger": "a sorted range and a monotone predicate",
        "brief": "## Core idea\n\nHalve the range.",
        "templates": [template()],
        "selector": {"technique": technique, "size": 5},
    } | overrides


def test_an_authored_case_reaches_the_stored_template(database):
    """The trainer checks a recalled form against these, and the author writes
    them beside the form."""
    store = CardStore(database)
    authored = template(cases=[{"args": [[1, 2, 3], 2], "expected": 1}])

    seed_cards([record(templates=[authored])], store=store, modules=MODULES)

    card = store.by_slug("binary-search")
    assert card is not None
    assert [(one.args, one.expected) for one in card.templates[0].cases] == [([[1, 2, 3], 2], 1)]


def test_seed_mints_identity(database):
    """The author writes slugs; the engine owns every id, at both levels."""
    store = CardStore(database)
    result = seed_cards([record()], store=store, modules=MODULES)

    assert result.ingested == 1
    assert result.updated == 0
    card = store.all()[0]
    assert card.id
    assert card.slug == "binary-search"
    assert [t.id for t in card.templates] == [card.templates[0].id]
    assert card.templates[0].id
    assert card.templates[0].slug == "predicate-first-true"


def test_the_payload_cannot_supply_identity(database):
    """The seed has no field for an id, so writing one supplies nothing."""
    store = CardStore(database)
    seed_cards(
        [record(id="forged", templates=[template(id="forged-template")])],
        store=store,
        modules=MODULES,
    )

    card = store.all()[0]
    assert card.id != "forged"
    assert card.templates[0].id != "forged-template"


def test_reseeding_a_slug_refreshes_and_keeps_the_id(database):
    """A card run references the id, so re-seeding never moves it."""
    store = CardStore(database)
    seed_cards([record()], store=store, modules=MODULES)
    minted = store.all()[0].id

    result = seed_cards([record(title="Binary search, revised")], store=store, modules=MODULES)

    assert result.ingested == 0
    assert result.updated == 1
    assert len(store.all()) == 1
    assert store.get(minted).title == "Binary search, revised"


def test_a_template_keeps_its_id_across_a_reseed(database):
    """Recall is per template and keys to its id, so the slug is what a
    re-seed matches on; a template the author added gets a new one."""
    store = CardStore(database)
    seed_cards([record()], store=store, modules=MODULES)
    before = {t.slug: t.id for t in store.all()[0].templates}

    seed_cards(
        [record(templates=[template(title="renamed"), template("answer-space")])],
        store=store,
        modules=MODULES,
    )

    after = {t.slug: t.id for t in store.all()[0].templates}
    assert after["predicate-first-true"] == before["predicate-first-true"]
    assert after["answer-space"] not in before.values()
    assert store.all()[0].templates[0].title == "renamed"


def test_a_new_slug_is_a_new_card(database):
    """Renaming is a title change: the runs and the recall history stay with
    the card whose slug they were written against."""
    store = CardStore(database)
    seed_cards([record()], store=store, modules=MODULES)
    result = seed_cards([record("binary-search-advanced")], store=store, modules=MODULES)

    assert result.ingested == 1
    assert result.updated == 0
    assert sorted(card.slug for card in store.all()) == [
        "binary-search",
        "binary-search-advanced",
    ]


@pytest.mark.parametrize("field", ["technique", "selector"])
def test_an_unknown_technique_is_rejected(database, field):
    """Membership is checked on the write path — here, and on the selector a
    ladder draws by, where an unknown code would resolve to nothing and say
    nothing."""
    store = CardStore(database)
    overrides = (
        {"technique": "sliding-windows"}
        if field == "technique"
        else {"selector": {"technique": "sliding-windows", "size": 5}}
    )
    result = seed_cards([record(**overrides)], store=store, modules=MODULES)

    assert result.ingested == 0
    assert [r.index for r in result.rejected] == [0]
    assert store.all() == []


def test_an_invalid_card_does_not_stop_the_batch(database):
    """Per record, by index, as at every other boundary."""
    store = CardStore(database)
    result = seed_cards(
        [
            record("binary-search"),
            {"slug": "half-written"},
            record("union-find", technique="union-find"),
        ],
        store=store,
        modules=MODULES,
    )

    assert result.ingested == 2
    assert [r.index for r in result.rejected] == [1]
    assert sorted(card.slug for card in store.all()) == ["binary-search", "union-find"]


def test_a_card_rejected_by_its_own_validator(database):
    """Two templates sharing a slug leave a re-seed with no rule for which
    minted id to keep."""
    store = CardStore(database)
    result = seed_cards([record(templates=[template(), template()])], store=store, modules=MODULES)

    assert [r.index for r in result.rejected] == [0]


def test_empty_batch(database):
    result = seed_cards([], store=CardStore(database), modules=MODULES)

    assert result.ingested == 0
    assert result.updated == 0
    assert result.rejected == []


def seeded_algo(database, tmp_path) -> None:
    """The command reads the seeded modules from the store."""
    base = authored(tmp_path)
    seed_module(read_module(base.rename(base.with_name("algo"))), root=database)


def test_seed_cards_command_over_a_directory(database, tmp_path, monkeypatch, capsys):
    seeded_algo(database, tmp_path)
    source = tmp_path / "authored"
    source.mkdir()
    (source / "binary-search.json").write_text(json.dumps(record()))
    (source / "union-find.json").write_text(
        json.dumps(record("union-find", technique="union-find"))
    )
    connected(database, monkeypatch)
    monkeypatch.setattr("sys.argv", ["climb", "seed", "cards", str(source)])

    cli.main()

    assert len(own(CardStore(database).all())) == 2
    printed = capsys.readouterr()
    assert json.loads(printed.out)["ingested"] == 2
    assert printed.err.splitlines() == ["seed: cards 2"]


def test_seed_cards_command_over_one_file(database, tmp_path, monkeypatch, capsys):
    seeded_algo(database, tmp_path)
    source = tmp_path / "binary-search.json"
    source.write_text(json.dumps(record()))
    connected(database, monkeypatch)
    monkeypatch.setattr("sys.argv", ["climb", "seed", "cards", str(source)])

    cli.main()

    assert len(own(CardStore(database).all())) == 1


def test_a_rejected_card_exits_nonzero(database, tmp_path, monkeypatch, capsys):
    source = tmp_path / "broken.json"
    source.write_text(json.dumps({"slug": "half-written"}))
    connected(database, monkeypatch)
    monkeypatch.setattr("sys.argv", ["climb", "seed", "cards", str(source)])

    with pytest.raises(SystemExit) as exit:
        cli.main()

    assert exit.value.code == 1
    assert json.loads(capsys.readouterr().out)["rejected"]


def test_a_file_that_is_not_json_never_reaches_the_engine(database, tmp_path, monkeypatch, capsys):
    """Corrupt transport, not an invalid card: it cannot come back as a
    rejection, since nothing validated it."""
    source = tmp_path / "broken.json"
    source.write_text("{")
    connected(database, monkeypatch)
    monkeypatch.setattr("sys.argv", ["climb", "seed", "cards", str(source)])

    with pytest.raises(SystemExit) as exit:
        cli.main()

    assert exit.value.code == 2
    assert "seed:" in capsys.readouterr().err


@pytest.mark.skipif(not CONTENT.is_dir(), reason="content/ is a private repo, absent in CI")
def test_the_authored_cards_seed(database):
    """The content in this repo is what the path exists to load, so it is
    seeded rather than described."""
    for module in sorted(MODULE_CONTENT.iterdir()):
        assert not seed_module(read_module(module), root=database).refused
    store = CardStore(database)
    result = seed_cards(
        [json.loads(path.read_text()) for path in sorted(CONTENT.glob("*.json"))],
        store=store,
        modules=seeded_modules(root=database),
        subtopics=seeded_subtopics(root=database),
    )

    assert result.rejected == []
    assert result.ingested == len(list(CONTENT.glob("*.json")))
    assert all(card.templates for card in store.all())


def edge(card: str = "union-find", template: str = "dsu-core", used_by: str = "kruskal-mst"):
    return {"card": card, "template": template, "used_by": used_by}


def dsu(**overrides) -> dict:
    return (
        record("union-find", technique="union-find", templates=[template("dsu-core")]) | overrides
    )


def kruskal(*requires: dict, **overrides) -> dict:
    return (
        record(
            "minimum-tree",
            technique="union-find",
            templates=[template("kruskal-mst")],
            requires=list(requires),
        )
        | overrides
    )


def test_a_requirement_reaches_the_stored_card(database):
    """The required card may come later in the batch: the edges are written
    after every card."""
    store = CardStore(database)

    result = seed_cards([kruskal(edge()), dsu()], store=store, modules=MODULES)

    assert result.rejected == []
    card = store.by_slug("minimum-tree")
    assert card is not None
    assert [one.model_dump() for one in card.requires] == [edge()]


def test_a_requirement_on_an_unknown_card_is_refused(database):
    result = seed_cards([kruskal(edge())], store=CardStore(database), modules=MODULES)

    assert [one.reason for one in result.rejected] == ["requires an unknown card: union-find"]


def test_a_requirement_on_an_unknown_template_is_refused(database):
    result = seed_cards(
        [dsu(), kruskal(edge(template="dsu-rank"))], store=CardStore(database), modules=MODULES
    )

    assert [one.index for one in result.rejected] == [1]
    assert "unknown template" in result.rejected[0].reason


def test_a_requirement_on_an_optional_template_is_refused(database):
    """The required card's study set leaves the optional form out, so a card
    requiring it would wait on a form nobody is asked for."""
    stretch = dsu(templates=[template("dsu-core", optional=True), template("dsu-plain")])

    result = seed_cards([stretch, kruskal(edge())], store=CardStore(database), modules=MODULES)

    assert [one.index for one in result.rejected] == [1]
    assert "optional template" in result.rejected[0].reason


def test_a_cycle_refuses_every_card_on_it(database):
    """A cycle locks each of its cards for every user."""
    looped = dsu(requires=[edge("minimum-tree", "kruskal-mst", "dsu-core")])

    result = seed_cards([looped, kruskal(edge())], store=CardStore(database), modules=MODULES)

    assert [one.reason for one in result.rejected] == ["on a cycle of requirements"] * 2


def test_used_by_names_a_template_of_the_requiring_card(database):
    result = seed_cards(
        [dsu(), kruskal(edge(used_by="prim"))], store=CardStore(database), modules=MODULES
    )

    assert "used_by names no template" in result.rejected[0].reason


def test_a_refused_card_refuses_the_cards_requiring_it(database):
    """A refused new card is in no graph, so an edge onto it names nothing."""
    looped = dsu(requires=[edge("union-find", "dsu-core", "dsu-core")])

    result = seed_cards([looped, kruskal(edge())], store=CardStore(database), modules=MODULES)

    assert [one.index for one in result.rejected] == [0, 1]


def test_a_reseed_dropping_a_required_template_is_refused(database):
    """The stored card requiring that template is not in the batch, so the seed
    breaking it is the one refused, and the stored card stands."""
    store = CardStore(database)
    seed_cards([dsu(), kruskal(edge())], store=store, modules=MODULES)

    result = seed_cards([dsu(templates=[template("dsu-rank")])], store=store, modules=MODULES)

    assert result.rejected[0].reason == "minimum-tree requires union-find/dsu-core"
    card = store.by_slug("union-find")
    assert card is not None
    assert [one.slug for one in card.templates] == ["dsu-core"]


def test_a_reseed_replaces_the_edges(database):
    store = CardStore(database)
    seed_cards([dsu(), kruskal(edge())], store=store, modules=MODULES)

    seed_cards([kruskal()], store=store, modules=MODULES)

    card = store.by_slug("minimum-tree")
    assert card is not None
    assert card.requires == []


def test_a_slug_seeded_twice_in_one_batch_is_refused(database):
    result = seed_cards([dsu(), dsu()], store=CardStore(database), modules=MODULES)

    assert [(one.index, one.reason) for one in result.rejected] == [(1, "seeded twice: union-find")]


def test_a_card_stored_as_authored_is_not_written_again(database):
    """A re-seed after one edit writes one card, which through a tunnel is
    the difference between seconds and minutes."""
    store = CardStore(database)
    seed_cards([dsu(), kruskal(edge())], store=store, modules=MODULES)

    result = seed_cards(
        [dsu(), kruskal(edge(), title="Kruskal, revised")], store=store, modules=MODULES
    )

    assert (result.unchanged, result.updated, result.ingested) == (1, 1, 0)
    assert store.by_slug("minimum-tree").title == "Kruskal, revised"


def test_a_card_naming_no_seeded_module_is_rejected(database):
    """A module no store holds pairs the card with no subtopic."""
    result = seed_cards([record(module="algorithms")], store=CardStore(database), modules=MODULES)

    assert [one.reason for one in result.rejected] == ["no seeded module: algorithms"]


def test_a_citation_naming_no_seeded_subtopic_is_rejected(database):
    """A citation links a subtopic the card's page could not open."""
    cited = template(cites=["py/stdlib/collections"])

    result = seed_cards([record(templates=[cited])], store=CardStore(database), modules=MODULES)

    assert [one.reason for one in result.rejected] == ["no seeded subtopic: py/stdlib/collections"]


def test_a_citation_naming_a_seeded_subtopic_is_stored(database):
    store = CardStore(database)
    cited = template(cites=["py/stdlib/collections"])

    seed_cards(
        [record(templates=[cited])],
        store=store,
        modules=MODULES,
        subtopics={"py/stdlib/collections"},
    )

    assert store.all()[0].templates[0].cites == ["py/stdlib/collections"]
