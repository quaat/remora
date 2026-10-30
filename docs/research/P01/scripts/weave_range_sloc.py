"""SLOC (code-token lines minus docstring lines) within line ranges of an untrusted Python file. Parses only."""
import ast, io, sys, tokenize
from pathlib import Path
path = Path(sys.argv[1]); text = path.read_text(encoding="utf-8")
code = set()
for tok in tokenize.generate_tokens(io.StringIO(text).readline):
    if tok.type not in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
        code.update(range(tok.start[0], tok.end[0] + 1))
doc = set()
for node in ast.walk(ast.parse(text)):
    if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
        b = node.body[0]
        if isinstance(b, ast.Expr) and isinstance(getattr(b, "value", None), ast.Constant) and isinstance(b.value.value, str):
            doc.update(range(b.lineno, b.end_lineno + 1))
s = code - doc
for spec in sys.argv[2:]:
    a, b = map(int, spec.split("-"))
    print(f"{path.name}:{a}-{b} physical={b-a+1} sloc={len([l for l in s if a <= l <= b])}")
