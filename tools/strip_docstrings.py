"""
Make copies of picozero without docstrings, for installing on a Raspberry Pi
Pico.

MicroPython throws docstrings away when it compiles a module, but while it
compiles picozero.py from source it has to hold all of them in memory, and
that takes most of the free memory on a Pico with an RP2040. The docstrings
are only needed for the documentation, which is built from the source in
picozero/, so the copies that are installed on a Pico are made without them:

- setup.py removes them when it builds the package that pip and Thonny
  install.
- This script writes the copy in device/ that mip and the manual install use.

Docstrings are replaced by blank lines, so line numbers in error messages from
a Pico are the same as in picozero/.

Usage, from the repository folder:

    python3 tools/strip_docstrings.py          # update device/ from picozero/
    python3 tools/strip_docstrings.py --check  # fail if device/ is out of date

Needs Python 3.8 or later.
"""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(ROOT, "picozero")
DEVICE_DIR = os.path.join(ROOT, "device", "picozero")

_HAS_BODY = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def _docstrings(tree):
    # (docstring node, whether it is the only statement in its body)
    for node in ast.walk(tree):
        if isinstance(node, _HAS_BODY) and node.body:
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                yield first, len(node.body) == 1


def _without_docstrings(source):
    # a dump of the code, ignoring docstrings and line numbers
    tree = ast.parse(source)
    for node in [n for n in ast.walk(tree) if isinstance(n, _HAS_BODY)]:
        if node.body:
            first = node.body[0]
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                node.body = node.body[1:] or [ast.Pass()]
    return ast.dump(tree)


def _split(line, byte_offset):
    # ast gives column offsets in bytes of UTF-8
    data = line.encode("utf-8")
    return data[:byte_offset].decode("utf-8"), data[byte_offset:].decode("utf-8")


def strip_docstrings(source):
    """
    Return ``source`` without its docstrings. Each docstring is replaced by
    blank lines (or ``pass``, if it was the only statement in its body), so
    the result has the same number of lines. A docstring that shares a line
    with other code is left as it is.
    """
    lines = source.splitlines(True)
    found = sorted(_docstrings(ast.parse(source)), key=lambda d: -d[0].lineno)
    for docstring, only_statement in found:
        first = docstring.lineno - 1
        last = docstring.end_lineno - 1
        indent = _split(lines[first], docstring.col_offset)[0]
        after = _split(lines[last], docstring.end_col_offset)[1]
        if indent.strip() or after.strip():
            continue
        for i in range(first, last + 1):
            ending = lines[i][len(lines[i].rstrip("\r\n")) :]
            lines[i] = ending
        if only_statement:
            lines[first] = indent + "pass" + lines[first]

    result = "".join(lines)
    if result.count("\n") != source.count("\n"):
        raise ValueError("removing the docstrings changed the number of lines")
    if _without_docstrings(result) != _without_docstrings(source):
        raise ValueError("removing the docstrings changed the code")
    return result


def _read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def main(args):
    check = "--check" in args
    out_of_date = []
    names = sorted(n for n in os.listdir(SOURCE_DIR) if n.endswith(".py"))
    for name in names:
        stripped = strip_docstrings(_read(os.path.join(SOURCE_DIR, name)))
        path = os.path.join(DEVICE_DIR, name)
        if os.path.exists(path) and _read(path) == stripped:
            continue
        out_of_date.append(os.path.relpath(path, ROOT))
        if not check:
            os.makedirs(DEVICE_DIR, exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(stripped)
    for name in sorted(os.listdir(DEVICE_DIR)) if os.path.isdir(DEVICE_DIR) else []:
        if name.endswith(".py") and name not in names:
            out_of_date.append(os.path.relpath(os.path.join(DEVICE_DIR, name), ROOT))
            if not check:
                os.remove(os.path.join(DEVICE_DIR, name))

    if check:
        if out_of_date:
            print("out of date, run python3 tools/strip_docstrings.py:")
            for path in out_of_date:
                print("  " + path)
            return 1
        print("device/ is up to date")
    else:
        for path in out_of_date:
            print("updated " + path)
        if not out_of_date:
            print("device/ is already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
