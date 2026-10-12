import sys
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 qwen_sanitize.py <file>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    inside_code_block = False
    language = None
    new_lines = []

    js_ts_langs = {'javascript', 'js', 'typescript', 'ts', 'jsx', 'tsx', 'json'}
    bash_langs = {'bash', 'sh', 'shell', 'yaml', 'yml'}

    js_pattern = re.compile(r'\$\{([a-zA-Z_]\w*)\}')
    bash_pattern = re.compile(r'\$\{([a-zA-Z_]\w*)\}')

    def js_replace(match):
        return f"${{ {match.group(1)}}}"

    def bash_replace(match):
        id_name = match.group(1)
        end = match.end()
        next_char = match.string[end] if end < len(match.string) else ''
        if next_char.isalnum() or next_char == '_':
            # Wrapping the variable in double quotes isolates it from the following characters.
            # Example:
            #   ${foo}bar -> "$foo"bar
            #   "${foo}bar" -> ""$foo"bar" (evaluates seamlessly in bash)
            return f'"${id_name}"'
        return f"${id_name}"

    for line in lines:
        if line.startswith('```'):
            inside_code_block = not inside_code_block
            if inside_code_block:
                lang = line[3:].strip().lower()
                language = lang
            else:
                language = None
            new_lines.append(line)
            continue

        if inside_code_block:
            if language in js_ts_langs:
                line = js_pattern.sub(js_replace, line)
            elif language in bash_langs:
                line = bash_pattern.sub(bash_replace, line)

        new_lines.append(line)

    with open(sys.argv[1], 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

if __name__ == '__main__':
    main()
