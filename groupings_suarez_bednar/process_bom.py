import json
import os
import csv
import time
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
BOM_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "book-of-mormon.json")
OUTPUT_DIR = "output"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # 'google' or 'openai'

# Initialize LLM client
if LLM_PROVIDER == "google":
    try:
        from google import genai
        google_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        GOOGLE_MODEL = "gemini-2.0-flash"
    except ImportError:
        import google.generativeai as genai_old
        genai_old.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        google_client = None
        google_model_old = genai_old.GenerativeModel('gemini-1.5-pro')
elif LLM_PROVIDER == "openai":
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Category definitions
CATEGORIES = {
    "affirms": (
        "Does this chapter affirm any SIGNIFICANT, GENERAL spiritual truths? "
        "Examples of the kind of thing we're looking for: 'God knows us by name', "
        "'We are children of God', 'We lived in heaven before we came to earth', "
        "'God keeps His promises'. We want big, meaningful affirmations — NOT plot summaries, "
        "NOT narrative events, NOT things specific only to the characters in the story."
    ),
    "refutes": (
        "Does this chapter clearly refute any FALSE BELIEFS commonly held by people today? "
        "For example: 'God no longer speaks to man', 'There are no consequences for sin', "
        "'Miracles have ceased'. We want clear, direct contradictions of modern false beliefs."
    ),
    "fulfills": (
        "Does this chapter demonstrate fulfillment of PROPHECIES from the Old Testament? "
        "The Book of Mormon itself — its existence, its people, its teachings — can be seen as "
        "fulfilling Old Testament prophecies. For example: Isaiah's prophecy of a record coming "
        "from the dust, the stick of Ephraim and the stick of Judah, the scattering and gathering "
        "of Israel, or prophecies about the Messiah. Only list clear, specific connections."
    ),
    "clarifies": (
        "Does this chapter clarify any TEACHINGS OF JESUS CHRIST that are less clear in the "
        "Old and New Testaments? For example: the purpose of baptism, the nature of the Atonement, "
        "the process of repentance, grace vs. works. Only list things where this text adds clarity "
        "beyond what the Bible already provides."
    ),
    "reveals": (
        "Does this chapter reveal anything we OTHERWISE WOULD NOT HAVE KNOWN — valuable knowledge "
        "about mankind, God, or the kingdom of heaven that is NOT available in the Bible? "
        "For example: details about the pre-mortal life, the spirit world, or God's plan for "
        "different civilizations. Only truly new information qualifies."
    ),
}


def load_bom():
    """Load the Book of Mormon JSON. Combine all verses into chapter-level text."""
    with open(BOM_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    chapters = []
    for book in data["books"]:
        for chapter in book["chapters"]:
            ref = chapter["reference"]  # e.g. "1 Nephi 1"
            # Combine all verses into one block of chapter text
            verses = []
            for v in chapter["verses"]:
                verses.append(v["text"])
            full_text = " ".join(verses)
            chapters.append((ref, full_text))
    return chapters


def build_prompt(chapter_ref, chapter_text, category_key, category_desc):
    return f"""You are an extremely selective scripture analyst. Read the ENTIRE chapter below as a whole and answer this question:

{category_desc}

CRITICAL RULES:
1. Think about the chapter AS A WHOLE — do NOT analyze verse by verse.
2. Most chapters will have NOTHING. Respond with exactly NONE for those. This is the expected, common answer.
3. Only list something if it is genuinely significant and clearly supported.
4. Maximum 1-2 items per chapter. If you find more than 2, pick only the most significant.
5. Do NOT list narrative events, plot points, or character actions — only broad truths/insights.
6. Do NOT be exhaustive. Be highly selective. Quality over quantity.

If nothing qualifies (the COMMON case), respond with exactly:
NONE

If something qualifies, use this format (one per line, no bullets, no numbering, just the chapter reference — do NOT cite individual verses):
{chapter_ref}, <One sentence insight>

--- CHAPTER TEXT ({chapter_ref}) ---
{chapter_text}
"""


def call_llm(prompt):
    """Call the configured LLM and return the response text."""
    if LLM_PROVIDER == "openai":
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are extremely selective. Most of the time the correct answer is NONE. Only respond with an insight when it is truly significant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    elif LLM_PROVIDER == "google":
        if google_client:
            resp = google_client.models.generate_content(
                model=GOOGLE_MODEL, contents=prompt
            )
            return resp.text.strip()
        else:
            resp = google_model_old.generate_content(prompt)
            return resp.text.strip()
    return ""


def parse_response(raw, chapter_ref):
    """Parse LLM response into list of (reference, insight) tuples.
    Returns empty list if NONE."""
    text = raw.strip()
    if not text or text.upper() == "NONE":
        return []

    results = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.upper() == "NONE":
            continue
        # Strip leading bullets / numbering
        if line and line[0] in "-•*":
            line = line[1:].strip()
        if line and line[0].isdigit():
            parts = line.split(".", 1)
            if len(parts) == 2 and parts[0].strip().isdigit():
                line = parts[1].strip()

        if "," in line:
            ref_part, insight = line.split(",", 1)
            ref_part = ref_part.strip()
            insight = insight.strip()
            if insight:
                results.append((ref_part, insight))
        elif line:
            results.append((chapter_ref, line))

    # Hard cap at 2 results per chapter
    return results[:2]


def init_csv(category_key):
    """Create output CSV with header if needed."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{category_key}.csv")
    if not os.path.isfile(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["Reference", "Insight"])
    return path


def append_csv(path, rows):
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for ref, insight in rows:
            writer.writerow([ref, insight])


def main():
    chapters = load_bom()
    total = len(chapters)
    print(f"Loaded {total} chapters from the Book of Mormon.", flush=True)

    # Allow partial runs: python process_bom.py [start] [end]
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else total

    csv_paths = {cat: init_csv(cat) for cat in CATEGORIES}

    for i, (chapter_ref, chapter_text) in enumerate(chapters[start:end], start=start):
        print(f"\n[{i+1}/{total}] {chapter_ref}", flush=True)

        for cat_key, cat_desc in CATEGORIES.items():
            prompt = build_prompt(chapter_ref, chapter_text, cat_key, cat_desc)
            try:
                raw = call_llm(prompt)
            except Exception as e:
                print(f"  ERROR ({cat_key}): {e}", flush=True)
                time.sleep(5)
                continue

            rows = parse_response(raw, chapter_ref)
            if rows:
                append_csv(csv_paths[cat_key], rows)
                print(f"  {cat_key}: {len(rows)}", flush=True)
            else:
                print(f"  {cat_key}: —", flush=True)

            time.sleep(0.5)

    print("\nDone! Results in output/", flush=True)


if __name__ == "__main__":
    main()
