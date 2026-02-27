"""Extract key narrative chapters for careful reading."""
import json
from pathlib import Path

data = json.load(open(Path(__file__).parent.parent / "data" / "book-of-mormon.json", encoding="utf-8"))

# Chapters to extract for fulfillment analysis
SECTIONS = {
    "Mosiah 19": ("Mosiah", 19),   # Noah's death
    "Mosiah 20": ("Mosiah", 20),   # Limhi's people — Abinadi referenced
    "Mosiah 21": ("Mosiah", 21),   # Bondage, slow to hear
    "Mosiah 22": ("Mosiah", 22),   # Escape from bondage
    "Mosiah 23": ("Mosiah", 23),   # Alma's people
    "Mosiah 24": ("Mosiah", 24),   # Burdens on backs, deliverance
    "Alma 14": ("Alma", 14),       # Believers burned by fire
    "Alma 25": ("Alma", 25),       # Abinadi's prophecy explicitly fulfilled
    "Helaman 11": ("Helaman", 11), # Famine
    "3 Nephi 1": ("3 Nephi", 1),   # Signs of birth
    "3 Nephi 8": ("3 Nephi", 8),   # Destruction at death
    "3 Nephi 9": ("3 Nephi", 9),   # Christ's voice — cities destroyed
    "3 Nephi 10": ("3 Nephi", 10), # Aftermath
    "3 Nephi 23": ("3 Nephi", 23), # Christ references Samuel
    "4 Nephi 1": ("4 Nephi", 1),   # Decline over 400 years
    "Mormon 1": ("Mormon", 1),     # The key chapter
    "Mormon 2": ("Mormon", 2),     # Samuel referenced again
    "Mormon 3": ("Mormon", 3),     # Mormon's despair
    "Mormon 4": ("Mormon", 4),     # Escalating destruction
    "Mormon 5": ("Mormon", 5),     # Near the end
    "Mormon 6": ("Mormon", 6),     # Cumorah
    "Moroni 9": ("Moroni", 9),     # Mormon's letter — final state
}

lines = []
for label, (book_name, ch_num) in SECTIONS.items():
    for b in data["books"]:
        if b["book"] == book_name:
            for c in b["chapters"]:
                if c["chapter"] == ch_num:
                    lines.append(f"\n{'='*60}")
                    lines.append(f"# {label}")
                    lines.append(f"{'='*60}\n")
                    for v in c["verses"]:
                        lines.append(f"**{v['reference']}**: {v['text']}\n")

out = Path(__file__).parent / "key_chapters.md"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"Extracted {len(SECTIONS)} chapters to {out}")
