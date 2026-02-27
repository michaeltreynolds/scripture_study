"""
Embedding-based semantic search for prophecy fulfillments.
Uses OpenAI text-embedding-3-small to find semantic matches
that keyword search missed.
"""
import json
import time
import numpy as np
from pathlib import Path
from openai import OpenAI

# Load API key
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load Book of Mormon
data = json.load(open(Path(__file__).parent.parent / "data" / "book-of-mormon.json", encoding="utf-8"))

BOOK_ORDER = [
    "1 Nephi", "2 Nephi", "Jacob", "Enos", "Jarom", "Omni",
    "Words of Mormon", "Mosiah", "Alma", "Helaman",
    "3 Nephi", "4 Nephi", "Mormon", "Ether", "Moroni"
]

# All 65 prophecies with their text and start location
PROPHECIES = {
    # Abinadi - start after Mosiah 11
    "A1": {"text": "Wo upon this people. I have seen their abominations, and their wickedness, and their whoredoms; and except they repent I will visit them in mine anger.", "after": ("Mosiah", 11)},
    "A2": {"text": "I will deliver them into the hands of their enemies; yea, and they shall be brought into bondage; and they shall be afflicted by the hand of their enemies.", "after": ("Mosiah", 11)},
    "A3": {"text": "They shall know that I am the Lord their God, and am a jealous God, visiting the iniquities of my people.", "after": ("Mosiah", 11)},
    "A4": {"text": "They shall be brought into bondage; and none shall deliver them, except it be the Lord the Almighty God.", "after": ("Mosiah", 11)},
    "A5": {"text": "When they shall cry unto me I will be slow to hear their cries; yea, and I will suffer them that they be smitten by their enemies.", "after": ("Mosiah", 11)},
    "A6": {"text": "Except they repent in sackcloth and ashes, and cry mightily to the Lord their God, I will not hear their prayers, neither will I deliver them out of their afflictions.", "after": ("Mosiah", 11)},
    "A7": {"text": "I will visit them in my anger, yea, in my fierce anger will I visit them in their iniquities and abominations.", "after": ("Mosiah", 12)},
    "A8": {"text": "This generation shall be brought into bondage, and shall be smitten on the cheek; yea, and shall be driven by men, and shall be slain; and the vultures of the air, and the dogs, yea, and the wild beasts, shall devour their flesh.", "after": ("Mosiah", 12)},
    "A9": {"text": "The life of king Noah shall be valued even as a garment in a hot furnace; for he shall know that I am the Lord.", "after": ("Mosiah", 12)},
    "A10": {"text": "I will smite this my people with sore afflictions, yea, with famine and with pestilence; and I will cause that they shall howl all the day long.", "after": ("Mosiah", 12)},
    "A11": {"text": "I will cause that they shall have burdens lashed upon their backs; and they shall be driven before like a dumb ass.", "after": ("Mosiah", 12)},
    "A12": {"text": "I will send forth hail among them, and it shall smite them; and they shall also be smitten with the east wind; and insects shall pester their land also, and devour their grain.", "after": ("Mosiah", 12)},
    "A13": {"text": "They shall be smitten with a great pestilence—and all this will I do because of their iniquities and abominations.", "after": ("Mosiah", 12)},
    "A14": {"text": "Except they repent I will utterly destroy them from off the face of the earth; yet they shall leave a record behind them, and I will preserve them for other nations which shall possess the land.", "after": ("Mosiah", 12)},
    "A15": {"text": "What you do with me, after this, shall be as a type and a shadow of things which are to come.", "after": ("Mosiah", 13)},
    "A16": {"text": "The wicked be cast out, and they shall have cause to howl, and weep, and wail, and gnash their teeth; and this because they would not hearken unto the voice of the Lord.", "after": ("Mosiah", 16)},
    "A17": {"text": "They are carnal and devilish, and the devil has power over them; yea, even that old serpent that did beguile our first parents, subjecting themselves to the devil.", "after": ("Mosiah", 16)},
    "A18": {"text": "He that persists in his own carnal nature, and goes on in the ways of sin and rebellion against God, remaineth in his fallen state and the devil hath all power over him.", "after": ("Mosiah", 16)},
    "A19": {"text": "He is the light and the life of the world; yea, a light that is endless, that can never be darkened.", "after": ("Mosiah", 16)},
    "A20": {"text": "Thy seed shall cause that many shall suffer the pains that I do suffer, even the pains of death by fire; and this because they believe in the salvation of the Lord their God.", "after": ("Mosiah", 17)},
    "A21": {"text": "Ye shall be afflicted with all manner of diseases because of your iniquities.", "after": ("Mosiah", 17)},
    "A22": {"text": "Ye shall be smitten on every hand, and shall be driven and scattered to and fro, even as a wild flock is driven by wild and ferocious beasts.", "after": ("Mosiah", 17)},
    "A23": {"text": "In that day ye shall be hunted, and ye shall be taken by the hand of your enemies, and then ye shall suffer, as I suffer, the pains of death by fire.", "after": ("Mosiah", 17)},
    "A24": {"text": "Thus God executeth vengeance upon those that destroy his people.", "after": ("Mosiah", 17)},
    # Samuel the Lamanite - start after Helaman 13-16
    "S1": {"text": "The sword of justice hangeth over this people; and four hundred years pass not away save the sword of justice falleth upon this people.", "after": ("Helaman", 13)},
    "S2": {"text": "Heavy destruction awaiteth this people, and it surely cometh; nothing can save this people save it be repentance and faith on the Lord Jesus Christ.", "after": ("Helaman", 13)},
    "S3": {"text": "I will take away my word from them, and I will withdraw my Spirit from them, and I will suffer them no longer, and I will turn the hearts of their brethren against them.", "after": ("Helaman", 13)},
    "S4": {"text": "Four hundred years shall not pass away before I will cause that they shall be smitten with the sword and with famine and with pestilence.", "after": ("Helaman", 13)},
    "S5": {"text": "There shall be those of the fourth generation who shall live, of your enemies, to behold your utter destruction.", "after": ("Helaman", 13)},
    "S6": {"text": "It is because of those who are righteous that Zarahemla is saved; if it were not for the righteous I would cause that fire should come down out of heaven and destroy it.", "after": ("Helaman", 13)},
    "S7": {"text": "When ye shall cast out the righteous from among you, then shall ye be ripe for destruction.", "after": ("Helaman", 13)},
    "S8": {"text": "A curse shall come upon the land because of the people who are upon the land, because of their wickedness and their abominations.", "after": ("Helaman", 13)},
    "S9": {"text": "Whoso shall hide up treasures in the earth shall find them again no more, because of the great curse of the land.", "after": ("Helaman", 13)},
    "S10": {"text": "Cursed be they who hide not up their treasures unto me; for none hideth up their treasures unto me save it be the righteous.", "after": ("Helaman", 13)},
    "S11": {"text": "They shall hide up their treasures because they have set their hearts upon riches; and because they will not hide them up unto me, cursed be they and also their treasures.", "after": ("Helaman", 13)},
    "S12": {"text": "He saith that ye are cursed because of your riches, and also are your riches cursed because ye have set your hearts upon them.", "after": ("Helaman", 13)},
    "S13": {"text": "For this cause hath the Lord God caused that a curse should come upon the land, and also upon your riches, and this because of your iniquities.", "after": ("Helaman", 13)},
    "S14": {"text": "Ye do cast out the prophets, and do mock them; if a prophet come among you and declareth unto you the word of the Lord ye are angry with him and say he is a false prophet.", "after": ("Helaman", 13)},
    "S15": {"text": "If a man shall come among you and say walk after the pride of your own hearts ye will receive him and say that he is a prophet.", "after": ("Helaman", 13)},
    "S16": {"text": "The anger of the Lord is already kindled against you; he hath cursed the land because of your iniquity.", "after": ("Helaman", 13)},
    "S17": {"text": "He curseth your riches, that they become slippery, that ye cannot hold them; and in the days of your poverty ye cannot retain them.", "after": ("Helaman", 13)},
    "S18": {"text": "In the days of your poverty ye shall cry unto the Lord; and in vain shall ye cry, for your desolation is already come upon you, and your destruction is made sure.", "after": ("Helaman", 13)},
    "S19": {"text": "O that I had repented, and had not killed the prophets; O that we had remembered the Lord our God; our riches are gone from us.", "after": ("Helaman", 13)},
    "S20": {"text": "We lay a tool here and on the morrow it is gone; and our swords are taken from us in the day we have sought them for battle.", "after": ("Helaman", 13)},
    "S21": {"text": "We have hid up our treasures and they have slipped away from us, because of the curse of the land.", "after": ("Helaman", 13)},
    "S22": {"text": "The land is cursed, and all things are become slippery, and we cannot hold them.", "after": ("Helaman", 13)},
    "S23": {"text": "We are surrounded by demons, yea, we are encircled about by the angels of him who hath sought to destroy our souls.", "after": ("Helaman", 13)},
    "S24": {"text": "Your days of probation are past; ye have procrastinated the day of your salvation until it is everlastingly too late, and your destruction is made sure.", "after": ("Helaman", 13)},
    "S25": {"text": "Five years more cometh, and behold, then cometh the Son of God to redeem all those who shall believe on his name.", "after": ("Helaman", 14)},
    "S26": {"text": "In the night before he cometh there shall be no darkness; it shall be one day and a night and a day, as if it were one day and there were no night.", "after": ("Helaman", 14)},
    "S27": {"text": "There shall a new star arise, such an one as ye never have beheld.", "after": ("Helaman", 14)},
    "S28": {"text": "There shall be many signs and wonders in heaven.", "after": ("Helaman", 14)},
    "S29": {"text": "The sun shall be darkened and refuse to give his light; there shall be no light upon the face of this land for the space of three days.", "after": ("Helaman", 14)},
    "S30": {"text": "There shall be thunderings and lightnings for the space of many hours, and the earth shall shake and tremble.", "after": ("Helaman", 14)},
    "S31": {"text": "The rocks shall be broken up, rent in twain, and shall ever after be found in seams and in cracks, and in broken fragments upon the face of the whole earth.", "after": ("Helaman", 14)},
    "S32": {"text": "Many mountains laid low, like unto a valley, and there shall be many places which are now called valleys which shall become mountains.", "after": ("Helaman", 14)},
    "S33": {"text": "Many highways shall be broken up, and many cities shall become desolate.", "after": ("Helaman", 14)},
    "S34": {"text": "Many graves shall be opened, and shall yield up many of their dead; and many saints shall appear unto many.", "after": ("Helaman", 14)},
    "S35": {"text": "Darkness should cover the face of the whole earth for the space of three days.", "after": ("Helaman", 14)},
    "S36": {"text": "Except ye shall repent your houses shall be left unto you desolate.", "after": ("Helaman", 15)},
    "S37": {"text": "Ye shall attempt to flee and there shall be no place for refuge; and wo unto them which are with child, for they shall be heavy and cannot flee; therefore, they shall be trodden down and shall be left to perish.", "after": ("Helaman", 15)},
    "S38": {"text": "The Lord shall prolong their days notwithstanding the many afflictions which they shall have; notwithstanding they shall be driven to and fro upon the face of the earth the Lord shall be merciful unto the Lamanites.", "after": ("Helaman", 15)},
    "S39": {"text": "The Lamanites shall again be brought to the true knowledge, which is the knowledge of their Redeemer.", "after": ("Helaman", 15)},
    "S40": {"text": "I will not utterly destroy the Lamanites, but I will cause that in the day of my wisdom they shall return again unto me.", "after": ("Helaman", 15)},
    "S41": {"text": "If the Nephites will not repent, and observe to do my will, I will utterly destroy them because of their unbelief.", "after": ("Helaman", 15)},
}


def get_embeddings(texts, model="text-embedding-3-small"):
    """Get embeddings for a list of texts, batching to stay under limits."""
    all_embeddings = []
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        resp = client.embeddings.create(input=batch, model=model)
        all_embeddings.extend([d.embedding for d in resp.data])
        if i + batch_size < len(texts):
            time.sleep(0.5)  # rate limit courtesy
    return np.array(all_embeddings)


def cosine_sim(a, b):
    """Cosine similarity between two vectors or a vector and matrix."""
    if b.ndim == 1:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return np.dot(b, a) / (np.linalg.norm(b, axis=1) * np.linalg.norm(a))


def get_verses_after(after_book, after_chapter):
    """Get all verses after a given book/chapter location."""
    verses = []
    past_start = False
    for b in data["books"]:
        book_name = b["book"]
        if book_name not in BOOK_ORDER:
            continue
        book_idx = BOOK_ORDER.index(book_name)
        start_idx = BOOK_ORDER.index(after_book)
        
        if book_idx < start_idx:
            continue
        
        for c in b["chapters"]:
            if book_name == after_book and c["chapter"] <= after_chapter:
                continue
            past_start = True
            for v in c["verses"]:
                verses.append({
                    "reference": v["reference"],
                    "text": v["text"],
                    "book": book_name,
                    "chapter": c["chapter"]
                })
    return verses


def main():
    print("=" * 60)
    print("EMBEDDING-BASED PROPHECY FULFILLMENT SEARCH")
    print("=" * 60)
    
    # Step 1: Collect all unique verse texts we need to embed
    # Group prophecies by their "after" location to reuse verse sets
    location_groups = {}
    for pid, pdata in PROPHECIES.items():
        key = pdata["after"]
        if key not in location_groups:
            location_groups[key] = []
        location_groups[key].append(pid)
    
    print(f"\n{len(location_groups)} unique start locations")
    
    # Step 2: For each location group, get verses and embed them
    results = {}
    
    for (after_book, after_ch), pids in location_groups.items():
        print(f"\nProcessing {len(pids)} prophecies starting after {after_book} {after_ch}...")
        
        verses = get_verses_after(after_book, after_ch)
        print(f"  {len(verses)} candidate verses to search")
        
        if not verses:
            for pid in pids:
                results[pid] = []
            continue
        
        # Embed prophecy texts
        prophecy_texts = [PROPHECIES[pid]["text"] for pid in pids]
        print(f"  Embedding {len(prophecy_texts)} prophecy texts...")
        prophecy_embeddings = get_embeddings(prophecy_texts)
        
        # Embed verse texts (in batches)
        verse_texts = [v["text"] for v in verses]
        print(f"  Embedding {len(verse_texts)} verse texts...")
        verse_embeddings = get_embeddings(verse_texts)
        
        # Compute similarities
        for i, pid in enumerate(pids):
            sims = cosine_sim(prophecy_embeddings[i], verse_embeddings)
            # Get top 15 matches
            top_indices = np.argsort(sims)[-15:][::-1]
            matches = []
            for idx in top_indices:
                if sims[idx] >= 0.35:  # min threshold
                    matches.append({
                        "reference": verses[idx]["reference"],
                        "similarity": float(sims[idx]),
                        "text": verses[idx]["text"][:200]
                    })
            results[pid] = matches
        
        print(f"  Done.")
    
    # Step 3: Write results
    out_json = Path(__file__).parent / "v4_embedding_results.json"
    json.dump(results, open(out_json, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    
    out_md = Path(__file__).parent / "v4_embedding_results.md"
    lines = ["# V4 Embedding-Based Search Results\n"]
    lines.append("Semantic search using OpenAI `text-embedding-3-small`. Min similarity threshold: 0.35.\n")
    lines.append("---\n")
    
    total_matches = 0
    for pid in sorted(results.keys(), key=lambda x: (x[0], int(x[1:]))):
        matches = results[pid]
        total_matches += len(matches)
        prophecy_text = PROPHECIES[pid]["text"][:100]
        lines.append(f"\n## {pid}: {prophecy_text}...\n")
        if not matches:
            lines.append("*No matches above threshold.*\n")
        else:
            lines.append(f"**{len(matches)} match(es)**\n")
            lines.append("| Sim | Reference | Text (truncated) |")
            lines.append("|-----|-----------|-------------------|")
            for m in matches:
                lines.append(f"| {m['similarity']:.3f} | {m['reference']} | {m['text'][:120]}... |")
        lines.append("\n---\n")
    
    lines.insert(2, f"**Total: {total_matches} matches across {len(PROPHECIES)} prophecies**\n")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    
    print(f"\nTotal: {total_matches} matches")
    print(f"JSON: {out_json}")
    print(f"Markdown: {out_md}")
    print("Done!")


if __name__ == "__main__":
    main()
