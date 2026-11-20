"""Prepare the copy of the repository that is published for the evaluators.

    .venv/bin/python -m tradecraft.publish

docs/build-plan.md, section 12. The existing history is never pushed: every
commit carries the operator's private email. This writes a fresh copy of the
committed files, with no history, to data/publish/tradecraft/, leaves out what
must not be published, and runs the checks. Each failed check is a stop.

It does not create a repository, commit or push. The operator does that, under
the hosting service's private no-reply address (the commands are printed).
"""
from __future__ import annotations

import io
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

from . import demo, settings

OUT = "publish/tradecraft"
# Left out of the published copy, and why.
EXCLUDE = {
    "logs/": "the scheduled job's logs: they hold this machine's folder paths and user name",
    "ops/": "the scheduled job's files for this machine (launchd): machine-specific, with the operator's name",
    "ladder_out/": "daily output derived from third-party option quotes",
    "universe.txt.pre-mode1": "a superseded working file",
}
MUST_EXIST = ["README.md", ".env.example", ".gitignore", "pyproject.toml", "uv.lock", "tradecraft/demo.py",
              "docs/recorded-demo.md", "docs/build-plan.md", "docs/site/tradecraft-prototype.html"]
MUST_NOT_EXIST = [".env", "data", "snapshots", "label_out", ".venv"]
def _operator_names() -> list[str]:
    """The operator's names, read from git's own settings so that none is written in this file."""
    who = subprocess.run(["git", "config", "user.name"], cwd=settings.ROOT, capture_output=True, text=True).stdout
    return [w for w in re.split(r"\W+", who + " " + Path.home().name) if len(w) >= 4]


def build(out: Path | None = None) -> dict:
    out = out or settings.data_dir() / OUT
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=settings.ROOT, capture_output=True, text=True).stdout.strip()
    if dirty:
        raise SystemExit("Commit or discard the uncommitted changes first: the copy is made from the last commit.")
    # Refresh the copy in place. Its own .git folder, once the operator has made the copy a repository, is kept,
    # so that a later change can be committed and pushed from the same folder.
    out.mkdir(parents=True, exist_ok=True)
    for old in out.iterdir():
        if old.name == ".git":
            continue
        shutil.rmtree(old) if old.is_dir() and not old.is_symlink() else old.unlink()
    blob = subprocess.run(["git", "archive", "HEAD"], cwd=settings.ROOT, capture_output=True, check=True).stdout
    left_out: dict[str, int] = {k: 0 for k in EXCLUDE}
    with tarfile.open(fileobj=io.BytesIO(blob)) as tar:
        for m in tar.getmembers():
            hit = next((k for k in EXCLUDE if m.name == k.rstrip("/") or m.name.startswith(k) or m.name == k), None)
            if hit:
                left_out[hit] += m.isfile()
                continue
            tar.extract(m, out, filter="data")
    files = [p for p in out.rglob("*") if p.is_file() and ".git" not in p.relative_to(out).parts]
    problems = [f"missing: {x}" for x in MUST_EXIST if not (out / x).exists()]
    problems += [f"must not be published: {x}" for x in MUST_NOT_EXIST if (out / x).exists()]
    problems += demo.scan(out)                                   # secrets, home-folder paths, email addresses
    names = _operator_names()
    NAME = re.compile("|".join(re.escape(n) for n in names), re.IGNORECASE) if names else re.compile(r"(?!x)x")
    # The address of the published repository is public by nature, so the account name inside it is not a leak.
    address = re.compile(r"github\.com/[A-Za-z0-9-]+|[A-Za-z0-9-]+\.github\.io")
    for p in files:
        rel = p.relative_to(out)
        if NAME.search(str(rel)) or NAME.search(address.sub("", p.read_text(errors="replace"))):
            problems.append(f"{rel}: holds the operator's name")
    example = (out / ".env.example").read_text()
    filled = [l for l in example.splitlines() if "=" in l and not l.startswith("#") and l.split("=", 1)[1].strip()]
    if filled:
        problems.append(".env.example has a value filled in")
    size = sum(p.stat().st_size for p in files)
    return {"out": out, "files": len(files), "bytes": size, "left_out": left_out, "problems": sorted(set(problems)),
            "commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=settings.ROOT,
                                     capture_output=True, text=True).stdout.strip()}


NEXT = """
Next, by the operator (nothing below has been done):
  1. Create an empty repository on the hosting service. Find your private no-reply address in its email settings.
  2. cd {out}
     git init -b main
     git -c user.name="<name to show>" -c user.email="<your no-reply address>" add -A
     git -c user.name="<name to show>" -c user.email="<your no-reply address>" commit -m "Tradecraft: capstone submission"
     git log -1 --format='%an <%ae>'        # confirm it shows the no-reply address
     git remote add origin <repository URL> && git push -u origin main
  3. The demo data is a second repository: the same steps inside data/demo-bundle, after
     `python -m tradecraft.demo scan` reports it clean.
  4. Open both links in a browser that is not signed in, then put the links in the README's two placeholders.
"""

if __name__ == "__main__":
    r = build()
    print(f"Copy of commit {r['commit']}: {r['files']} files, {r['bytes'] / 1e6:.1f} MB, in {r['out']}")
    for k, n in r["left_out"].items():
        print(f"  left out: {k} ({n} file{'s' if n != 1 else ''}): {EXCLUDE[k]}")
    if r["problems"]:
        print("\nSTOP. Do not publish this copy:")
        print("\n".join("  " + p for p in r["problems"]))
        sys.exit(1)
    print("\nChecks passed: no secret value, no home-folder path, no email address, no operator name, "
          "no data folder, .env.example empty.")
    print(NEXT.format(out=r["out"]))
