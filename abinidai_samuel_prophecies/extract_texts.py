"""
Extract the words of Abinadi, Samuel the Lamanite, and Mormon 1
from book-of-mormon.json into a clean markdown file.
"""

import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
JSON_PATH = SCRIPT_DIR.parent / "data" / "book-of-mormon.json"
OUTPUT_PATH = SCRIPT_DIR / "source_texts.md"

# Chapters to extract:
#   Abinadi: Mosiah 11-17  (his confrontation with King Noah, trial, and teachings)
#   Samuel:  Helaman 13-16 (his prophecies from the wall of Zarahemla)
#   Target:  Mormon 1      (the chapter Mormon references their prophecies)
SECTIONS = [
    {"book": "Mosiah",  "chapters": range(11, 18), "label": "Abinadi's Words (Mosiah 11–17)"},
    {"book": "Helaman", "chapters": range(13, 17), "label": "Samuel the Lamanite's Words (Helaman 13–16)"},
    {"book": "Mormon",  "chapters": range(1, 2),   "label": "Mormon Chapter 1"},
]


def load_json():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_chapters(data, book_name, chapter_range):
    """Return list of (reference, verse_num, text) for matching chapters."""
    verses = []
    for book in data["books"]:
        if book["book"] == book_name:
            for chapter in book["chapters"]:
                if chapter["chapter"] in chapter_range:
                    for v in chapter["verses"]:
                        verses.append((v["reference"], v["verse"], v["text"]))
    return verses


def write_markdown(sections_data):
    lines = [
        "# Source Texts for Prophecy Fulfillment Analysis",
        "",
        "> Auto-extracted from `book-of-mormon.json`",
        "",
        "---",
        "",
    ]
    for label, verses in sections_data:
        lines.append(f"## {label}")
        lines.append("")
        for ref, verse_num, text in verses:
            lines.append(f"**{ref}** — {text}")
            lines.append("")
        lines.append("---")
        lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written {len(lines)} lines to {OUTPUT_PATH}")


def main():
    data = load_json()
    sections_data = []
    for section in SECTIONS:
        verses = extract_chapters(data, section["book"], section["chapters"])
        sections_data.append((section["label"], verses))
        print(f"  {section['label']}: {len(verses)} verses extracted")
    write_markdown(sections_data)


if __name__ == "__main__":
    main()
