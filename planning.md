# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

CCNY Computer Science Professor Reviews and Course Advice

This project focuses on student-generated reviews and discussions 
about CCNY computer science professors and courses. While official 
course descriptions explain what a course covers, they often do not 
provide information about teaching style, workload, grading policies, 
exam difficulty, or student experiences. The goal is to make this 
unofficial knowledge searchable so students can make more informed 
academic decisions.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description                                                                         | URL or location                                                                                 |
|---|--------|-------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| 1 | Reddit | How is CCNY when it comes to CS?                                                    | https://www.reddit.com/r/CCNY/comments/1fdtv3f/how_is_city_college_when_it_comes_to_computer/                          |
| 2 | Quora  | Does CCNY have a good CS program?                                                   | https://www.quora.com/Does-The-City-College-of-New-York-CCNY-have-a-good-computer-science-program-for-undergraduates |
| 3 | CCNY   | CCNY CS Research                                       v                            | https://www.ccny.cuny.edu/compsci/research?srsltid=AfmBOoqUmFRGYedfufFAEt4HYj4jqxwBVnV4OJqSMr2Z8I7jvAeZ0ykl                             |
| 4 | Reddit | What is CCNY really like in terms of professors, classes, course load, and grading? | https://www.reddit.com/r/CCNY/comments/1l47u0u/what_is_ccny_really_like_in_terms_of_professors/ |
| 5 | Reddit | Is City College (CCNY) seriously that bad?                                          |  https://www.reddit.com/r/CUNY/comments/1b501o0/is_city_college_ccny_seriously_that_bad/                                                                                               |
| 6 | RMP    | Michael Grossberg CCNY                                                              |  https://www.ratemyprofessors.com/professor/854471                                                                                               |
| 7 | RMP    | Douglas Troeger CCNY                                                                |   https://www.ratemyprofessors.com/professor/432142                                                                                          |
| 8 | RMP    | CCNY Professors                                                                     |  https://www.ratemyprofessors.com/school/224                                                                                               |
| 9 | RMP    | William Skeith                                                                      |  https://www.ratemyprofessors.com/professor/1316015                                                                                             |
| 10 | CCNY   | CCNY Computer Science Catalog                                                       |  https://ccny-undergraduate.catalog.cuny.edu/programs/CMPSC-BS                                                                                               |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size: 300 words**

**Overlap: 50**

**Reasoning: Most documents consist of short student reviews and discussion posts. Smaller
    chunks help preserve specific opinions about professors, grading, exams, and workload
    while overlap prevents information from being lost across chunk boundaries.**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:all-MiniLM-L6-v2**

**Top-k: 5**

**Production tradeoff reflection: For a production system I would consider larger 
    embedding models that provide higher retrieval accuracy and better support for longer 
    contexts or multiple languages. However, they may increase latency and computational cost.**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question                                                                                                  | Expected answer |
|---|-----------------------------------------------------------------------------------------------------------|-----------------|
| 1 | What do students say about Professor Grossberg’s exams?                                                   |Reviews commonly describe his exams as challenging but fair and emphasize understanding concepts rather than memorization. |
| 2 | According to student discussions, what preparation is recommended before taking Algorithms at CCNY?       |Students recommend having a strong understanding of data structures and consistent problem-solving practice before taking Algorithms. |
| 3 | How to do well in Troeger's or Gertner's class?                                                           |Students frequently recommend staying on top of coursework, reviewing lecture material regularly, and seeking clarification early when concepts become difficult. |
| 4 | What workload concerns do students mention most frequently when discussing CCNY computer science courses? |Students frequently mention heavy workloads, difficult assignments,

challenging exams, and significant time commitments in upper-level

computer science courses. |
| 5 | Based on student reviews, what factors contribute most to a professor receiving positive ratings?         |Positive ratings are commonly associated with clear explanations, fair grading, organized lectures, and helpful feedback. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.    Student reviews may contain conflicting opinions about the same professor or course. 
      One student may describe a professor as helpful while another may describe the same
      professor as difficult, making it challenging to generate balanced answers.

2.     Retrieval may return irrelevant or incomplete chunks because discussions often 
       cover multiple topics in the same post. Important information about a professor or 
       course could be split across chunk boundaries, causing the system to miss relevant 
       context.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
