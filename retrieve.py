import chromadb
from sentence_transformers import SentenceTransformer


#  Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_DIR      = "chroma_db"
COLLECTION_NAME = "ccny_professors"
TOP_K           = 5


#  Core retrieval function
def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Embed `query` and return the top_k most similar chunks.

    Each returned dict:
        {
            "text":       str,    chunk content
            "source":     str,    source filename
            "chunk_id":   int,    position within that file
            "score":      float,  cosine similarity (0–1, higher = more relevant)
        }
    """
    # Load model and collection (fast: model is cached after first load)
    model  = SentenceTransformer(EMBEDDING_MODEL)
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        raise RuntimeError(
            f"Collection '{COLLECTION_NAME}' not found in '{CHROMA_DIR}/'. "
            "Run embed.py first to build the vector store."
        )

    # Embed the query
    query_embedding = model.encode(query).tolist()

    # Query ChromaDB — include distances so we can compute similarity
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=15,
        include=["documents", "metadatas", "distances"],
    )

    # ChromaDB returns distances (lower = more similar for cosine space).
    # Convert to similarity: similarity = 1 - distance
    chunks = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text":     text,
            "source":   meta.get("source", "unknown"),
            "chunk_id": meta.get("chunk_id", -1),
            "score":    round(1 - dist, 4),
        })
    # Simple professor-name boosting
    query_lower = query.lower()

    for chunk in chunks:
        text_lower = chunk["text"].lower()

        if "grossberg" in query_lower and "grossberg" in text_lower:
            chunk["score"] += 0.25

        if "troeger" in query_lower and "troeger" in text_lower:
            chunk["score"] += 0.25

        if "skeith" in query_lower and "skeith" in text_lower:
            chunk["score"] += 0.25
    # Sort by descending similarity (should already be sorted, but be explicit)

    chunks.sort(key=lambda x: x["score"], reverse=True)
    return chunks[:top_k]


#  Pretty printer

def print_results(query: str, results: list[dict]) -> None:
    print(f"\n── Query: \"{query}\" ──────────────────────────────────────────\n")
    for rank, chunk in enumerate(results, start=1):
        preview = chunk["text"][:300].replace("\n", " ")
        print(f"Rank {rank}  |  score={chunk['score']:.4f}  |  source={chunk['source']}  "
              f"|  chunk_id={chunk['chunk_id']}")
        print(f"  {preview}...\n")


#  Main (demo)

def main():
    sample_queries = [
        "What do students say about Professor Grossberg's exams?",
        "How hard is Troeger's class?",
        "What is the workload like for CCNY computer science courses?",
        "Michael Grossberg workload",

        "Michael Grossberg lectures",

        "Douglas Troeger exams",

        "William Skeith curve",
    ]

    for query in sample_queries:
        results = retrieve(query)
        print_results(query, results)
        print("=" * 70)


if __name__ == "__main__":
    main()