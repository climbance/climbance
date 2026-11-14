import json
from pathlib import Path

from authoring import question, written
from test_seed_cards import record, template
from test_seed_knowledge import COURSE, authored

from climb.knowledge import read_module
from climb.knowledge.authoring import check
from climb.knowledge.authoring.pairing import crossed

SUBS = 'subs = ["types", "flow"]\n'


def module(tmp_path: Path, techniques: str, needs: str = "", subs: str = SUBS) -> Path:
    base = authored(tmp_path, graph=f"format = 2\n[needs]\n{needs}\n")
    (base / "course.toml").write_text(COURSE.replace(SUBS, subs + techniques))
    return base


def card(slug: str, technique: str, *requires: str) -> dict:
    return record(
        slug,
        technique=technique,
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

    (found,) = crossed(read_module(root), held)

    assert "depth-first-search -> stack (card dfs)" in found
    assert "stack -> depth-first-search (subtopic types needs flow)" in found


def test_graphs_agreeing_on_the_order_pass(tmp_path):
    root = module(
        tmp_path,
        'sub_techniques = { types = ["stack"], flow = ["depth-first-search"] }\n',
        needs='"flow" = ["types"]',
    )
    held = cards(tmp_path, card("stack", "stack"), card("dfs", "depth-first-search", "stack"))

    assert crossed(read_module(root), held) == []


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

    (found,) = crossed(read_module(root), held)

    assert "subtopic types needs flow" in found


def test_two_techniques_of_one_subtopic_draw_no_edge_between_them(tmp_path):
    """A subtopic teaching both reads as neither first."""
    root = module(tmp_path, 'sub_techniques = { flow = ["stack", "depth-first-search"] }\n')
    held = cards(tmp_path, card("stack", "stack"), card("dfs", "depth-first-search", "stack"))

    assert crossed(read_module(root), held) == []


def test_a_module_naming_no_technique_reads_no_cards(tmp_path):
    root = module(tmp_path, "")

    assert crossed(read_module(root), tmp_path / "nowhere") == []


def test_a_module_naming_a_technique_with_no_cards_beside_it_is_refused(tmp_path):
    """Reading no cards would pass every module, so the check refuses."""
    root = module(tmp_path, 'sub_techniques = { flow = ["stack"] }\n')

    (found,) = crossed(read_module(root), tmp_path / "nowhere")

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
