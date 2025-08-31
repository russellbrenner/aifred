#!/usr/bin/env python3
import os
import sys
import zipfile
from pathlib import Path


INCLUDE_EXT = {".py", ".plist", ".png", ".icns", ".md", ".txt"}


def should_include(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    if path.is_dir():
        return path.name in {"providers", "utils", "assets"}
    if path.suffix in INCLUDE_EXT:
        return True
    return False


def main():
    root = Path(__file__).parent
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / "aifred.alfredworkflow"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in [root / "info.plist", root / "README.md", root / "LICENSE", root / "requirements.txt", root / "setup.py", root / "aifred.py", root / "alfred_filter.py", root / "alfred_action.py", root / "store.py", root / "build_workflow.py"]:
            if p.exists():
                z.write(p, p.name)
        for sub in (root / "providers", root / "utils", root / "assets"):
            if not sub.exists():
                continue
            for path in sub.rglob("*"):
                if path.is_file() and should_include(path):
                    z.write(path, str(path.relative_to(root)))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

