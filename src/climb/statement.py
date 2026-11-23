def signed(statement: str) -> tuple[str, str | None]:
    """The prose before the `def solve(...)` line a statement ends on, and that
    line. Split here so no renderer reads a parameter name as markup."""
    text = statement.rstrip()
    # a generated statement ends on the line bare, or inside a fenced block
    fenced = text.endswith("```")
    body = text.removesuffix("```").rstrip()
    start = body.rfind("def solve(")
    at_line_start = start == 0 or (start > 0 and body[start - 1] == "\n")
    if start == -1 or not at_line_start or "\n" in body[start:]:
        return statement, None
    prose = body[:start].rstrip()
    if fenced:
        prose = prose[: prose.rfind("```")].rstrip()
    return prose, body[start:]
