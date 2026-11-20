import argparse
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from climb.knowledge.refresh import Refreshed, refresh


def library(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    content = Path(args.content)
    modules = sorted(p.parent for p in (content / "modules").glob("*/course.toml"))
    if args.module:
        modules = [m for m in modules if m.name == args.module]
        if not modules:
            parser.exit(2, f"library refresh: no module {args.module} under {content}\n")
    found = refresh(modules, content / "library", date.today())
    if args.json:
        print(json.dumps(asdict(found), indent=2))
    else:
        for line in lines(found):
            print(line)
    if found.broken or found.failed:
        parser.exit(1)


def lines(found: Refreshed) -> list[str]:
    out = [
        f"{len(found.unchanged) + len(found.changed) + len(found.failed)} sources: "
        f"{len(found.unchanged)} unchanged, {len(found.changed)} changed, "
        f"{len(found.failed)} not fetched"
    ]
    out += [f"changed  {url}" for url in found.changed]
    out += [f"failed   {url}: {why}" for url, why in found.failed.items()]
    out += [f"moved    read_on of {key}" for key in found.moved]
    for b in found.broken:
        out.append(f"broken   {b.module} {b.file} {b.concept}: {b.url} ({b.snapshot})")
        out.append(f"  was    {b.held}")
        out.append(f"  now    {b.now or 'nothing alike'}")
    return out
