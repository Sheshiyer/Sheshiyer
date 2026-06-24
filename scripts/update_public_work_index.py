#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import unicodedata
from collections import Counter
from pathlib import Path


USER = "Sheshiyer"
ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ATLAS = ROOT / "assets" / "atlas.svg"


FIELDS = [
    {
        "name": "Venture operations",
        "short": "VENTURE OPS",
        "keywords": ["cambium", "brand", "mint", "meristem", "team", "forge", "snow", "gloves", "operator"],
        "pattern": "Taste, planning, execution, and review stay in the same loop.",
        "signal": "taste + execution",
    },
    {
        "name": "Reflection runtimes",
        "short": "REFLECTION",
        "keywords": ["selemene", "witness", "noesis", "tryambakam", "samsclawra", "consciousness", "symbolic"],
        "pattern": "Symbolic work is kept runnable, inspectable, and grounded in code.",
        "signal": "symbolic systems",
    },
    {
        "name": "Spatial systems",
        "short": "SPATIAL",
        "keywords": ["spatial", "panorama", "panaroma", "marina", "viewer", "vantyx", "property", "parkarea", "reality"],
        "pattern": "Place is treated as interface: mapped, navigable, and operational.",
        "signal": "place as UI",
    },
    {
        "name": "Trust surfaces",
        "short": "TRUST",
        "keywords": ["fitcheck", "klear", "karma", "tirak", "tryon", "commerce", "consent", "marketplace", "verify"],
        "pattern": "Trust surfaces carry consent, verification, and cultural context.",
        "signal": "verification",
    },
    {
        "name": "Narrative archives",
        "short": "NARRATIVE",
        "keywords": ["somatic", "canticle", "synchronocities", "wtf", "media", "rabbit", "vault", "wiki", "blog", "tpothp"],
        "pattern": "Archives hold story, research, media, and ritual without flattening them.",
        "signal": "memory systems",
    },
    {
        "name": "Toolmaking",
        "short": "TOOLS",
        "keywords": ["skill", "raycast", "mcp", "orchestrator", "headshot", "extension", "cli", "homebrew", "template"],
        "pattern": "Expert workflows become portable without shaving off the practice.",
        "signal": "portable craft",
    },
]

PUBLIC_ANCHOR_EXCLUDES = {"sheshiyer", "motionsites-skills"}


def shell_json(command: list[str]) -> object:
    output = subprocess.check_output(command, cwd=ROOT, text=True)
    return json.loads(output)


def fetch_public_repos() -> list[dict[str, object]]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token and shutil.which("gh"):
        data = shell_json(
            [
                "gh",
                "repo",
                "list",
                USER,
                "--limit",
                "300",
                "--json",
                "name,description,isPrivate,isFork,primaryLanguage,url,updatedAt",
            ]
        )
        return [
            {
                "name": repo["name"],
                "description": repo.get("description") or "",
                "url": repo["url"],
                "language": (repo.get("primaryLanguage") or {}).get("name") or "Unspecified",
                "updated_at": repo.get("updatedAt") or "",
                "is_fork": bool(repo.get("isFork")),
                "is_private": bool(repo.get("isPrivate")),
            }
            for repo in data
            if not repo.get("isFork") and not repo.get("isPrivate")
        ]

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repos: list[dict[str, object]] = []
    page = 1
    while True:
        request = urllib.request.Request(
            f"https://api.github.com/users/{USER}/repos?type=owner&sort=updated&per_page=100&page={page}",
            headers=headers,
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            batch = json.loads(response.read().decode("utf-8"))
        if not batch:
            break
        for repo in batch:
            if repo.get("fork"):
                continue
            language = repo.get("language") or "Unspecified"
            repos.append(
                {
                    "name": repo["name"],
                    "description": repo.get("description") or "",
                    "url": repo["html_url"],
                    "language": language,
                    "updated_at": repo.get("updated_at") or "",
                    "is_fork": False,
                    "is_private": False,
                }
            )
        page += 1
    return repos


def classify(repo: dict[str, object]) -> str:
    haystack = f"{repo['name']} {repo.get('description', '')}".lower()
    best_name = "Toolmaking"
    best_score = 0
    for field in FIELDS:
        score = sum(len(keyword) for keyword in field["keywords"] if keyword in haystack)
        if score > best_score:
            best_name = field["name"]
            best_score = score
    return best_name


def repo_link(repo: dict[str, object]) -> str:
    return f"[`{repo['name']}`]({repo['url']})"


def ascii_text(value: object) -> str:
    text = str(value)
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00b7": "/",
        "\u2026": "...",
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def compact_description(repo: dict[str, object]) -> str:
    description = ascii_text(repo.get("description") or "").strip()
    if not description:
        return "Public work surface."
    description = re.sub(r"\s+", " ", description)
    if len(description) <= 108:
        return description
    clipped = description[:105].rstrip()
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    return clipped.rstrip(" .,") + "..."


def generate_markdown(repos: list[dict[str, object]]) -> str:
    by_field: dict[str, list[dict[str, object]]] = {field["name"]: [] for field in FIELDS}
    profile_name = USER.lower()
    for repo in repos:
        by_field[classify(repo)].append(repo)
    for bucket in by_field.values():
        bucket.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)

    lines: list[str] = []
    lines.append("## Public work index")
    lines.append("")
    lines.append("| Field | Public repos | Recent anchors | Pattern |")
    lines.append("| --- | ---: | --- | --- |")
    for field in FIELDS:
        bucket = by_field[field["name"]]
        anchor_pool = [repo for repo in bucket if str(repo["name"]).lower() not in PUBLIC_ANCHOR_EXCLUDES]
        anchors = ", ".join(repo_link(repo) for repo in anchor_pool[:4]) or "N/A"
        lines.append(f"| {field['name']} | {len(bucket)} | {anchors} | {field['pattern']} |")

    recent = [
        repo
        for repo in sorted(repos, key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        if str(repo["name"]).lower() not in PUBLIC_ANCHOR_EXCLUDES
    ][:8]
    lines.append("")
    lines.append("## Recent public movement")
    lines.append("")
    lines.append("| Repository | Field | Language | Focus |")
    lines.append("| --- | --- | --- | --- |")
    for repo in recent:
        lines.append(
            f"| {repo_link(repo)} | {classify(repo)} | {repo['language']} | {compact_description(repo)} |"
        )

    languages = Counter(str(repo["language"]) for repo in repos)
    lines.append("")
    lines.append("<details>")
    lines.append("<summary><b>Public language profile</b></summary>")
    lines.append("<br />")
    lines.append("")
    lines.append("| Language | Public non-fork repositories |")
    lines.append("| --- | ---: |")
    for language, count in languages.most_common(12):
        lines.append(f"| {language} | {count} |")
    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


def replace_generated_block(markdown: str, count: int) -> None:
    text = README.read_text()
    start = "<!-- public-work-index:start -->"
    end = "<!-- public-work-index:end -->"
    block = f"{start}\n{markdown}\n{end}"
    if start in text and end in text:
        text = re.sub(f"{re.escape(start)}.*?{re.escape(end)}", block, text, flags=re.S)
    else:
        text = text.replace("## Public work index", f"{start}\n## Public work index", 1)
        marker = "\n\n<img src=\"assets/divider.svg\""
        text = text.replace(marker, f"\n{end}{marker}", 1)
        text = re.sub(f"{re.escape(start)}.*?{re.escape(end)}", block, text, flags=re.S)

    text = re.sub(r"Public work spans \*\*\d+ non-fork repositories\*\*", f"Public work spans **{count} non-fork repositories**", text)
    README.write_text(text)


def svg_text(value: object) -> str:
    return html.escape(str(value), quote=True)


def generate_svg(repos: list[dict[str, object]]) -> str:
    by_field = {field["name"]: 0 for field in FIELDS}
    for repo in repos:
        by_field[classify(repo)] += 1
    max_count = max(by_field.values()) or 1

    rows: list[str] = []
    y = 240
    for field in FIELDS:
        count = by_field[field["name"]]
        ink_width = round(120 + (count / max_count) * 260)
        gold_width = 58 + (len(field["signal"]) % 4) * 14
        rows.append(
            f'''
    <g transform="translate(0 {y})">
      <text class="mono" x="72" y="0" fill="#E1E0CC" font-size="13">{svg_text(field["short"])}</text>
      <text class="body" x="72" y="28" fill="#A9A797" font-size="15">{svg_text(field["pattern"])}</text>
      <rect x="640" y="-16" width="{ink_width}" height="12" rx="6" fill="#E1E0CC" fill-opacity="0.44"/>
      <rect x="{656 + ink_width}" y="-16" width="{gold_width}" height="12" rx="6" fill="#DEDBC8" fill-opacity="0.82"/>
      <text class="mono" x="620" y="-5" fill="#DEDBC8" font-size="12" text-anchor="end">{count} repos</text>
    </g>'''
        )
        y += 82

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 760" width="1200" height="760">
  <defs>
    <linearGradient id="field" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0C0C0B"/>
      <stop offset="58%" stop-color="#141412"/>
      <stop offset="100%" stop-color="#23211D"/>
    </linearGradient>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.86" numOctaves="3" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
      <feComponentTransfer>
        <feFuncA type="table" tableValues="0 0.12"/>
      </feComponentTransfer>
    </filter>
    <style>
      .title {{ font-family: "Geist", "Satoshi", "Avenir Next", sans-serif; font-weight: 700; letter-spacing: -0.8px; }}
      .mono {{ font-family: "Geist Mono", "SFMono-Regular", Consolas, monospace; font-weight: 600; letter-spacing: 1px; }}
      .body {{ font-family: "Geist", "Satoshi", "Avenir Next", sans-serif; font-weight: 400; }}
    </style>
  </defs>

  <rect width="1200" height="760" rx="30" fill="url(#field)"/>
  <rect width="1200" height="760" rx="30" filter="url(#grain)" opacity="0.42"/>
  <rect x="28" y="28" width="1144" height="704" rx="22" fill="none" stroke="#E1E0CC" stroke-opacity="0.12"/>

  <text class="mono" x="72" y="78" fill="#DEDBC8" font-size="13">PUBLIC WORK INDEX / SIX OPERATING FIELDS</text>
  <text class="title" x="72" y="124" fill="#E1E0CC" font-size="42">{len(repos)} public repositories across six operating fields.</text>
  <text class="body" x="72" y="158" fill="#A9A797" font-size="18">A living map of rooms, tools, runtimes, archives, and trust surfaces.</text>
  <rect x="72" y="198" width="1056" height="1" fill="#E1E0CC" fill-opacity="0.16"/>
{''.join(rows)}
</svg>
'''


def main() -> int:
    repos = fetch_public_repos()
    if not repos:
        print("No public repositories found", file=sys.stderr)
        return 1
    repos.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
    replace_generated_block(generate_markdown(repos), len(repos))
    ATLAS.write_text(generate_svg(repos))
    print(f"Updated README and atlas from {len(repos)} public repositories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
