"""
V3 Comprehensive Prophecy Fulfillment Search

For each prophecy in V2, searches the Book of Mormon JSON for fulfillment
candidates in all verses AFTER the prophecy is given. Uses keyword matching
with term weighting. Outputs structured JSON for further analysis.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
JSON_PATH = SCRIPT_DIR.parent / "data" / "book-of-mormon.json"
OUTPUT_PATH = SCRIPT_DIR / "v3_search_results.json"
OUTPUT_MD_PATH = SCRIPT_DIR / "v3_search_results.md"

# Book order for determining "after"
BOOK_ORDER = [
    "1 Nephi", "2 Nephi", "Jacob", "Enos", "Jarom", "Omni",
    "Words of Mormon", "Mosiah", "Alma", "Helaman",
    "3 Nephi", "4 Nephi", "Mormon", "Ether", "Moroni"
]

def book_index(book_name):
    return BOOK_ORDER.index(book_name)

# ──────────────────────────────────────────────────────────
# PROPHECY DEFINITIONS
# Each prophecy has:
#   id, ref (book, chapter), keywords (weighted terms),
#   exclude_terms (to reduce noise), description
# ──────────────────────────────────────────────────────────

PROPHECIES = [
    # === ABINADI (Mosiah 11-17) — search from Mosiah 12 onward ===
    {
        "id": "A1", "book": "Mosiah", "chapter": 11,
        "keywords": ["abomination", "wickedness", "whoredom", "anger", "visit"],
        "description": "Wo upon this people — abominations, wickedness, whoredoms; God will visit in anger"
    },
    {
        "id": "A2", "book": "Mosiah", "chapter": 11,
        "keywords": ["deliver", "hands of", "enemies", "bondage", "afflict"],
        "description": "Delivered into enemy hands / bondage / afflicted by enemies"
    },
    {
        "id": "A3", "book": "Mosiah", "chapter": 11,
        "keywords": ["know that I am the Lord", "jealous God", "visiting the iniquities"],
        "description": "They shall know that I am the Lord — jealous God"
    },
    {
        "id": "A4", "book": "Mosiah", "chapter": 11,
        "keywords": ["bondage", "none shall deliver", "Almighty God"],
        "description": "Bondage with no deliverer except the Lord"
    },
    {
        "id": "A5", "book": "Mosiah", "chapter": 11,
        "keywords": ["slow to hear", "cry", "cries", "smitten", "enemies"],
        "description": "God slow to hear their cries; smitten by enemies"
    },
    {
        "id": "A6", "book": "Mosiah", "chapter": 11,
        "keywords": ["sackcloth", "ashes", "cry mightily", "not hear", "affliction"],
        "description": "Must repent in sackcloth and ashes or God will not hear"
    },
    {
        "id": "A7", "book": "Mosiah", "chapter": 12,
        "keywords": ["fierce anger", "iniquities", "abominations", "visit"],
        "description": "Visited in fierce anger for iniquities and abominations"
    },
    {
        "id": "A8", "book": "Mosiah", "chapter": 12,
        "keywords": ["bondage", "smitten", "cheek", "driven", "slain", "vulture", "devour", "flesh"],
        "description": "Bondage, smitten on cheek, driven, slain, flesh devoured"
    },
    {
        "id": "A9", "book": "Mosiah", "chapter": 12,
        "keywords": ["Noah", "garment", "furnace", "fire"],
        "description": "King Noah's life valued as a garment in a hot furnace"
    },
    {
        "id": "A10", "book": "Mosiah", "chapter": 12,
        "keywords": ["famine", "pestilence", "howl"],
        "description": "Famine and pestilence; howl all day long"
    },
    {
        "id": "A11", "book": "Mosiah", "chapter": 12,
        "keywords": ["burden", "backs", "driven", "dumb ass"],
        "description": "Burdens lashed upon backs; driven like a dumb ass"
    },
    {
        "id": "A12", "book": "Mosiah", "chapter": 12,
        "keywords": ["hail", "east wind", "insect", "devour", "grain"],
        "description": "Hail, east wind, insects devouring grain"
    },
    {
        "id": "A13", "book": "Mosiah", "chapter": 12,
        "keywords": ["pestilence", "great pestilence"],
        "description": "Great pestilence because of iniquities"
    },
    {
        "id": "A14", "book": "Mosiah", "chapter": 12,
        "keywords": ["utterly destroy", "face of the earth", "record", "preserve", "other nations"],
        "description": "Utter destruction but a record preserved for other nations"
    },
    {
        "id": "A15", "book": "Mosiah", "chapter": 13,
        "keywords": ["type", "shadow", "things to come"],
        "description": "Abinadi's fate as a type and shadow of things to come"
    },
    {
        "id": "A16", "book": "Mosiah", "chapter": 16,
        "keywords": ["wicked", "cast out", "howl", "weep", "wail", "gnash"],
        "description": "Wicked cast out — howling, weeping, gnashing of teeth"
    },
    {
        "id": "A17", "book": "Mosiah", "chapter": 16,
        "keywords": ["devil", "power over", "carnal", "devilish", "subjecting"],
        "description": "The devil has power over the carnal and devilish"
    },
    {
        "id": "A18", "book": "Mosiah", "chapter": 16,
        "keywords": ["devil", "all power", "fallen state", "rebellion", "enemy to God"],
        "description": "The devil has ALL power over the unrepentant rebel"
    },
    {
        "id": "A19", "book": "Mosiah", "chapter": 16,
        "keywords": ["light", "life of the world", "endless", "never be darkened"],
        "description": "Christ is the light and life — endless, never darkened"
    },
    {
        "id": "A20", "book": "Mosiah", "chapter": 17,
        "keywords": ["death by fire", "fire", "seed", "believe", "salvation"],
        "description": "Noah's seed shall cause believers to suffer death by fire"
    },
    {
        "id": "A21", "book": "Mosiah", "chapter": 17,
        "keywords": ["disease", "all manner of diseases", "iniquities"],
        "description": "Afflicted with all manner of diseases"
    },
    {
        "id": "A22", "book": "Mosiah", "chapter": 17,
        "keywords": ["smitten", "driven", "scattered", "wild flock", "ferocious", "beast"],
        "description": "Smitten, driven, scattered as a wild flock by ferocious beasts"
    },
    {
        "id": "A23", "book": "Mosiah", "chapter": 17,
        "keywords": ["hunted", "taken", "enemies", "death by fire", "fire"],
        "description": "Hunted, taken by enemies, suffer death by fire"
    },
    {
        "id": "A24", "book": "Mosiah", "chapter": 17,
        "keywords": ["vengeance", "destroy his people"],
        "description": "God executes vengeance on those who destroy his people"
    },

    # === SAMUEL THE LAMANITE (Helaman 13-16) — search from Helaman 14 onward ===
    {
        "id": "S1", "book": "Helaman", "chapter": 13,
        "keywords": ["sword of justice", "four hundred years", "400"],
        "description": "Sword of justice within 400 years"
    },
    {
        "id": "S2", "book": "Helaman", "chapter": 13,
        "keywords": ["heavy destruction", "repentance", "faith", "Jesus Christ"],
        "description": "Heavy destruction unless they repent and have faith in Christ"
    },
    {
        "id": "S3", "book": "Helaman", "chapter": 13,
        "keywords": ["take away", "word", "withdraw", "Spirit", "brethren against"],
        "description": "Word taken away, Spirit withdrawn, brethren turned against them"
    },
    {
        "id": "S4", "book": "Helaman", "chapter": 13,
        "keywords": ["sword", "famine", "pestilence", "four hundred"],
        "description": "Sword, famine, pestilence within 400 years"
    },
    {
        "id": "S5", "book": "Helaman", "chapter": 13,
        "keywords": ["fourth generation", "utter destruction", "enemies"],
        "description": "Fourth generation of enemies to witness utter destruction"
    },
    {
        "id": "S6", "book": "Helaman", "chapter": 13,
        "keywords": ["righteous", "saved", "spared", "fire", "heaven", "destroy"],
        "description": "Zarahemla spared only for the righteous' sake"
    },
    {
        "id": "S7", "book": "Helaman", "chapter": 13,
        "keywords": ["cast out", "righteous", "ripe for destruction"],
        "description": "Casting out the righteous = ripe for destruction"
    },
    {
        "id": "S8", "book": "Helaman", "chapter": 13,
        "keywords": ["curse", "land", "wickedness", "abomination"],
        "description": "Curse upon the land because of wickedness"
    },
    {
        "id": "S9", "book": "Helaman", "chapter": 13,
        "keywords": ["treasure", "hide", "earth", "find", "no more", "curse"],
        "description": "Treasures hidden in earth found no more because of curse"
    },
    {
        "id": "S10", "book": "Helaman", "chapter": 13,
        "keywords": ["treasure", "hide", "Lord", "righteous", "cursed"],
        "description": "Only righteous can hide treasures unto the Lord"
    },
    {
        "id": "S11", "book": "Helaman", "chapter": 13,
        "keywords": ["treasure", "hide", "riches", "flee", "enemies", "smitten"],
        "description": "Smitten when hiding treasures while fleeing enemies"
    },
    {
        "id": "S12", "book": "Helaman", "chapter": 13,
        "keywords": ["cursed", "riches", "hearts upon"],
        "description": "Cursed because of riches — hearts set upon them"
    },
    {
        "id": "S13", "book": "Helaman", "chapter": 13,
        "keywords": ["curse", "land", "riches", "iniquities"],
        "description": "Curse upon land and riches because of iniquities"
    },
    {
        "id": "S14", "book": "Helaman", "chapter": 13,
        "keywords": ["cast out", "prophet", "mock", "stone", "slay", "false prophet"],
        "description": "They reject true prophets, call them false"
    },
    {
        "id": "S15", "book": "Helaman", "chapter": 13,
        "keywords": ["flattering", "prophet", "pride", "all is well"],
        "description": "They embrace flattering false prophets"
    },
    {
        "id": "S16", "book": "Helaman", "chapter": 13,
        "keywords": ["anger", "kindled", "cursed", "land", "iniquity"],
        "description": "Anger of the Lord kindled; land cursed"
    },
    {
        "id": "S17", "book": "Helaman", "chapter": 13,
        "keywords": ["slippery", "riches", "cannot hold", "poverty"],
        "description": "Riches become slippery, cannot be held"
    },
    {
        "id": "S18", "book": "Helaman", "chapter": 13,
        "keywords": ["cry", "Lord", "vain", "desolation", "destruction"],
        "description": "Crying unto Lord in vain; desolation come, destruction sure"
    },
    {
        "id": "S19", "book": "Helaman", "chapter": 13,
        "keywords": ["repented", "killed", "prophets", "riches", "gone"],
        "description": "Lamenting: O that I had repented; riches are gone"
    },
    {
        "id": "S20", "book": "Helaman", "chapter": 13,
        "keywords": ["tool", "gone", "sword", "taken", "battle"],
        "description": "Tools and swords disappear"
    },
    {
        "id": "S21", "book": "Helaman", "chapter": 13,
        "keywords": ["treasure", "hid", "slipped away", "curse"],
        "description": "Hidden treasures slip away because of curse"
    },
    {
        "id": "S22", "book": "Helaman", "chapter": 13,
        "keywords": ["slippery", "cannot hold", "cursed", "land"],
        "description": "All things become slippery; cannot hold them"
    },
    {
        "id": "S23", "book": "Helaman", "chapter": 13,
        "keywords": ["demon", "surrounded", "encircled", "angels", "destroy", "souls"],
        "description": "Surrounded by demons, encircled by angels of the devil"
    },
    {
        "id": "S24", "book": "Helaman", "chapter": 13,
        "keywords": ["probation", "past", "procrastinated", "salvation", "too late", "happiness", "iniquity"],
        "description": "Days of probation past; sought happiness in iniquity"
    },
    {
        "id": "S25", "book": "Helaman", "chapter": 14,
        "keywords": ["five years", "Son of God", "redeem", "believe"],
        "description": "Five years until Christ comes"
    },
    {
        "id": "S26", "book": "Helaman", "chapter": 14,
        "keywords": ["no darkness", "night", "day", "as if it were one day", "born"],
        "description": "Night with no darkness — day, night, day as one day"
    },
    {
        "id": "S27", "book": "Helaman", "chapter": 14,
        "keywords": ["new star", "star arise"],
        "description": "A new star shall arise"
    },
    {
        "id": "S28", "book": "Helaman", "chapter": 14,
        "keywords": ["signs", "wonders", "heaven"],
        "description": "Many signs and wonders in heaven"
    },
    {
        "id": "S29", "book": "Helaman", "chapter": 14,
        "keywords": ["sun", "darkened", "moon", "stars", "no light", "three days"],
        "description": "Sun darkened for three days at Christ's death"
    },
    {
        "id": "S30", "book": "Helaman", "chapter": 14,
        "keywords": ["thunder", "lightning", "earth", "shake", "tremble"],
        "description": "Thunder, lightning, earthquakes"
    },
    {
        "id": "S31", "book": "Helaman", "chapter": 14,
        "keywords": ["rock", "broken", "rent", "twain", "seam", "crack", "fragment"],
        "description": "Rocks broken up, found in seams and cracks"
    },
    {
        "id": "S32", "book": "Helaman", "chapter": 14,
        "keywords": ["mountain", "laid low", "valley", "height"],
        "description": "Mountains laid low, valleys become mountains"
    },
    {
        "id": "S33", "book": "Helaman", "chapter": 14,
        "keywords": ["highway", "broken", "cities", "desolate"],
        "description": "Highways broken, cities desolate"
    },
    {
        "id": "S34", "book": "Helaman", "chapter": 14,
        "keywords": ["grave", "opened", "dead", "saints", "appear"],
        "description": "Graves opened, saints appear"
    },
    {
        "id": "S35", "book": "Helaman", "chapter": 14,
        "keywords": ["darkness", "cover", "whole earth", "three days"],
        "description": "Darkness covers the whole earth for three days"
    },
    {
        "id": "S36", "book": "Helaman", "chapter": 15,
        "keywords": ["house", "desolate"],
        "description": "Houses left desolate"
    },
    {
        "id": "S37", "book": "Helaman", "chapter": 15,
        "keywords": ["flee", "no place", "refuge", "with child", "trodden", "perish"],
        "description": "No place of refuge; pregnant women trodden down"
    },
    {
        "id": "S38", "book": "Helaman", "chapter": 15,
        "keywords": ["Lamanite", "prolong", "days", "affliction", "driven", "merciful"],
        "description": "Lamanites preserved despite afflictions"
    },
    {
        "id": "S39", "book": "Helaman", "chapter": 15,
        "keywords": ["Lamanite", "true knowledge", "Redeemer", "shepherd", "sheep"],
        "description": "Lamanites brought to true knowledge of Redeemer"
    },
    {
        "id": "S40", "book": "Helaman", "chapter": 15,
        "keywords": ["not utterly destroy", "Lamanite", "return", "unto me"],
        "description": "Lamanites not utterly destroyed; shall return"
    },
    {
        "id": "S41", "book": "Helaman", "chapter": 15,
        "keywords": ["utterly destroy", "Nephite", "unbelief", "repent"],
        "description": "Nephites utterly destroyed if they don't repent"
    },
]


def load_json():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def is_after(verse_book, verse_chapter, prophecy_book, prophecy_chapter):
    """Return True if the verse comes AFTER the prophecy's location."""
    vb = book_index(verse_book)
    pb = book_index(prophecy_book)
    if vb > pb:
        return True
    if vb == pb and verse_chapter > prophecy_chapter:
        return True
    return False


def score_verse(text_lower, keywords):
    """Score how well a verse matches a prophecy's keywords.
    Returns (score, matched_terms)."""
    matched = []
    score = 0
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in text_lower:
            # Multi-word phrases get higher weight
            weight = len(kw_lower.split())
            score += weight
            matched.append(kw)
    return score, matched


def search_fulfillments(data, prophecy, min_score=2):
    """Find all verses after the prophecy's location that match keywords."""
    results = []
    for book in data["books"]:
        for chapter in book["chapters"]:
            if not is_after(book["book"], chapter["chapter"],
                          prophecy["book"], prophecy["chapter"]):
                continue
            for verse in chapter["verses"]:
                text_lower = verse["text"].lower()
                score, matched = score_verse(text_lower, prophecy["keywords"])
                if score >= min_score:
                    results.append({
                        "reference": verse["reference"],
                        "book": book["book"],
                        "chapter": chapter["chapter"],
                        "verse": verse["verse"],
                        "text": verse["text"],
                        "score": score,
                        "matched_terms": matched,
                    })
    # Sort by score descending, then by book order
    results.sort(key=lambda r: (-r["score"], book_index(r["book"]), r["chapter"], r["verse"]))
    return results


def generate_markdown(all_results):
    """Generate a markdown report from the search results."""
    lines = [
        "# V3 Comprehensive Fulfillment Search Results",
        "",
        "Left-join of all 65 prophecies against the full Book of Mormon text.",
        "Each prophecy shows ALL candidate fulfillment verses found after the prophecy's location.",
        "",
        "> **Method**: Keyword matching with term weighting. Min score = 2 (at least 2 single-word matches or 1 multi-word phrase).",
        "> **Scope**: Only verses *after* the prophecy's book/chapter are searched.",
        "",
        "---",
        "",
    ]

    total_matches = 0
    for prophecy_id, prophecy_desc, results in all_results:
        count = len(results)
        total_matches += count
        lines.append(f"## {prophecy_id}: {prophecy_desc}")
        lines.append("")
        if not results:
            lines.append("*No matches found above threshold.*")
            lines.append("")
        else:
            lines.append(f"**{count} candidate(s) found**")
            lines.append("")
            lines.append("| Score | Reference | Matched Terms | Text (truncated) |")
            lines.append("|-------|-----------|---------------|------------------|")
            # Show top 15 per prophecy to keep it readable
            for r in results[:15]:
                text_trunc = r["text"][:150].replace("|", "\\|") + ("..." if len(r["text"]) > 150 else "")
                terms = ", ".join(r["matched_terms"])
                lines.append(f"| {r['score']} | {r['reference']} | {terms} | {text_trunc} |")
            if count > 15:
                lines.append(f"| ... | *{count - 15} more results omitted* | | |")
            lines.append("")
        lines.append("---")
        lines.append("")

    # Summary at top
    summary = f"\n**Total: {total_matches} candidate matches across {len(all_results)} prophecies**\n"
    lines.insert(9, summary)

    OUTPUT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Markdown report: {OUTPUT_MD_PATH}")


def main():
    data = load_json()
    all_results = []

    for p in PROPHECIES:
        results = search_fulfillments(data, p)
        all_results.append((p["id"], p["description"], results))
        match_count = len(results)
        top_refs = ", ".join(r["reference"] for r in results[:3])
        print(f"  {p['id']:>3}: {match_count:>3} matches  (top: {top_refs})")

    # Save JSON for further analysis
    json_output = {}
    for pid, pdesc, results in all_results:
        json_output[pid] = {
            "description": pdesc,
            "match_count": len(results),
            "matches": [
                {
                    "reference": r["reference"],
                    "score": r["score"],
                    "matched_terms": r["matched_terms"],
                    "text": r["text"],
                }
                for r in results[:20]  # Top 20 per prophecy
            ]
        }
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"\nJSON output: {OUTPUT_PATH}")

    generate_markdown(all_results)
    print("Done!")


if __name__ == "__main__":
    main()
