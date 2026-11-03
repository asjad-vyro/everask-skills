#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pyyaml>=6"]
# ///
"""Check this repo against the EverAsk Skills Library import rules.

    uv run scripts/validate.py
    # or: pip install pyyaml && python3 scripts/validate.py

Every top-level folder named after a Library type (document, slides, website,
research, email, data, marketing, engineering) is one import link, because one
import gives every skill the same type. For each link it checks:

- each folder has SKILL.md at its top, and no skill sits inside another skill;
- skills are at most 3 levels below the type folder, and at most 50 per folder;
- SKILL.md frontmatter is valid YAML with a name of 1-64 characters (at least
  one English letter or digit) and a description of 1-1024 characters;
- each skill has at most 100 files and 25 MiB, a LICENSE, and no symlinks or
  OS junk;
- covers, when present: cover.png, .jpg, .webp or .gif next to SKILL.md, of
  that image type, and small;
- the folder and the whole repo against 1000 files and 50 MiB per link.

Exits 1 if anything fails.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("validate.py needs PyYAML: run `uv run scripts/validate.py`, or `pip install pyyaml` first.")

ROOT = Path(__file__).resolve().parent.parent
TYPES = ("document", "slides", "website", "research", "email", "data", "marketing", "engineering")
MIB = 1024 * 1024
NAME_MAX, DESCRIPTION_MAX = 64, 1024
SKILL_MAX_FILES, SKILL_MAX_BYTES = 100, 25 * MIB
LINK_MAX_FILES, LINK_MAX_BYTES = 1000, 50 * MIB
LINK_MAX_SKILLS, MAX_DEPTH = 50, 3
# "Kept small" is the rule; 1 MiB is our budget (chatly's own cover upload limit is 10 MiB).
COVER_MAX_BYTES = 1 * MIB
COVER_SIGNATURES = {
    "cover.png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
    "cover.jpg": lambda b: b.startswith(b"\xff\xd8\xff"),
    "cover.webp": lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP",
    "cover.gif": lambda b: b[:6] in (b"GIF87a", b"GIF89a"),
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".heic", ".svg", ".bmp", ".tif", ".tiff"}
JUNK_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "Icon\r"}
JUNK_DIRS = {"__MACOSX", ".Spotlight-V100", ".Trashes", ".fseventsd"}
LICENSE_RE = re.compile(r"^LICEN[CS]E(\.(md|txt))?$", re.I)

failures: list[str] = []
notes: list[str] = []


def fail(path: Path, message: str) -> None:
    failures.append(f"{rel(path)}: {message}")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix() or "."


def chars(text: str) -> int:
    """Length as JavaScript counts it (UTF-16 units), never less than Python's len()."""
    return len(text.encode("utf-16-le")) // 2


def walk(top: Path) -> list[Path]:
    """Every file under top, plus symlinks (not followed); skips the repo's .git."""
    found = []
    for here, dirs, files in os.walk(top):
        base = Path(here)
        found += [base / d for d in dirs if (base / d).is_symlink()]
        dirs[:] = sorted(d for d in dirs if not (base == ROOT and d == ".git"))
        found += [base / f for f in sorted(files)]
    return found


def size(paths: list[Path]) -> int:
    return sum(p.lstat().st_size for p in paths)


def duplicate_keys(node, where=""):
    """Keys repeated in one YAML mapping (YAML forbids it; some parsers reject it)."""
    if isinstance(node, yaml.MappingNode):
        seen = set()
        for key, value in node.value:
            if isinstance(key, yaml.ScalarNode) and key.tag != "tag:yaml.org,2002:merge":
                if key.value in seen:
                    yield where + key.value
                seen.add(key.value)
            yield from duplicate_keys(value, where + str(getattr(key, "value", "?")) + ".")
    elif isinstance(node, yaml.SequenceNode):
        for item in node.value:
            yield from duplicate_keys(item, where)


def check_frontmatter(skill_md: Path) -> str | None:
    """Check the frontmatter; returns the name when it is usable."""
    try:
        text = skill_md.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        fail(skill_md, "is not UTF-8 text")
        return None
    if text.startswith("﻿"):
        fail(skill_md, "starts with a byte-order mark; save it as UTF-8 without BOM")
        return None
    lines = text.split("\n")
    if lines[0].rstrip("\r \t") != "---":
        fail(skill_md, "must start with a '---' line opening the YAML frontmatter")
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip("\r \t") == "---"), None)
    if end is None:
        fail(skill_md, "frontmatter has no closing '---' line")
        return None
    block, body = "\n".join(lines[1:end]), "\n".join(lines[end + 1:])
    try:
        dups = list(duplicate_keys(yaml.compose(block, Loader=yaml.SafeLoader)))
        data = yaml.safe_load(block)
    except yaml.YAMLError as exc:
        fail(skill_md, f"frontmatter is not valid YAML: {' '.join(str(exc).split())}")
        return None
    if dups:
        fail(skill_md, f"frontmatter repeats the key(s) {', '.join(dups)}")
    if not isinstance(data, dict):
        fail(skill_md, "frontmatter is not a YAML mapping")
        return None
    if not body.strip():
        fail(skill_md, "has no instructions after the frontmatter")

    name, description = data.get("name"), data.get("description")
    usable = None
    if not isinstance(name, str):
        fail(skill_md, f"name must be a string, got {type(name).__name__} (quote it)")
    elif not name.strip() or chars(name) > NAME_MAX:
        fail(skill_md, f"name must be 1-{NAME_MAX} characters, is {chars(name)}")
    elif not re.search(r"[A-Za-z0-9]", name):
        fail(skill_md, "name needs at least one English letter or digit")
    else:
        usable = name
    if not isinstance(description, str):
        fail(skill_md, f"description must be a string, got {type(description).__name__}")
    elif not description.strip() or chars(description) > DESCRIPTION_MAX:
        fail(skill_md, f"description must be 1-{DESCRIPTION_MAX} characters, is {chars(description)}")
    return usable


def check_covers(skill: Path) -> None:
    covers = [p for p in sorted(skill.iterdir())
              if p.is_file() and p.stem.lower() == "cover" and p.suffix.lower() in IMAGE_SUFFIXES]
    for cover in covers:
        check = COVER_SIGNATURES.get(cover.name)
        if check is None:
            fail(cover, f"a cover must be named one of {', '.join(COVER_SIGNATURES)} (lowercase)")
            continue
        data = cover.read_bytes()
        ok = True
        if not check(data):
            fail(cover, f"is not a {cover.suffix[1:].upper()} image")
            ok = False
        if len(data) > COVER_MAX_BYTES:
            fail(cover, f"is {len(data) / MIB:.1f} MiB; keep covers under {COVER_MAX_BYTES // MIB} MiB")
            ok = False
        if ok and cover.name != "cover.webp":
            notes.append(f"{rel(cover)}: fine, but webp is preferred")
    if len(covers) > 1:
        fail(skill, f"has {len(covers)} covers; keep one")


def check_skill(skill: Path, names: dict[str, list[str]]) -> tuple[int, int]:
    files = walk(skill)
    total = size(files)
    if len(files) > SKILL_MAX_FILES:
        fail(skill, f"has {len(files)} files; the limit is {SKILL_MAX_FILES}")
    if total > SKILL_MAX_BYTES:
        fail(skill, f"is {total / MIB:.1f} MiB; the limit is {SKILL_MAX_BYTES // MIB} MiB")
    for path in files:
        if path.is_symlink():
            fail(path, "is a symbolic link; skills can't carry links")
        elif path.name in JUNK_NAMES or path.name.startswith("._") or JUNK_DIRS & set(path.parts):
            fail(path, "is OS junk; delete it")
    if not any(LICENSE_RE.match(p.name) for p in skill.iterdir() if p.is_file()):
        fail(skill, "has no LICENSE file")
    name = check_frontmatter(skill / "SKILL.md")
    if name:
        names.setdefault(" ".join(name.split()).casefold(), []).append(rel(skill))
    check_covers(skill)
    return len(files), total


def check_type_folder(folder: Path, names: dict[str, list[str]]) -> tuple[int, int, int]:
    files = walk(folder)
    for path in files:
        if path.name.lower() == "skill.md" and path.name != "SKILL.md":
            fail(path, "must be named SKILL.md exactly, or renamed so it isn't read as a skill")
    skills = sorted({p.parent for p in files if p.name == "SKILL.md" and not p.is_symlink()})
    if folder in skills:
        fail(folder, "has a SKILL.md at its top, which makes the whole type folder one skill")
        skills.remove(folder)
    for skill in skills:
        depth = len(skill.relative_to(folder).parts)
        if depth > MAX_DEPTH:
            fail(skill, f"is {depth} levels below {folder.name}/; the limit is {MAX_DEPTH}")
        outer = [other for other in skills if other in skill.parents]
        if outer:
            fail(skill, f"is a skill inside the skill {rel(outer[-1])}; rename its SKILL.md")
    for sub in sorted(p for p in folder.iterdir() if p.is_dir() and not p.is_symlink()):
        if not any(s == sub or sub in s.parents for s in skills):
            fail(sub, "has no SKILL.md at its top")
    if not skills:
        fail(folder, "has no skills")
    if len(skills) > LINK_MAX_SKILLS:
        fail(folder, f"has {len(skills)} skills; one link takes at most {LINK_MAX_SKILLS}")
    for skill in skills:
        check_skill(skill, names)
    total = size(files)
    if len(files) > LINK_MAX_FILES or total > LINK_MAX_BYTES:
        fail(folder, f"is {len(files)} files and {total / MIB:.1f} MiB; one link takes at most "
                     f"{LINK_MAX_FILES} files and {LINK_MAX_BYTES // MIB} MiB")
    return len(skills), len(files), total


def main() -> int:
    if (ROOT / "SKILL.md").exists():
        fail(ROOT / "SKILL.md", "a SKILL.md at the repo root makes every skill nested")
    for top in sorted(ROOT.iterdir()):
        if top.is_dir() and top.name not in TYPES and top.name != ".git":
            for path in walk(top):
                if path.name.lower() == "skill.md":
                    fail(path, "is outside a type folder, so no import link would give it a type")

    names: dict[str, list[str]] = {}
    rows = []
    for folder in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name in TYPES):
        rows.append((folder.name, *check_type_folder(folder, names)))
    if not rows:
        failures.append("no type folders found")
    for skills in names.values():
        if len(skills) > 1:
            failures.append(f"{', '.join(skills)}: same name; names must be unique")

    print(f"{'folder':<14}{'skills':>7}{'files':>7}{'size':>11}")
    for name, skills, files, total in rows:
        print(f"{name + '/':<14}{skills:>7}{files:>7}{total / 1024:>8.0f} KiB")
    repo_files = walk(ROOT)
    repo_bytes = size(repo_files)
    print(f"{'repo total':<14}{sum(r[1] for r in rows):>7}{len(repo_files):>7}{repo_bytes / 1024:>8.0f} KiB"
          f"   (limits per link: {LINK_MAX_FILES} files, {LINK_MAX_BYTES // MIB} MiB)")
    if len(repo_files) > LINK_MAX_FILES or repo_bytes > LINK_MAX_BYTES:
        notes.append("the whole repo is over the per-link limits, so it can't be imported as one link; "
                     "link the type folders, as the README says")

    for note in notes:
        print(f"note: {note}")
    for problem in failures:
        print(f"FAIL {problem}")
    print(f"\n{'FAILED' if failures else 'PASSED'}: {len(failures)} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
