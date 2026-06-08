import chromadb
from sentence_transformers import SentenceTransformer

from ingest import load_documents


#  Configuration

EMBEDDING_MODEL  = "all-MiniLM-L6-v2"
CHROMA_DIR       = "chroma_db"          # local folder ChromaDB writes to
COLLECTION_NAME  = "ccny_professors"
BATCH_SIZE       = 64                   # embed this many chunks at a time


#  Helpers

def get_or_create_collection(client: chromadb.PersistentClient):
    """
    Return the named collection, creating it fresh each run.
    Deletes any existing collection with the same name so re-running
    embed.py always produces a clean, consistent store.
    """
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}' for a clean rebuild.")

    collection = client.create_collection(
        name     = COLLECTION_NAME,
        metadata = {"hnsw:space": "cosine"},   # cosine similarity for retrieval
    )
    return collection


def batch(iterable: list, size: int):
    """Yield successive slices of `size` from `iterable`."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


#  Main
def embed_and_store():
    print("\n── Embeddings + ChromaDB ────────────────────────────────────────\n")

    # 1. Load chunks from ingest.py
    print("Loading documents and chunks...")
    chunks = load_documents()
    print(f"  {len(chunks):,} chunks ready for embedding.\n")

    # 2. Load the embedding model
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("  Model loaded.\n")

    # 3. Connect to (or create) the local ChromaDB store
    client     = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = get_or_create_collection(client)
    print(f"Collection '{COLLECTION_NAME}' ready.\n")

    # 4. Embed and store in batches to avoid memory spikes
    print(f"Embedding and storing chunks (batch size = {BATCH_SIZE})...")
    stored = 0

    for chunk_batch in batch(chunks, BATCH_SIZE):
        texts     = [c["text"]     for c in chunk_batch]
        sources   = [c["source"]   for c in chunk_batch]
        chunk_ids = [c["chunk_id"] for c in chunk_batch]

        # Unique ChromaDB document ID: "filename__chunkN"
        ids = [
            f"{src}__{cid}"
            for src, cid in zip(sources, chunk_ids)
        ]

        # Generate embeddings (returns a numpy array)
        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        collection.add(
            ids        = ids,
            documents  = texts,
            embeddings = embeddings,
            metadatas  = [
                {"source": src, "chunk_id": cid}
                for src, cid in zip(sources, chunk_ids)
            ],
        )
        stored += len(chunk_batch)
        print(f"  Stored {stored:,} / {len(chunks):,} chunks...", end="\r")

    print(f"\n\nDone. Total chunks stored in ChromaDB: {stored:,}")
    print(f"Collection path : {CHROMA_DIR}/")
    print(f"Collection name : {COLLECTION_NAME}\n")

    return collection


if __name__ == "__main__":
    embed_and_store()