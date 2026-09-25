def test_parse():
    text = """plugins:
  enabled:
    - alpha
    - beta
  disabled:
    - gamma
    - delta
hooks_auto_accept: false"""

    lines = text.splitlines()
    plugin="agency-agents-router"

    plugin_start = None
    enabled_start = None
    enabled_end = None
    end_line = None
    enabled_indent = ""
    item_indent = ""
    has_enabled = False
    enabled_empty = False

    for i, line in enumerate(lines):
        if line.startswith("plugins:"):
            plugin_start = i
            j = i + 1
            broke = False
            while j < len(lines):
                jl = lines[j]
                if jl and not jl.startswith((" ", "\t")):
                    broke = True
                    break
                stripped = jl.strip()
                if stripped.startswith("enabled:"):
                    if not enabled_indent:
                        has_enabled = True
                        enabled_start = j
                        enabled_indent = jl[: len(jl) - len(stripped)]
                        if "[]" in stripped:
                            enabled_empty = True

                # Check if we moved to a sibling key of enabled:
                elif has_enabled and enabled_end is None:
                    # if it's a key and has same or less indent than enabled_indent
                    # we should probably also look at jl.strip().endswith(":") but maybe not strictly necessary
                    # if the line is not empty, does not start with #, and its indent is <= enabled_indent
                    if jl.strip() and not jl.strip().startswith("#"):
                        indent = len(jl) - len(jl.lstrip())
                        if indent <= len(enabled_indent) and jl.strip().endswith(":"):
                            enabled_end = j

                elif stripped.startswith("-") and has_enabled and enabled_end is None and not item_indent:
                    item_indent = jl[: len(jl) - len(stripped)]
                j += 1
            end_line = j if broke else len(lines)
            if has_enabled and enabled_end is None:
                enabled_end = end_line
            break

    print(f"plugin_start={plugin_start}, enabled_start={enabled_start}, enabled_end={enabled_end}, end_line={end_line}")

test_parse()
