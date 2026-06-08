# The Unofficial Guide - Project 1
## CCNY Computer Science: Professor Reviews and Course Advice

---

# Domain

CCNY students rely on two very different sources of information when making academic decisions. The official sources include 
department websites, degree requirements, and course catalogs. The unofficial sources include Rate My Professors reviews,
Reddit discussions, Quora posts, Discord conversations, and advice passed between students.

This project makes that unofficial knowledge searchable through Retrieval-Augmented Generation (RAG). Students can ask 
natural language questions such as:

- "How do I do well in Troeger's class?"
- "Does Skeith curve exams?"
- "What workload should I expect in upper-level CS courses?"

The system retrieves relevant information from student-generated sources and official department documents, then generates grounded answers with source attribution.

The goal is not to replace official advising, but to make scattered student knowledge accessible through a single interface.

---

# Document Sources

| # | Source | Type | URL or File Path |
|---|---------|---------|---------|
| 1 | Reddit r/CCNY – "How is CCNY for CS?" | Student discussion | https://www.reddit.com/r/CCNY/comments/1fdtv3f/ |
| 2 | Quora – "Does CCNY have a good CS program?" | Student discussion | https://www.quora.com/Does-The-City-College-of-New-York-CCNY-have-a-good-computer-science-program-for-undergraduates |
| 3 | CCNY Computer Science Research Page | Official department page | https://www.ccny.cuny.edu/compsci/research |
| 4 | Reddit r/CCNY – "What is CCNY really like?" | Student discussion | https://www.reddit.com/r/CCNY/comments/1l47u0u/ |
| 5 | Reddit r/CUNY – "Is City College that bad?" | Student discussion | https://www.reddit.com/r/CUNY/comments/1b501o0/ |
| 6 | Rate My Professors – Michael Grossberg | Professor reviews | https://www.ratemyprofessors.com/professor/854471 |
| 7 | Rate My Professors – Douglas Troeger | Professor reviews | https://www.ratemyprofessors.com/professor/432142 |
| 8 | Rate My Professors – CCNY Computer Science Listing | Professor reviews | https://www.ratemyprofessors.com/school/224 |
| 9 | Rate My Professors – William Skeith | Professor reviews | https://www.ratemyprofessors.com/professor/1316015 |
| 10 | CCNY Undergraduate Catalog | Official curriculum | https://ccny-undergraduate.catalog.cuny.edu/programs/CMPSC-BS |

---

# Chunking Strategy

Chunk Size: 200 words

Overlap: 50 words

### Why These Choices Fit My Documents

Most of my source documents are short professor reviews, Reddit discussions, and Quora responses.
A 200-word chunk is large enough to preserve context across multiple reviews while remaining small 
enough to isolate information about a specific professor, course, or topic. I originally experimented
with 300-word chunks and 50-word overlap. That produced only 18 chunks across the corpus, which 
reduced retrieval quality because each chunk contained too many unrelated ideas. Reducing the chunk size
to 200 words increased the corpus to 31 chunks, providing more retrieval candidates while still preserving 
context. The 50-word overlap helps maintain continuity when information spans chunk boundaries and reduces 
the chance of losing important context.


### Final Chunk Count

31 chunks across 10 source documents.

---

# Sample Chunks

### Sample Chunk 1: grossberg_rmp.txt

Rate My Professors: Michael Grossberg - Computer Science, City College of New York. Student review discussing unreasonable 
workload, delayed grading, and quizzes being assigned during the final week.

### Sample Chunk 2: troeger_rmp.txt

Student review describing CSC 335 as one of the hardest courses in the curriculum, with exam averages around 20% and significant workload expectations.

### Sample Chunk 3: skeith_rmp.txt

Student review stating that Professor Skeith is tough but fair and gives significant curves that help final grades.

### Sample Chunk 4: reddit_ccny_cs.txt

Discussion of professor quality across CCNY CS courses, highlighting differences between lower-level and upper-level classes.

### Sample Chunk 5: ccny_catalog.txt

Official curriculum listing required courses including Data Structures, Algorithms, Operating Systems, Software Engineering, and Database Systems.

---

# Embedding Model

### Model Used

all-MiniLM-L6-v2 (Sentence Transformers)

### Production Tradeoff Reflection

This model was selected because it is free, lightweight, runs locally, and provides strong semantic retrieval performance for small datasets.

For a production deployment I would consider:

- Larger embedding models such as all-mpnet-base-v2 for higher retrieval accuracy.
- OpenAI text-embedding models for improved semantic understanding.
- Multilingual models because CCNY students occasionally mix English with other languages.
- Longer-context embedding models if larger documents such as syllabi are added.

The tradeoff is between accuracy, speed, memory usage, and operating cost.

---

# Retrieval Test Results

## Query 1

### Query

Michael Grossberg lectures

### Top Returned Chunks

1. grossberg_rmp.txt
2. grossberg_rmp.txt
3. rmp_ccny_general.txt

### Why Relevant

The first two chunks come directly from Grossberg reviews and discuss his teaching style, lectures, and student experiences.

---

## Query 2

### Query

Douglas Troeger exams

### Top Returned Chunks

1. troeger_rmp.txt
2. troeger_rmp.txt
3. skeith_rmp.txt

### Why Relevant

The top two chunks specifically discuss Troeger's exams, grading style, office hours, and workload.

---

## Query 3

### Query

What is the workload like for CCNY computer science courses?

### Top Returned Chunks

1. reddit_ccny_cs.txt
2. reddit_ccny_cs.txt
3. quora_ccny_cs.txt

### Why Relevant

The retrieved chunks discuss course rigor, grading expectations, workload, and student experiences throughout the CS program.

---

# Grounded Generation

## System Prompt Grounding Instruction

The model is instructed:

"Answer questions about professors, courses, and workload based ONLY on the student reviews and course information provided
below. Do not use any outside knowledge. When you use information from a source, cite it as [Source N]. If the provided
context does not contain enough information to answer the question, say exactly: 'I don't have enough information in my s
ources to answer that question.'"

The generation model is:

llama-3.3-70b-versatile via Groq.

The temperature is set to 0.2 to minimize hallucination.

## How Source Attribution Is Surfaced

Source attribution is enforced in two ways:

1. The prompt instructs the model to cite sources inline.
2. The application automatically appends a source legend showing which documents correspond to each citation.

This ensures source attribution remains visible even if the model produces an incomplete citation.

---

# Example Responses

## Example 1

### Question

Does Skeith curve his exams?

### Response

Yes. Student reviews indicate that Skeith gives significant curves that help final grades [Source 1].

Sources:
Source 1 → skeith_rmp.txt

---

## Example 2

### Question

How do I do well in Troeger's class?

### Response

Students recommend understanding all material before each midterm, attending weekend office hours, avoiding syntax 
mistakes on exams, and carefully completing homework because exam questions are often similar [Source 1][Source 2].

Sources:
Source 1, Source 2 → troeger_rmp.txt

---

## Out-of-Scope Query

### Question

What is the best pizza place in NYC?

### Response

I don't have enough information in my sources to answer that question. Try rephrasing, or ask about a specific CCNY CS professor or course.

---

# Query Interface

The system provides a Gradio web interface.

### Inputs

- Question textbox
- Example question buttons
- Retrieval inspection page

### Outputs

- Grounded answer generated from retrieved context
- Inline source citations
- Source legend mapping citations to documents
- Retrieval inspection view showing:
  - retrieved chunks
  - similarity scores
  - source filenames
  - chunk IDs
  
### Sample Interaction

User:

Does Skeith curve his exams?

System:

Yes. Student reviews indicate that Skeith gives significant curves on exams [Source 1].

Sources:
Source 1 → skeith_rmp.txt

---

# Evaluation Report

| # | Question | Expected Answer | System Response (Summarized) | Retrieval Quality | Response Accuracy |
|---|----------|----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Professor Grossberg's exams? | Reviews mention workload, grading delays, quizzes assigned late | Correctly discussed workload and grading issues but lacked exam details | Partially Relevant | Partially Accurate |
| 2 | What preparation is recommended before taking Algorithms? | Strong Data Structures background and problem solving | Correctly identified preparation recommendations | Relevant | Accurate |
| 3 | How do I do well in Troeger's class? | Understand material early, avoid syntax errors, attend office hours | Retrieved and cited all major recommendations | Relevant | Accurate |
| 4 | What workload should I expect in upper-level CS courses? | Heavy workload and professor-dependent experience | Correctly summarized student reports | Relevant | Accurate |
| 5 | What factors contribute to positive professor ratings? | Clear explanations, fair grading, organization, accessibility | Correctly identified all major factors | Relevant | Accurate |

Retrieval Quality: Relevant / Partially Relevant / Off-Target

Response Accuracy: Accurate / Partially Accurate / Inaccurate

---

# Failure Case Analysis

### Question That Failed

What do students say about Professor Grossberg's exams?

### What The System Returned

The answer focused on workload and grading delays rather than exam-specific information.

### Root Cause

This failure originated in the retrieval stage.

The Grossberg document contains relatively few reviews and very little discussion of exam structure. Meanwhile,
Troeger reviews contain many references to exams. Because the embedding model focuses on semantic similarity,
exam-related Troeger chunks were often ranked above Grossberg chunks.

### What I Would Change

I would:

- Add additional Grossberg reviews.
- Store professor names as metadata.
- Apply metadata filtering when the query explicitly names a professor.

This would improve entity-specific retrieval.

---

# Spec Reflection

### One Way the Spec Helped Me

The planning document forced me to define evaluation questions before implementation. This made it easier to identify 
retrieval failures because I already knew what the correct answer should look like.

### One Way My Implementation Diverged

My original plan used 300-word chunks with 50-word overlap. After testing on the actual corpus, this produced too few chunks and weak
retrieval performance. I reduced the chunk size to 200 words and overlap to 50 words to better match the document collection.

---

## AI Usage

### Instance 1

What I gave the AI

I described my document corpus (Rate My Professors reviews, Reddit discussions, Quora posts, and CCNY department pages) and 
explained that I needed an ingestion pipeline that could clean text, chunk documents, and prepare them for embedding.

What it produced

The AI generated an initial version of ingest.py that loaded text files, cleaned basic formatting issues, and split documents into chunks.

What I changed or overrode

After testing on my corpus, I determined that the generated chunking strategy was not appropriate for short student reviews.
I modified the implementation to use word-based chunking, experimented with different chunk sizes and overlaps, and added chunk 
validation checks to detect fragments, HTML artifacts, and boilerplate text. I also ran multiple ingestion diagnostics and 
adjusted the chunking parameters based on retrieval performance rather than simply accepting the initial implementation.

---

### Instance 2

What I gave the AI

I provided my retrieval design from planning.md, including the use of ChromaDB, the all-MiniLM-L6-v2 embedding model,
cosine similarity search, and the requirement that answers be traceable back to source documents.

What it produced

The AI generated an initial implementation of the embedding and retrieval pipeline using SentenceTransformers and ChromaDB.

What I changed or overrode

I extended the implementation by adding source metadata (source and chunk_id) to every stored chunk so responses could be 
traced back to specific documents. After evaluating retrieval quality, I observed that professor-specific queries sometimes
retrieved chunks about different professors. To improve results, I implemented professor-name score boosting and modified 
the ranking logic. I also tested retrieval using multiple evaluation queries and adjusted the system based on observed 
failures rather than relying solely on the generated code.