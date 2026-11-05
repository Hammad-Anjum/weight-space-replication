"""Git "clean" filter: strips local, machine-specific details from files as they are committed. The working tree is
left untouched, which matters here because experiments write to these files while they run.

Set it up once per clone (local git config, not committed):
    git config filter.sanitize.clean "python3 scripts/sanitize_paths.py %f"
    git config filter.sanitize.smudge cat
.gitattributes selects which files go through it.

Rewrites:
  - Python files: string literals holding an absolute path into the repo become paths relative to the file
    (the scripts that use them live one level below the repo root).
  - Shell files: `cd <abs repo>` becomes `cd "$(dirname "$0")/.."`.
  - All other text: <repo>, <scratch>, <tasks>, <home> placeholders for local paths. Codex thread ids become
    `id-` plus 8 hex digits, the same per thread (the convention of the upstream logs).
"""
import re
import sys

REPO = "<repo>"
SESSION = r"<tmp>"\s]+/[0-9a-f-]{36}"
HOME = "<home>"


def sanitize(path, text):
    if path.endswith(".py"):
        text = re.sub(r'"' + re.escape(REPO) + r'/([^"]*)"',
                      r'str(__import__("pathlib").Path(__file__).resolve().parents[1] / "\1")', text)
    elif path.endswith(".sh"):
        text = text.replace(f"cd {REPO}\n", 'cd "$(dirname "$0")/.."\n')
    text = text.replace(REPO, "<repo>")
    text = re.sub(SESSION + r"/scratchpad", "<scratch>", text)
    text = re.sub(SESSION + r"/tasks", "<tasks>", text)
    text = re.sub(SESSION, "<session>", text)
    text = re.sub(r"<tmp>"']*", "<tmp>", text)
    text = re.sub(r"(/private)?<tmp>"']*", "<tmp>", text)
    text = text.replace(HOME, "<home>")
    text = re.sub(r'("thread_id"\s*:\s*")([0-9a-f]{8})[0-9a-f-]{28}"', r'\1id-\2"', text)
    return text


if __name__ == "__main__":
    data = sys.stdin.buffer.read()
    try:
        out = sanitize(sys.argv[1] if len(sys.argv) > 1 else "", data.decode("utf-8")).encode("utf-8")
    except UnicodeDecodeError:
        out = data
    sys.stdout.buffer.write(out)
