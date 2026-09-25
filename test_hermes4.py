def run_fix():
    text = """plugins:
  enabled:
    - alpha
    - beta
  disabled:
    - gamma
    - delta
    - agency-agents-router
hooks_auto_accept: false"""

    lines = text.splitlines()
    plugin="agency-agents-router"
    plugin_strip = plugin.strip()

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

                # Check if we transitioned out of enabled block
                if has_enabled and enabled_end is None and stripped and not stripped.startswith("#"):
                    indent = len(jl) - len(jl.lstrip("\t "))
                    if indent <= len(enabled_indent):
                        enabled_end = j

                if stripped.startswith("enabled:") and not enabled_indent:
                    has_enabled = True
                    enabled_start = j
                    enabled_indent = jl[: len(jl) - len(stripped)]
                    if "[]" in stripped:
                        enabled_empty = True
                elif stripped.startswith("-") and has_enabled and enabled_end is None and not item_indent:
                    item_indent = jl[: len(jl) - len(stripped)]
                j += 1
            end_line = j if broke else len(lines)
            if has_enabled and enabled_end is None:
                enabled_end = end_line
            break

    print(f"plugin_start={plugin_start}, enabled_start={enabled_start}, enabled_end={enabled_end}, end_line={end_line}")
    print(f"enabled_indent='{enabled_indent}', item_indent='{item_indent}'")

    has_plugin_already = False
    if has_enabled and not enabled_empty:
        for idx in range(enabled_start + 1, enabled_end):
            l = lines[idx]
            stripped = l.strip()
            if not stripped.startswith("-"):
                continue
            if stripped.count("- ") > 1:
                pass # corrupted
            else:
                value = stripped[1:].strip().strip('"\'')
                if value == plugin_strip:
                    has_plugin_already = True

    print(f"has_plugin_already={has_plugin_already}")

    # We also need to remove stale references from the rest of the block (e.g. disabled:)
    stale_lines = []
    for idx in range(plugin_start + 1, end_line):
        # don't delete from enabled if already there, but delete if anywhere else
        if has_enabled and enabled_start <= idx < enabled_end:
            continue
        l = lines[idx]
        stripped = l.strip()
        if stripped.startswith("-"):
            value = stripped[1:].strip().strip('"\'')
            if value == plugin_strip:
                stale_lines.append(idx)

    print(f"stale_lines={stale_lines}")

    for idx in sorted(stale_lines, reverse=True):
        del lines[idx]
        end_line -= 1
        if has_enabled and enabled_end > idx:
            enabled_end -= 1

    if has_plugin_already:
        print("ALREADY HAS PLUGIN")
        return "\n".join(lines) + "\n"

    new_item_line = f"{item_indent or (enabled_indent + '  ')}- {plugin}"

    if plugin_start is None:
        pass # case 1
    elif enabled_empty:
        pass # case 2
    elif has_enabled and not item_indent and not enabled_empty:
        pass # case 3
    else:
        # insert at the end of the enabled block
        insert_at = None
        for idx in range(enabled_end - 1, enabled_start, -1):
            l = lines[idx]
            stripped = l.strip()
            if stripped.startswith("-"):
                if l != item_indent + stripped:
                    lines[idx] = item_indent + stripped
                insert_at = idx + 1
                break

        if insert_at is None and has_enabled:
            insert_at = enabled_start + 1

        if insert_at is not None:
            lines.insert(insert_at, new_item_line)

    return "\n".join(lines) + "\n"

print("--- RESULT ---")
print(run_fix())
