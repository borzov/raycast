#!/usr/bin/env python3
"""Generate Raycast snippets JSON from asciimoji.com data."""

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import TypedDict

ASCIIMOJI_URL = (
    "https://codeberg.org/jiggly/asciimoji/raw/branch/main/"
    "dist/text-file/asciimoji.txt"
)

class Entry(TypedDict):
    """A parsed asciimoji entry."""

    keywords: list[str]
    ascii: str


# Dynamic entries not present in asciimoji.txt — demo values
DYNAMIC_ENTRIES: list[Entry] = [
    {
        "keywords": ["dollarbill"],
        "ascii": "[̲̅$̲̅(̲̅ ͡° ͜ʖ ͡°̲̅)̲̅$̲̅]",
    },
    {
        "keywords": ["fancytext"],
        "ascii": "ɦɛʟʟօ ֆǟʏ ɦɛʟʟօ",
    },
    {
        "keywords": ["fliptext"],
        "ascii": "ʇxǝʇdılɟ",
    },
    {
        "keywords": ["fliptexttable"],
        "ascii": "(ノ ͡° ͜ʖ ͡°ノ)︵ ʇxǝʇdılɟ",
    },
    {
        "keywords": ["loading"],
        "ascii": "█▒▒▒▒▒▒▒▒▒",
    },
    {
        "keywords": ["rolldice"],
        "ascii": "⚃",
    },
    {
        "keywords": ["witchtext"],
        "ascii": "H̶̡̬̯̙͎̝̣̖͔̰̫̮͉̥̍̍̉͐̇̕e̵̳̣͕̤͕̟̞̝̪̺̩͐̃̑̔̈́l̵̤̞̞̂̀l̵̛̹̺̣̗̗̠̣̫̼̈́̐̈́̅̈̋̌̚o̴̡̨̝̗͓̗̤̩͛̔̓̈́̾̓̀̏̕",
    },
]


def download_asciimoji() -> str:
    """Download asciimoji.txt from Codeberg."""
    try:
        with urllib.request.urlopen(ASCIIMOJI_URL, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"HTTP error fetching asciimoji: {exc.code} {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error fetching asciimoji: {exc.reason}") from exc
    except UnicodeDecodeError as exc:
        raise SystemExit(f"Failed to decode asciimoji response as UTF-8: {exc}") from exc


def parse_line(line: str) -> Entry | None:
    """Parse a single line: 'keyword1,keyword2 ascii_string'."""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    keywords_part, sep, ascii_part = line.partition(" ")
    if not sep:
        return None
    keywords = [kw.strip() for kw in keywords_part.split(",") if kw.strip()]
    return {"keywords": keywords, "ascii": ascii_part}


def to_snippet(entry: Entry) -> dict[str, str]:
    """Convert parsed entry to Raycast snippet format."""
    keywords = entry["keywords"]
    primary = keywords[0]
    ascii_str = entry["ascii"]

    name = f"{primary.capitalize()} {ascii_str}"
    if len(keywords) > 1:
        aliases = ", ".join(keywords[1:])
        name += f" (also: {aliases})"

    return {
        "name": name,
        "text": ascii_str,
        "keyword": f"!{primary}",
    }


def main() -> None:
    raw = download_asciimoji()
    entries: list[Entry] = []

    for line in raw.splitlines():
        parsed = parse_line(line)
        if parsed is not None:
            entries.append(parsed)

    entries.extend(DYNAMIC_ENTRIES)

    snippets = [to_snippet(e) for e in entries]
    snippets.sort(key=lambda s: s["keyword"])

    output = Path(__file__).parent / "asciimoji.json"
    output.write_text(
        json.dumps(snippets, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(snippets)} snippets -> {output}")


if __name__ == "__main__":
    main()
