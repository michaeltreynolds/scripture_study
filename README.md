# 📖 Scripture Study

AI-assisted studies of the Book of Mormon. Each folder is an independent study project, using Python scripts and [OpenAI](https://openai.com/) APIs to explore the text computationally — keyword search, semantic embeddings, and LLM-driven analysis.

## Source Data

All projects share a single copy of `book-of-mormon.json` in the `data/` folder, sourced from [bcbooks/scriptures-json](https://github.com/bcbooks/scriptures-json) (public domain). Created by Ben Crowder; text from the [Mormon Documentation Project](http://scriptures.nephi.org/).

## Projects

| Folder | Description |
|--------|-------------|
| [`groupings_suarez_bednar`](groupings_suarez_bednar/) | Examines the Book of Mormon chapter by chapter through five lenses inspired by Elder Bednar/Suarez: what it **affirms**, **refutes**, **fulfills**, **clarifies**, and **reveals**. Uses OpenAI to analyze each chapter and produce categorized insights. |
| [`abinidai_samuel_prophecies`](abinidai_samuel_prophecies/) | A comprehensive, verse-by-verse analysis of all 65 prophecies from Abinadi (Mosiah 11–17) and Samuel the Lamanite (Helaman 13–16), tracing their fulfillment across the entire Book of Mormon text. Uses keyword search and OpenAI embedding-based semantic search. See [`Final_Report_V5.md`](abinidai_samuel_prophecies/Final_Report_V5.md) for the full report. |

## Setup (for re-running scripts)

The generated reports and output files are already included — you don't need to run anything to read them. If you want to re-run the Python scripts yourself:

1. **Python 3.10+** and a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .venv\Scripts\activate      # Windows
   pip install openai numpy
   ```

2. **OpenAI API Key** — set as an environment variable:
   ```bash
   export OPENAI_API_KEY=sk-...        # macOS/Linux
   $env:OPENAI_API_KEY = "sk-..."      # PowerShell
   ```

## Tools & Credits

| Tool | Role |
|------|------|
| [Antigravity (Google DeepMind)](https://deepmind.google/) | AI coding assistant — research, scripting, analysis |
| [OpenAI `text-embedding-3-small`](https://platform.openai.com/docs/guides/embeddings) | Embedding model for semantic search |
| [bcbooks/scriptures-json](https://github.com/bcbooks/scriptures-json) | Structured JSON Book of Mormon text (public domain) |

## License

The scripture text is public domain. Scripts and analysis in this repo are shared freely — use them however you'd like.\n