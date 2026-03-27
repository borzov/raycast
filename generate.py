#!/usr/bin/env python3
"""Generate Raycast snippets JSON from asciimoji.com data."""

import json
import urllib.request
from pathlib import Path

ASCIIMOJI_URL = (
    "https://codeberg.org/jiggly/asciimoji/raw/branch/main/"
    "dist/text-file/asciimoji.txt"
)

# Dynamic entries not present in asciimoji.txt — demo values
DYNAMIC_ENTRIES: list[dict[str, str | list[str]]] = [
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
    with urllib.request.urlopen(ASCIIMOJI_URL) as resp:
        return resp.read().decode("utf-8")


def parse_line(line: str) -> dict[str, str | list[str]] | None:
    """Parse a single line: 'keyword1,keyword2 ascii_string'."""
    line = line.strip()
    if not line:
        return None
    first_space = line.index(" ")
    keywords_part = line[:first_space]
    ascii_part = line[first_space + 1:]
    keywords = [kw.strip() for kw in keywords_part.split(",") if kw.strip()]
    return {"keywords": keywords, "ascii": ascii_part}


def to_snippet(entry: dict[str, str | list[str]]) -> dict[str, str]:
    """Convert parsed entry to Raycast snippet format."""
    keywords = entry["keywords"]
    primary = str(keywords[0])
    ascii_str = str(entry["ascii"])

    name = f"{primary.capitalize()} {ascii_str}"
    if len(keywords) > 1:
        aliases = ", ".join(str(kw) for kw in keywords[1:])
        name += f" (also: {aliases})"

    return {
        "name": name,
        "text": ascii_str,
        "keyword": f"!{primary}",
    }


def main() -> None:
    raw = download_asciimoji()
    entries: list[dict[str, str | list[str]]] = []

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
