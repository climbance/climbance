"""Generate the views in `docs/architecture/README.md`, and each flow's sequence
diagram in the page the flow names, from `docs/architecture/model.toml`, and
check them.

    python3 tools/model_views.py write   # rewrite the views
    python3 tools/model_views.py check   # fail on a stale view or broken model
"""

import re
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs" / "architecture"
MODEL = DOCS / "model.toml"
README = DOCS / "README.md"
BEGIN = "<!-- generated from model.toml by `just model-views`, never edited -->"
END = "<!-- end of the generated views -->"
FLOW_BEGIN = "<!-- generated from model.toml by `just model-views`, never edited: the flow -->"
FLOW_END = "<!-- end of the generated flow -->"
KINDS = {"person", "system", "container", "library", "component"}
ACCESS = {"reads", "writes"}


def load() -> dict:
    return tomllib.loads(MODEL.read_text())


def relation_problems(model: dict, ids: list[str]) -> list[str]:
    found = []
    for r in model["relation"]:
        found += [f"a relation names `{r[end]}`" for end in ("from", "to") if r[end] not in ids]
        if r.get("access") not in ACCESS:
            found.append(f"the relation from `{r['from']}` to `{r['to']}` lacks `access`")
    return found


def problems(model: dict) -> list[str]:
    found = []
    elements = [model["engine"], *model["element"]]
    ids = [e["id"] for e in elements]
    found += [f"`{i}` is defined twice" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for e in model["element"]:
        if e["kind"] not in KINDS:
            found.append(f"`{e['id']}` has kind `{e['kind']}`")
        if (e["kind"] == "component") != ("container" in e):
            found.append(f"`{e['id']}` names a container, or lacks one, against its kind")
        elif "container" in e and e["container"] not in ids:
            found.append(f"`{e['id']}` sits in `{e['container']}`, which is not an element")
    found += relation_problems(model, ids)
    pairs = {(r["from"], r["to"]) for r in model["relation"]}
    for f in model.get("flow", []):
        found += [
            f"flow `{f['id']}` step {n} has no relation from `{s['from']}` to `{s['to']}`"
            for n, s in enumerate(f["steps"], 1)
            if (s["from"], s["to"]) not in pairs
        ]
    for e in elements + model.get("flow", []):
        path = DOCS / e["doc"]
        if not path.is_file():
            found.append(f"`{e['id']}` cites `{e['doc']}`, which does not exist")
            continue
        text = path.read_text()
        if "section" not in e:  # the file documents this element alone
            continue
        if not re.search(rf"^#{{2,3}} {re.escape(e['section'])}$", text, re.M):
            found.append(f"`{e['id']}` cites a section `{e['doc']}` lacks: {e['section']}")
        elif "bullet" in e and f"**{e['bullet']}" not in re.sub(r"\s+", " ", text):
            found.append(f"`{e['id']}` cites a bullet `{e['doc']}` no longer holds: {e['bullet']}")
    return found


def label(text: str) -> str:
    return text.replace("`", "").replace('"', "#quot;")


def key(element_id: str) -> str:
    return element_id.replace("-", "_")  # a hyphen in a Mermaid id reads as the start of an edge


def node(e: dict) -> str:
    return f'{key(e["id"])}["{label(e["name"])}<br/>{label(e["role"])}"]'


def edge(source: str, target: str, text: str, reads: bool) -> str:
    return f'    {key(source)} {"-.->" if reads else "-->"}|"{label(text)}"| {key(target)}'


def joined(after: dict[str, set[str]], source: str, target: str) -> bool:
    seen, todo = {source}, [source]
    while todo:
        for n in after.get(todo.pop(), ()):
            if n == target:
                return True
            if n not in seen:
                seen.add(n)
                todo.append(n)
    return False


def edges(model: dict, shown: set[str], owner: dict[str, str]) -> list[str]:
    # a relation reaching a hidden element is drawn at the element holding it,
    # unless a path of relations between shown elements already joins that pair

    def up(element_id: str) -> str:
        while element_id not in shown:
            element_id = owner[element_id]
        return element_id

    after: dict[str, set[str]] = {}
    for r in model["relation"]:
        if {r["from"], r["to"]} <= shown:
            after.setdefault(r["from"], set()).add(r["to"])
    labels: dict[tuple[str, str], list[str]] = {}
    reads: dict[tuple[str, str], bool] = {}
    for r in model["relation"]:
        pair = (up(r["from"]), up(r["to"]))
        mapped = pair != (r["from"], r["to"])
        if pair[0] == pair[1] or (mapped and joined(after, *pair)):
            continue
        if r["label"] not in labels.setdefault(pair, []):
            labels[pair].append(r["label"])
        reads[pair] = reads.get(pair, True) and r["access"] == "reads"
    return [edge(s, t, "; ".join(texts), reads[s, t]) for (s, t), texts in labels.items()]


def owners(model: dict) -> dict[str, str]:
    engine = model["engine"]["id"]
    return {e["id"]: e.get("container", engine) for e in model["element"]}


def context(model: dict) -> list[str]:
    outside = [e for e in model["element"] if e["kind"] in ("person", "system")]
    shown = {model["engine"]["id"], *(e["id"] for e in outside)}
    lines = ["flowchart TB", "    " + node(model["engine"])]
    lines += ["    " + node(e) for e in outside]
    return lines + edges(model, shown, owners(model))


def containers(model: dict) -> list[str]:
    engine = model["engine"]
    lines = ["flowchart TB"]
    outside = [e for e in model["element"] if e["kind"] in ("person", "system")]
    inside = [e for e in model["element"] if e["kind"] in ("container", "library")]
    lines += ["    " + node(e) for e in outside]
    lines.append(f'    subgraph {key(engine["id"])}["{label(engine["name"])}"]')
    lines += ["        " + node(e) for e in inside]
    lines.append("    end")
    shown = {e["id"] for e in outside + inside}
    return lines + edges(model, shown, owners(model))


def components(model: dict, container: dict) -> list[str]:
    parts = [e for e in model["element"] if e.get("container") == container["id"]]
    ids = {e["id"] for e in parts}
    owner = owners(model)
    level = {e["id"] for e in model["element"] if e["kind"] != "component"} | ids
    touching = [r for r in model["relation"] if r["from"] in ids or r["to"] in ids]
    near = {end if end in level else owner[end] for r in touching for end in (r["from"], r["to"])}
    near -= ids | {container["id"]}
    lines = ["flowchart TB"]
    lines += ["    " + node(e) for e in model["element"] if e["id"] in near]
    lines.append(f'    subgraph {key(container["id"])}["{label(container["name"])}"]')
    lines += ["        " + node(e) for e in parts]
    lines.append("    end")
    return lines + edges({**model, "relation": touching}, ids | near, owner)


def sequence(model: dict, flow: dict) -> list[str]:
    names = {e["id"]: e["name"] for e in [model["engine"], *model["element"]]}
    labels = {(r["from"], r["to"]): r["label"] for r in model["relation"]}
    lines = ["sequenceDiagram"]
    seen: list[str] = []
    for s in flow["steps"]:
        seen += [end for end in (s["from"], s["to"]) if end not in seen]
    lines += [f"    participant {key(i)} as {label(names[i])}" for i in seen]
    for s in flow["steps"]:
        text = label(labels[(s["from"], s["to"])]).replace(";", "#59;")
        lines.append(f"    {key(s['from'])}->>{key(s['to'])}: {text}")
    return lines


def views(model: dict) -> str:
    block = [
        BEGIN,
        "",
        "## Views",
        "",
        "A dashed arrow reads and leaves its target unchanged. A solid arrow writes,",
        "or starts a run.",
        "",
        "The engine's context: who uses it and what it reaches outside itself.",
        "",
        "```mermaid",
        *context(model),
        "```",
        "",
        "The engine's containers: what runs on its own, and what each talks to.",
        "",
        "```mermaid",
        *containers(model),
        "```",
    ]
    for container in model["element"]:
        if any(e.get("container") == container["id"] for e in model["element"]):
            block += [
                "",
                f"The {container['name']}'s components, and what each reads and writes.",
                "",
                "```mermaid",
                *components(model, container),
                "```",
            ]
    block += ["", END]
    return "\n".join(block)


def rendered(text: str, model: dict) -> str:
    if BEGIN in text:
        head, rest = text.split(BEGIN, 1)
        return head + views(model) + rest.split(END, 1)[1]
    head, rest = text.split("\n## ", 1)  # the views open the file, before its first section
    return f"{head}\n{views(model)}\n\n## {rest}"


def drawn(text: str, model: dict, flow: dict) -> str:
    head, rest = text.split(FLOW_BEGIN, 1)
    block = [FLOW_BEGIN, "", "```mermaid", *sequence(model, flow), "```", "", FLOW_END]
    return head + "\n".join(block) + rest.split(FLOW_END, 1)[1]


def main(command: str) -> int:
    model = load()
    found = problems(model)
    if found:  # a view drawn from a broken model would raise or mislead
        for line in found:
            sys.stderr.write(f"model views: {line}\n")
        return 1
    pages: dict[Path, Callable[[str], str]] = {README: lambda text: rendered(text, model)}
    for flow in model.get("flow", []):
        path = DOCS / flow["doc"]
        if FLOW_BEGIN not in path.read_text():
            found.append(f"flow `{flow['id']}`: `{flow['doc']}` has no place marked for it")
            continue
        pages[path] = lambda text, flow=flow: drawn(text, model, flow)  # bound per flow
    for path, draw in pages.items():
        text = path.read_text()
        if command == "write":
            path.write_text(draw(text))
        elif draw(text) != text:
            found.append(f"`{path.relative_to(DOCS)}` is stale: run `just model-views`")
    for line in found:
        sys.stderr.write(f"model views: {line}\n")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "check"))
