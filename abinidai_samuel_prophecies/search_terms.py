import json
from pathlib import Path

data = json.load(open(Path(__file__).parent.parent / "data" / "book-of-mormon.json", encoding="utf-8"))
terms = ["sorcer", "witchcraft", "magic", "power of the evil"]

lines = []
for b in data["books"]:
    for c in b["chapters"]:
        for v in c["verses"]:
            text_lower = v["text"].lower()
            matched = [t for t in terms if t in text_lower]
            if matched:
                lines.append(f"\n{v['reference']} [matched: {', '.join(matched)}]")
                lines.append(v["text"])

out = Path(__file__).parent / "search_results.txt"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"Found {len([l for l in lines if l.startswith(chr(10))])} verses, written to {out}")
