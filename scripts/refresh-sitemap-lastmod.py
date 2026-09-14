#!/usr/bin/env python3
"""Refresh sitemap lastmod values from the files' actual Git change dates."""

from __future__ import annotations

import datetime as dt
import re
import subprocess
from pathlib import Path


SITE = Path(__file__).resolve().parents[1]
SITEMAP = SITE / "sitemap.xml"
TODAY = dt.date.today().isoformat()


def source_file(url: str) -> Path:
    tail = url.rstrip("/").rsplit("/", 1)[-1]
    return SITE / (tail if tail.endswith(".html") else "index.html")


def git_date(path: Path) -> str:
    rel = path.relative_to(SITE).as_posix()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", rel],
        cwd=SITE,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if dirty:
        return TODAY
    committed = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", rel],
        cwd=SITE,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return committed or TODAY


def patch_block(match: re.Match[str]) -> str:
    block = match.group(0)
    loc = re.search(r"<loc>([^<]+)</loc>", block)
    if not loc:
        return block
    path = source_file(loc.group(1))
    if not path.exists():
        raise FileNotFoundError(f"Sitemap URL has no local page: {loc.group(1)}")
    return re.sub(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{git_date(path)}</lastmod>", block, count=1)


def main() -> None:
    before = SITEMAP.read_text(encoding="utf-8")
    after = re.sub(r"<url>.*?</url>", patch_block, before, flags=re.S)
    SITEMAP.write_text(after, encoding="utf-8")
    changed = sum(a != b for a, b in zip(re.findall(r"<lastmod>([^<]+)", before), re.findall(r"<lastmod>([^<]+)", after)))
    print(f"Refreshed {changed} sitemap lastmod values from real file history.")


if __name__ == "__main__":
    main()
