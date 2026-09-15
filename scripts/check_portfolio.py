"""Check public catalog completeness, method links and maintained local paths."""

import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

root = Path(__file__).resolve().parents[1]
snapshot = json.loads((root / "catalog/public-repositories.json").read_text())
catalog = json.loads((root / "catalog/projects.json").read_text())
expected = {r["name"] for r in snapshot["repositories"] if not r["isFork"]}
assert {r["repository"] for r in catalog} == expected
assert len({r["repository"] for r in catalog}) == len(catalog)
assert all(r["priority"] in {"P0", "P1", "P2"} for r in catalog)
assert all(re.fullmatch(r"[0-9a-f]{40}", r["verified_commit"]) for r in catalog)
cases = (root / "scenarios/README.md").read_text()
ids = set(re.findall(r"^## ([A-Z][0-9]{2}) ", cases, re.M))
assert len(ids) == 12
assert all(set(r["scenario_ids"]) <= ids for r in catalog)
for section in re.split(r"^## [A-Z][0-9]{2} ", cases, flags=re.M)[1:]:
    assert all(label in section for label in ("输入与方法", "执行", "反例与行动", "面试", "来源"))
    assert "https://" in section
links = []
for page in root.rglob("*.md"):
    if any(p in {".git", ".venv", "outputs", "build", "dist"} for p in page.relative_to(root).parts):
        continue
    content = re.sub(r"```.*?```", "", page.read_text(), flags=re.S)
    for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", content):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        destination = page.parent / unquote(parsed.path)
        assert destination.exists(), (str(page.relative_to(root)), target)
        links.append(target)
print(json.dumps({"catalog_projects": len(catalog), "reference_forks": sum(r["isFork"] for r in snapshot["repositories"]), "core_scenarios": len(ids), "local_paths_checked": len(links), "meaning": "structural consistency; not financial-method or human-usability approval"}))
