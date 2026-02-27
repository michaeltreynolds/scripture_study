import csv
import os

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "study_results.md")

CATEGORIES = {
    "affirms": {
        "title": "What It Affirms",
        "emoji": "✅",
        "description": "Significant general truths affirmed by the Book of Mormon.",
    },
    "refutes": {
        "title": "What It Refutes",
        "emoji": "🚫",
        "description": "False beliefs of people today that the Book of Mormon contradicts.",
    },
    "fulfills": {
        "title": "What It Fulfills",
        "emoji": "📜",
        "description": "Old Testament prophecies fulfilled by the Book of Mormon.",
    },
    "clarifies": {
        "title": "What It Clarifies",
        "emoji": "💡",
        "description": "Teachings of Jesus made clearer than in the Old and New Testaments.",
    },
    "reveals": {
        "title": "What It Reveals",
        "emoji": "🌟",
        "description": "Valuable knowledge we would not have known without the Book of Mormon.",
    },
}


def read_csv(category_key):
    path = os.path.join(OUTPUT_DIR, f"{category_key}.csv")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ref = row["Reference"].strip()
            insight = row["Insight"].strip()
            if ref and insight:
                rows.append((ref, insight))
    return rows


def main():
    lines = []
    lines.append("# 📖 Book of Mormon Study — Five Lenses\n")
    lines.append("A chapter-by-chapter study of the Book of Mormon through five lenses:\n")
    lines.append("what it **affirms**, **refutes**, **fulfills**, **clarifies**, and **reveals**.\n")
    lines.append("---\n")

    for cat_key, cat_info in CATEGORIES.items():
        rows = read_csv(cat_key)
        lines.append(f"## {cat_info['emoji']} {cat_info['title']}\n")
        lines.append(f"*{cat_info['description']}*\n")
        lines.append(f"**{len(rows)} insights found.**\n")

        if not rows:
            lines.append("*(No results for this category.)*\n")
            lines.append("---\n")
            continue

        # Group by book for readability
        current_book = None
        for ref, insight in rows:
            # Extract book name (everything except last number)
            book = " ".join(ref.split()[:-1]) if ref.split()[-1].isdigit() else ref
            if book != current_book:
                current_book = book
                lines.append(f"\n### {book}\n")

            lines.append(f"> **{ref}** — {insight}\n")

        lines.append("\n---\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Generated {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
