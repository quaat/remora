"""Physical and code (non-blank, non-comment-only) line counts for line ranges of an untrusted file."""
import sys
from pathlib import Path
path = Path(sys.argv[1]); lines = path.read_text(encoding="utf-8").splitlines()
for spec in sys.argv[2:]:
    a, b = map(int, spec.split("-"))
    seg = lines[a-1:b]
    code = sum(1 for l in seg if l.strip() and not l.strip().startswith("#"))
    print(f"{path.name}:{a}-{b} physical={len(seg)} nonblank_noncomment={code}")
