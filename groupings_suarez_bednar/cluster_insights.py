import csv
import os
import sys
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.cluster import AgglomerativeClustering

load_dotenv()

OUTPUT_DIR = "output"

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CATEGORIES = {
    "affirms": {"title": "What It Affirms", "emoji": "✅"},
    "refutes": {"title": "What It Refutes", "emoji": "🚫"},
    "fulfills": {"title": "What It Fulfills", "emoji": "📜"},
    "clarifies": {"title": "What It Clarifies", "emoji": "💡"},
    "reveals": {"title": "What It Reveals", "emoji": "🌟"},
}


def read_csv(cat_key):
    path = os.path.join(OUTPUT_DIR, f"{cat_key}.csv")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ref = row["Reference"].strip()
            insight = row["Insight"].strip()
            if ref and insight:
                rows.append((ref, insight))
    return rows


def get_embeddings(texts, batch_size=100):
    """Embed a list of texts using OpenAI's small embedding model."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = openai_client.embeddings.create(
            model="text-embedding-3-small", input=batch
        )
        all_embeddings.extend([d.embedding for d in resp.data])
    return np.array(all_embeddings)


def cluster_by_distance(rows, distance_threshold=0.35):
    """Cluster insights by cosine distance threshold — produces many granular themes."""
    if len(rows) <= 1:
        return [rows]

    texts = [insight for _, insight in rows]
    embeddings = get_embeddings(texts)

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="cosine",
        linkage="average",
    )
    labels = clustering.fit_predict(embeddings)

    clusters = {}
    for label, row in zip(labels, rows):
        clusters.setdefault(label, []).append(row)

    return sorted(clusters.values(), key=len, reverse=True)


def cluster_by_count(rows, target_clusters=5):
    """Cluster insights into a fixed number of high-level groups."""
    if len(rows) <= 1:
        return [rows]

    n = min(target_clusters, len(rows))
    texts = [insight for _, insight in rows]
    embeddings = get_embeddings(texts)

    clustering = AgglomerativeClustering(
        n_clusters=n,
        metric="cosine",
        linkage="average",
    )
    labels = clustering.fit_predict(embeddings)

    clusters = {}
    for label, row in zip(labels, rows):
        clusters.setdefault(label, []).append(row)

    return sorted(clusters.values(), key=len, reverse=True)


def pick_label(cluster_rows):
    """Use the LLM to summarize a cluster into one clean label."""
    if len(cluster_rows) == 1:
        return cluster_rows[0][1]

    insights = "\n".join(f"- {ins}" for _, ins in cluster_rows)
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Summarize these similar insights into ONE concise sentence that captures the shared theme. No preamble, just the sentence.",
            },
            {"role": "user", "content": insights},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def generate_report(mode="distance"):
    """Generate a clustered report. mode='distance' for granular, 'fixed' for 3-5 clusters."""
    if mode == "summary":
        out_file = os.path.join(OUTPUT_DIR, "summary_report.md")
        title = "Summary Report"
        subtitle = "One overarching theme per category with counts."
    elif mode == "distance":
        out_file = os.path.join(OUTPUT_DIR, "detail_report.md")
        title = "Detail Report (Granular Themes)"
        subtitle = "Insights clustered by semantic similarity. Similar ideas grouped together with counts."
    else:
        out_file = os.path.join(OUTPUT_DIR, "cluster_report.md")
        title = "Cluster Report (High-Level Themes)"
        subtitle = "Insights grouped into ~5 broad themes per category."

    lines = []
    lines.append(f"# 📖 Book of Mormon Study — {title}\n")
    lines.append(f"{subtitle}\n")
    lines.append("---\n")

    for cat_key, cat_info in CATEGORIES.items():
        rows = read_csv(cat_key)
        print(f"\n{cat_info['emoji']} {cat_info['title']}: {len(rows)} raw insights", flush=True)

        if not rows:
            lines.append(f"## {cat_info['emoji']} {cat_info['title']}\n")
            lines.append("*(No insights found.)*\n\n---\n")
            continue

        print("  Embedding and clustering...", flush=True)
        if mode == "summary":
            clusters = cluster_by_distance(rows, distance_threshold=0.75)
        elif mode == "distance":
            clusters = cluster_by_distance(rows)
        else:
            clusters = cluster_by_count(rows)
        print(f"  → {len(clusters)} themes found", flush=True)

        lines.append(f"## {cat_info['emoji']} {cat_info['title']}\n")
        lines.append(f"*{len(rows)} insights → {len(clusters)} themes*\n")

        print("  Generating cluster labels...", flush=True)
        for cluster_rows in clusters:
            count = len(cluster_rows)
            label = pick_label(cluster_rows)
            refs = ", ".join(ref for ref, _ in cluster_rows)

            if count > 1:
                lines.append(f"- **({count})** {label}")
                lines.append(f"  - *{refs}*\n")
            else:
                lines.append(f"- (1) {label}")
                lines.append(f"  - *{refs}*\n")

        lines.append("\n---\n")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nDone! Report saved to {out_file}", flush=True)


if __name__ == "__main__":
    # Usage:
    #   python cluster_insights.py summary   → concise 1-theme summary
    #   python cluster_insights.py distance  → granular themes by similarity
    #   python cluster_insights.py fixed     → 5 high-level clusters
    #   python cluster_insights.py all       → all three
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode == "all":
        print("=== SUMMARY REPORT ===", flush=True)
        generate_report("summary")
        print("\n\n=== HIGH-LEVEL CLUSTER REPORT ===", flush=True)
        generate_report("fixed")
    else:
        generate_report(mode)
