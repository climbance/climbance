import json
from pathlib import Path

from authoring import question, written
from test_seed_cards import record, template
from test_seed_knowledge import COURSE, authored

from climb.knowledge import read_module
from climb.knowledge.authoring import check
from climb.knowledge.authoring.pairing import Paired, paired

SUBS = 'subs = ["types", "flow"]\n'


def module(tmp_path: Path, techniques: str, needs: str = "", subs: str = SUBS) -> Path:
    base = authored(tmp_path, graph=f"format = 2\n[needs]\n{needs}\n")
    (base / "course.toml").write_text(COURSE.replace(SUBS, subs + techniques))
    return base


def card(slug: str, technique: str, *requires: str, module: str = "python") -> dict:
    """Primary for the module `authored` writes, `python`, unless named."""
    return record(
        slug,
        technique=technique,
        module=module,
        templates=[template("form")],
        requires=[{"card": one, "template": "form", "used_by": "form"} for one in requires],
    )


def cards(tmp_path: Path, *held: dict) -> Path:
    base = tmp_path / "cards"
    base.mkdir()
    for one in held:
        (base / f"{one['slug']}.json").write_text(json.dumps(one))
    return base


def test_a_prerequisite_against_a_requirement_is_refused(tmp_path):
    """The card graph has stack first, and the prerequisite graph DFS first."""
    root = module(
        tmp_path,
        'sub_techniques = { types = ["stack"], flow = ["depth-first-search"] }\n',
        needs='"types" = ["flow"]',
    )
    held = cards(tmp_path, card("stack", "stack"), card("dfs", "depth-first-search", "stack"))

    (found,) = paired(read_module(root), held).errors

    assert "depth-first-search -> stack (card dfs)" in found
    assert "stack -> depth-first-search (subtopic types needs flow)" in found


def test_graphs_agreeing_on_the_order_pass(tmp_path):
    root = module(
        tmp_path,
        'sub_techniques = { types = ["stack"], flow = ["depth-first-search"] }\n',
        needs='"flow" = ["types"]',
    )
    held = cards(tmp_path, card("stack", "stack"), card("dfs", "depth-first-search", "stack"))

    assert paired(read_module(root), held).errors == []


def test_a_subtopic_naming_no_technique_passes_its_edges_through(tmp_path):
    """Stack's subtopic needs DFS's through one naming none, which still puts
    DFS's facts first."""
    root = module(
        tmp_path,
        'sub_techniques = { types = ["stack"], flow = ["depth-first-search"] }\n',
        needs='"types" = ["plain"]\n"plain" = ["flow"]',
        subs='subs = ["types", "flow", "plain"]\n',
    )
    held = cards(tmp_path, card("stack", "stack"), card("dfs", "depth-first-search", "stack"))

    (found,) = paired(read_module(root), held).errors

    assert "subtopic types needs flow" in found


def test_two_techniques_of_one_subtopic_draw_no_edge_between_them(tmp_path):
    """A subtopic teaching both reads as neither first."""
    root = module(tmp_path, 'sub_techniques = { flow = ["stack", "depth-first-search"] }\n')
    held = cards(tmp_path, card("stack", "stack"), card("dfs", "depth-first-search", "stack"))

    assert paired(read_module(root), held).errors == []


def test_a_module_naming_no_technique_needs_no_cards(tmp_path):
    root = module(tmp_path, "")

    assert paired(read_module(root), tmp_path / "nowhere") == Paired()


def test_a_module_naming_a_technique_with_no_cards_beside_it_is_refused(tmp_path):
    """Reading no cards would pass every module, so the check refuses."""
    root = module(tmp_path, 'sub_techniques = { flow = ["stack"] }\n')

    (found,) = paired(read_module(root), tmp_path / "nowhere").errors

    assert found.startswith("no cards at")


def test_the_module_check_reads_the_cards_beside_the_modules(tmp_path):
    """Two cards whose requirements order stack and DFS both ways, found under
    `content/cards` from `content/modules/<slug>`."""
    root = written(tmp_path, [question("a")])
    with (root / "course.toml").open("a") as course:
        course.write('[[topic]]\nslug = "t"\ntier = 1\ntitle = "T"\nsubs = ["sub"]\n')
        course.write('sub_techniques = { sub = ["stack"] }\n')
    cards(
        tmp_path,
        card("stack", "stack", "dfs"),
        card("dfs", "depth-first-search"),
        card("stack-again", "stack"),
        card("dfs-again", "depth-first-search", "stack-again"),
    )

    errors = check(root, run=False).report.errors

    (found,) = [e for e in errors if e.startswith("[0] graph:")]
    assert "stack -> depth-first-search (card stack)" in found
    assert "depth-first-search -> stack (card dfs-again)" in found


def test_a_card_whose_technique_no_subtopic_names_is_listed(tmp_path):
    root = module(tmp_path, 'sub_techniques = { flow = ["stack"] }\n')
    held = cards(tmp_path, card("stack", "stack"), card("dfs", "depth-first-search", "stack"))

    assert paired(read_module(root), held).unnamed == [
        "card dfs: no subtopic names depth-first-search"
    ]


def test_the_module_check_warns_on_an_unnamed_card_and_refuses_nothing(tmp_path):
    """A card is studied in full without its subtopic, so the list is work
    still to write."""
    root = written(tmp_path, [question("a")])
    with (root / "course.toml").open("a") as course:
        course.write('[[topic]]\nslug = "t"\ntier = 1\ntitle = "T"\nsubs = ["sub"]\n')
        course.write('sub_techniques = { sub = ["stack"] }\n')
    cards(tmp_path, card("stack", "stack", module="m"), card("heap", "heap", module="m"))

    report = check(root, run=False).report

    assert "[0] cards: card heap: no subtopic names heap" in report.warnings
    assert not any("cards:" in e for e in report.errors)


def test_a_card_another_module_is_primary_for_is_not_listed(tmp_path):
    """Another module's card is that module's gap, not this one's."""
    root = module(tmp_path, 'sub_techniques = { flow = ["stack"] }\n')
    held = cards(tmp_path, card("stack", "stack"), card("go", "hashing", module="go"))

    assert paired(read_module(root), held).unnamed == []


def test_every_card_is_listed_before_the_module_names_a_technique(tmp_path):
    """The gap list of a module not yet written is every card it is primary
    for."""
    root = module(tmp_path, "")
    held = cards(tmp_path, card("stack", "stack"), card("heap", "heap"))

    assert paired(read_module(root), held).unnamed == [
        "card heap: no subtopic names heap",
        "card stack: no subtopic names stack",
    ]
