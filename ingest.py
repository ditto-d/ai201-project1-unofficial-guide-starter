import os
import re
import random


#  Configuration

DOCUMENTS_DIR = "documents"
CHUNK_SIZE    = 200   # words per chunk
OVERLAP       = 50    # words of overlap between consecutive chunks


#  Text cleaning

def clean_text(text: str) -> str:
    """
    Clean plain-text documents sourced from Reddit, RateMyProfessors,
    Quora, and CCNY web pages.

    These documents were already saved as .txt so there are no HTML tags,
    but we still clean:
      - HTML entities  (&amp; &nbsp; &#39; etc.)
      - Redundant whitespace and blank lines
      - UI boilerplate fragments that slipped in during manual copying
      - Unicode smart quotes / dashes normalised to ASCII
    """
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Decode common HTML entities (leftovers from copy-paste)
    entity_map = {
        "&amp;": "&", "&nbsp;": " ", "&#39;": "'", "&quot;": '"',
        "&lt;": "<", "&gt;": ">", "&mdash;": "—", "&ndash;": "–",
        "&hellip;": "...", "&lsquo;": "'", "&rsquo;": "'",
        "&ldquo;": '"', "&rdquo;": '"',
    }
    for entity, replacement in entity_map.items():
        text = text.replace(entity, replacement)

    # Normalise Unicode punctuation to ASCII equivalents
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", " - ").replace("\u2013", "-")
    text = text.replace("\u2026", "...")

    # Remove UI boilerplate patterns common in scraped Reddit / RMP text
    boilerplate = [
        r"Upvote\s*\d*\s*Downvote",
        r"Reply\s+Award\s+Share",
        r"Log In\s*Sign Up",
        r"Skip to main content",
        r"Rate My Professors.*?All Rights Reserved",
        r"© \d{4}.*?reserved\.?",
        r"Tags:\s*",                     # RMP tag labels — keep tag content
        r"\[deleted\]",
        r"Comment deleted by user",
        r"Comment removed by moderator",
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE | re.DOTALL)

    # Collapse multiple blank lines into one paragraph break
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse inline whitespace (tabs, multiple spaces) but preserve newlines
    text = re.sub(r"[ \t]+", " ", text)

    # Remove lines that are just whitespace
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    text  = "\n".join(lines)

    return text.strip()


#  Chunking

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks measured in words.

    The sliding window advances by (chunk_size - overlap) words per step,
    so consecutive chunks share `overlap` words of context.
    Empty strings and very short fragments (< 10 words) are discarded.
    """
    words = text.split()
    if not words:
        return []

    step   = chunk_size - overlap
    chunks = []

    for start in range(0, len(words), step):
        end   = start + chunk_size
        chunk = " ".join(words[start:end])

        # Discard fragments too short to carry meaning
        if len(chunk.split()) >= 10:
            chunks.append(chunk)

        if end >= len(words):
            break

    return chunks


#   Validation
def validate_chunk(chunk: str) -> list[str]:
    """
    Check a single chunk for known quality issues.
    Returns a list of warning strings (empty = chunk is clean).
    """
    warnings = []
    words    = chunk.split()

    if len(words) < 20:
        warnings.append(f"FRAGMENT: only {len(words)} words")

    if re.search(r"<[a-z]+[\s>]", chunk, re.IGNORECASE):
        warnings.append("HTML ARTIFACT: contains tag-like content")

    if re.search(r"&[a-z]+;", chunk, re.IGNORECASE):
        warnings.append("HTML ENTITY: contains un-decoded entity")

    if re.search(r"(skip to|log in|sign up|cookie|advertisement)", chunk,
                 re.IGNORECASE):
        warnings.append("BOILERPLATE: possible nav/ad content")

    return warnings


#  Per-file processor

def process_file(filepath: str) -> list[dict]:
    """
    Load, clean, and chunk one .txt file.
    Returns a list of chunk records with source metadata.
    """
    filename = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned = clean_text(raw)
    chunks  = chunk_text(cleaned)

    records = []
    for idx, chunk in enumerate(chunks):
        records.append({
            "source":   filename,
            "chunk_id": idx,
            "text":     chunk,
        })
    return records


#  Main
def load_documents(documents_dir: str = DOCUMENTS_DIR) -> list[dict]:
    """Load all .txt files and return flat list of chunk records."""
    if not os.path.isdir(documents_dir):
        raise FileNotFoundError(
            f"'{documents_dir}/' not found — create it and add your .txt files."
        )

    txt_files = sorted(
        f for f in os.listdir(documents_dir) if f.endswith(".txt")
    )
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in '{documents_dir}/'.")

    all_chunks = []
    for filename in txt_files:
        filepath = os.path.join(documents_dir, filename)
        all_chunks.extend(process_file(filepath))

    return all_chunks


def main():
    print("\n" + "=" * 65)
    print("  MILESTONE 3 — Ingestion + Chunking Diagnostic Report")
    print("=" * 65)

    all_chunks = load_documents()
    sources    = sorted(set(c["source"] for c in all_chunks))

    #  Per-file summary
    print(f"\n{'File':<45} {'Words':>6}  {'Chunks':>6}")
    print("-" * 62)
    for src in sources:
        filepath   = os.path.join(DOCUMENTS_DIR, src)
        with open(filepath, encoding="utf-8") as f:
            raw = f.read()
        word_count = len(clean_text(raw).split())
        chunk_count = sum(1 for c in all_chunks if c["source"] == src)
        print(f"{src:<45} {word_count:>6,}  {chunk_count:>6,}")

    print("-" * 62)
    print(f"{'TOTAL':<45} {'':>6}  {len(all_chunks):>6,}")

    #  Health check
    print(f"\n── Health check ──────────────────────────────────────────────")
    total = len(all_chunks)
    if total < 50:
        print(f"  ⚠  Only {total} chunks — consider smaller chunk size (chunks too large?)")
    elif total > 2000:
        print(f"  ⚠  {total} chunks — may be too many (chunks too small?)")
    else:
        print(f"  ✓  {total} chunks — within healthy range (50–2000)")

    issues = 0
    for c in all_chunks:
        warnings = validate_chunk(c["text"])
        if warnings:
            issues += 1
            print(f"  ⚠  [{c['source']} chunk {c['chunk_id']}] {'; '.join(warnings)}")
    if issues == 0:
        print(f"  ✓  All {total} chunks passed quality checks (no HTML, no fragments)")

    #  5 representative sample chunks
    print(f"\n── 5 representative sample chunks ────────────────────────────")

    # Pick: first, last, and three spread across the corpus
    indices = [
        0,
        total // 4,
        total // 2,
        (total * 3) // 4,
        total - 1,
    ]

    for rank, i in enumerate(indices, 1):
        c        = all_chunks[i]
        word_cnt = len(c["text"].split())
        warnings = validate_chunk(c["text"])
        status   = "✓ GOOD" if not warnings else f"⚠ {'; '.join(warnings)}"

        print(f"\n  ── Sample {rank} ──  [{status}]")
        print(f"  source={c['source']}  chunk_id={c['chunk_id']}  words={word_cnt}")
        print(f"  {'─'*55}")

        # Print full chunk text, wrapped at 65 chars per line
        words  = c["text"].split()
        line   = []
        for word in words:
            line.append(word)
            if len(" ".join(line)) > 65:
                print(f"  {' '.join(line[:-1])}")
                line = [line[-1]]
        if line:
            print(f"  {' '.join(line)}")

    #  Self-contained question test
    print(f"\n── Self-contained test (random chunk) ─────────────────────")
    test_chunk = random.choice(all_chunks)
    print(f"  source={test_chunk['source']}  chunk_id={test_chunk['chunk_id']}")
    print(f"\n  QUESTION: Could someone answer a question from this chunk alone?")
    print(f"  CHUNK TEXT:\n")
    words = test_chunk["text"].split()
    line  = []
    for word in words:
        line.append(word)
        if len(" ".join(line)) > 65:
            print(f"    {' '.join(line[:-1])}")
            line = [line[-1]]
    if line:
        print(f"    {' '.join(line)}")
    print(f"\n  (Answer the self-contained question manually before moving on.)")

    print(f"\n{'=' * 65}")
    print(f"  Documents loaded : {len(sources)}")
    print(f"  Total chunks     : {total}")
    print(f"  Chunk size       : {CHUNK_SIZE} words  |  Overlap: {OVERLAP} words")
    print(f"  Step size        : {CHUNK_SIZE - OVERLAP} words per advance")
    print(f"{'=' * 65}\n")

    return all_chunks


if __name__ == "__main__":
    main()