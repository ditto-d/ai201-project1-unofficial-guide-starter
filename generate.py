import os
from groq import Groq

from retrieve import retrieve
from dotenv import load_dotenv

load_dotenv()

#  Configuration

GROQ_MODEL         = "llama-3.3-70b-versatile"   # fast, free-tier Groq model
TOP_K              = 5
MIN_SCORE          = 0.30               # chunks below this score are considered weak
MIN_RELEVANT_CHUNKS = 2                 # refuse if fewer than this many chunks qualify


#  Prompt builder

def build_prompt(question: str, chunks: list[dict]) -> str:
    """
    Construct a grounded system + user prompt.

    The model is instructed to:
      - answer only from the provided context
      - cite sources inline
      - admit when it does not know
    """
    context_blocks = []
    for i, chunk in enumerate(chunks, start=1):
        context_blocks.append(
            f"[Source {i}: {chunk['source']} | chunk {chunk['chunk_id']} "
            f"| similarity {chunk['score']:.2f}]\n{chunk['text']}"
        )
    context = "\n\n---\n\n".join(context_blocks)

    system_prompt = (
        "You are a helpful academic advisor assistant for students at "
        "City College of New York (CCNY). "
        "You answer questions about professors, courses, and workload "
        "based ONLY on the student reviews and course information provided below. "
        "Do not use any outside knowledge. "
        "When you use information from a source, cite it as [Source N]. "
        "If the provided context does not contain enough information to answer "
        "the question, say exactly: "
        "'I don't have enough information in my sources to answer that question.'"
    )

    user_prompt = (
        f"Context from student reviews and course documents:\n\n"
        f"{context}\n\n"
        f"---\n\n"
        f"Question: {question}\n\n"
        f"Answer (cite sources inline, e.g. [Source 1]):"
    )

    return system_prompt, user_prompt


#  Relevance check

def has_enough_context(chunks: list[dict]) -> bool:
    """
    Return True if at least MIN_RELEVANT_CHUNKS chunks meet the MIN_SCORE
    threshold. Used to decide whether to call the LLM at all.
    """
    strong = [c for c in chunks if c["score"] >= MIN_SCORE]
    return len(strong) >= MIN_RELEVANT_CHUNKS


#  Core answer function

def answer(question: str, verbose: bool = True) -> str:
    """
    Full RAG pipeline: retrieve → check relevance → generate → return answer.

    Returns the model's answer string (with source citations), or a
    polite refusal if context is insufficient.
    """
    # 1. Retrieve top-k chunks
    chunks = retrieve(question, top_k=TOP_K)

    if verbose:
        print(f"\n── Retrieved {len(chunks)} chunks ──")
        for i, c in enumerate(chunks, 1):
            print(f"  [{i}] score={c['score']:.4f}  source={c['source']}")
        print()

    # 2. Check whether retrieved context is strong enough
    if not has_enough_context(chunks):
        refusal = (
            "I don't have enough information in my sources to answer that question. "
            "Try rephrasing, or ask about a specific CCNY CS professor or course."
        )
        if verbose:
            print(f"⚠  Insufficient context (threshold={MIN_SCORE}, "
                  f"required={MIN_RELEVANT_CHUNKS} strong chunks). Refusing.\n")
        return refusal

    # 3. Build the prompt
    system_prompt, user_prompt = build_prompt(question, chunks)

    # 4. Call Groq
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY environment variable is not set. "
            "Export it before running: export GROQ_API_KEY='your-key'"
        )

    client = Groq(api_key=api_key)

    if verbose:
        print(f"Sending prompt to Groq ({GROQ_MODEL})...\n")

    response = client.chat.completions.create(
        model    = GROQ_MODEL,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature = 0.2,    # low temperature for factual, grounded answers
        max_tokens  = 512,
    )

    answer_text = response.choices[0].message.content.strip()

    # 5. Append a source legend at the bottom
    source_legend = "\n\n── Sources ──────────────────────────────────────────\n"
    seen = {}
    for i, chunk in enumerate(chunks, 1):
        key = chunk["source"]
        if key not in seen:
            seen[key] = []
        seen[key].append(f"Source {i}")

    for src, labels in seen.items():
        source_legend += f"  {', '.join(labels)} → {src}\n"

    return answer_text + source_legend


#  Main (demo)

def main():
    demo_questions = [
        "What do students say about Professor Grossberg's exams?",
        "How do I do well in Troeger's class?",
        "What workload should I expect in upper-level CS courses at CCNY?",
        "What is the best pizza place near CCNY?",   # out-of-domain → refusal
    ]

    for q in demo_questions:
        print("=" * 70)
        print(f"QUESTION: {q}\n")
        result = answer(q, verbose=True)
        print(f"ANSWER:\n{result}\n")


if __name__ == "__main__":
    main()