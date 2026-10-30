"""Static line/test counts for an untrusted tree. Reads files only; imports nothing from it."""
import ast, io, sys, tokenize, json
from pathlib import Path

root = Path(sys.argv[1])
files = sys.argv[2:]

def py_counts(text):
    total = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
    blank = sum(1 for l in text.splitlines() if not l.strip())
    comment_lines = set()
    code_lines = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                comment_lines.add(tok.start[0])
            elif tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
                for ln in range(tok.start[0], tok.end[0] + 1):
                    code_lines.add(ln)
    except tokenize.TokenError:
        pass
    # docstring lines
    doc = set()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            b = node.body
            if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) and isinstance(b[0].value.value, str):
                doc.update(range(b[0].lineno, b[0].end_lineno + 1))
    sloc = len(code_lines - doc)
    tests = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for f in node.body:
                if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name.startswith("test"):
                    tests += 1
    return {"total": total, "blank": blank, "comment_only": len(comment_lines - code_lines), "docstring": len(doc), "sloc": sloc, "test_methods": tests}

out = {}
for f in files:
    p = root / f
    text = p.read_text(encoding="utf-8")
    if f.endswith(".py"):
        out[f] = py_counts(text)
    else:
        out[f] = {"total": text.count("\n"), "blank": sum(1 for l in text.splitlines() if not l.strip())}
print(json.dumps(out, indent=1))
