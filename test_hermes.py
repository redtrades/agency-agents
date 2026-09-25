def parse_hermes_config(text, plugin="agency-agents-router"):
    lines = text.splitlines()
    plugin_strip = plugin.strip()

    plugin_start = None
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
                if stripped.startswith("enabled:") and not enabled_indent:
                    has_enabled = True
                    enabled_indent = jl[: len(jl) - len(stripped)]
                    if "[]" in stripped:
                        enabled_empty = True
                elif stripped.startswith("-") and has_enabled and not item_indent:
                    item_indent = jl[: len(jl) - len(stripped)]
                j += 1
            end_line = j if broke else len(lines)
            break

    # Simulate insertion
    insert_at = None
    for idx in range(end_line - 1, plugin_start, -1):
        l = lines[idx]
        stripped = l.strip()
        if stripped.startswith("-"):
            if l != item_indent + stripped:
                lines[idx] = item_indent + stripped
            insert_at = idx + 1
            break

    print(f"insert_at={insert_at} lines[insert_at-1]={lines[insert_at-1]}")

text = """plugins:
  enabled:
    - alpha
    - beta
  disabled:
    - gamma
    - delta
hooks_auto_accept: false
"""
parse_hermes_config(text)
