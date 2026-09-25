def parse_hermes_config(text, plugin="agency-agents-router"):
    lines = text.splitlines()
    plugin_strip = plugin.strip()

    plugin_start = None
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
            in_enabled_block = False
            while j < len(lines):
                jl = lines[j]
                if jl and not jl.startswith((" ", "\t")):
                    broke = True
                    break

                stripped = jl.strip()

                # Check for block transitions
                if jl and jl.startswith((" ", "\t")) and stripped.endswith(":"):
                    current_indent = jl[: len(jl) - len(stripped)]
                    if current_indent == enabled_indent and stripped != "enabled:":
                        in_enabled_block = False
                        if enabled_end is None:
                           enabled_end = j

                if stripped.startswith("enabled:") and not enabled_indent:
                    has_enabled = True
                    in_enabled_block = True
                    enabled_indent = jl[: len(jl) - len(stripped)]
                    if "[]" in stripped:
                        enabled_empty = True
                elif stripped.startswith("-") and has_enabled and in_enabled_block and not item_indent:
                    item_indent = jl[: len(jl) - len(stripped)]
                j += 1

            end_line = j if broke else len(lines)
            if enabled_end is None:
                enabled_end = end_line
            break

    print(f"plugin_start={plugin_start}, enabled_end={enabled_end}, end_line={end_line}, has_enabled={has_enabled}, enabled_indent='{enabled_indent}', item_indent='{item_indent}'")

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

text2 = """plugins:
  disabled:
    - gamma
  enabled:
    - alpha
"""
parse_hermes_config(text2)
