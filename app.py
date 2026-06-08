"""
app.py — Gradio Interface for CCNY CS Unofficial Guide
"""

import gradio as gr
from generate import answer
from retrieve import retrieve


def ask(question):
    if not question.strip():
        return "", ""
    full = answer(question, verbose=False)
    if "── Sources" in full:
        parts = full.split("── Sources", 1)
        ans = parts[0].strip()
        src = parts[1].strip()
    else:
        ans = full
        src = ""
    return ans, src


def debug_chunks(question):
    if not question.strip():
        return ""
    chunks = retrieve(question)
    lines = []
    for i, c in enumerate(chunks, 1):
        lines.append(
            f"#{i}  score={c['score']:.4f}  ·  {c['source']}  ·  chunk {c['chunk_id']}\n"
            f"{c['text'][:300]}...\n"
        )
    return ("\n" + "─" * 56 + "\n").join(lines)


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Sora:wght@400;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg:       #0d0d0f;
    --surface:  #141417;
    --elevated: #1c1c21;
    --border:   rgba(255,255,255,0.07);
    --border2:  rgba(255,255,255,0.12);
    --text:     #e8e8f0;
    --muted:    #6e6e85;
    --accent:   #7c6af5;
    --accent2:  #5eead4;
    --danger:   #f97316;
    --glow:     rgba(124,106,245,0.15);
}

body, .gradio-container, .gradio-container * {
    font-family: 'Inter', sans-serif !important;
    background: transparent;
}

.gradio-container {
    background: var(--bg) !important;
    min-height: 100vh;
}

/* ── Header ── */
.site-header {
    padding: 56px 40px 48px;
    text-align: center;
    position: relative;
}
.site-header::after {
    content: '';
    display: block;
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border2), transparent);
    margin-top: 48px;
}
.pill {
    display: inline-block;
    background: rgba(124,106,245,0.12);
    border: 1px solid rgba(124,106,245,0.3);
    color: #a89ff8;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 999px;
    margin-bottom: 22px;
}
.site-header h1 {
    font-family: 'Sora', sans-serif !important;
    font-size: clamp(2rem, 5vw, 3.2rem) !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    line-height: 1.1 !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 14px !important;
}
.site-header h1 .grad {
    background: linear-gradient(135deg, #7c6af5, #5eead4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.site-header p {
    color: var(--muted) !important;
    font-size: 0.95rem !important;
    font-weight: 300 !important;
    letter-spacing: 0.01em !important;
}

/* ── Tabs ── */
.tab-nav {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0 40px !important;
    gap: 0 !important;
}
.tab-nav button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 14px 20px !important;
    transition: color 0.2s, border-color 0.2s !important;
    margin-bottom: -1px !important;
}
.tab-nav button:hover { color: var(--text) !important; }
.tab-nav button.selected {
    color: var(--text) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Tab panels ── */
.tabitem { padding: 36px 40px !important; }

/* ── Labels ── */
label > span {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin-bottom: 8px !important;
    display: block;
}

/* ── Textareas & inputs ── */
textarea, input[type="text"] {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 400 !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    caret-color: var(--accent) !important;
    resize: none !important;
}
textarea:focus, input[type="text"]:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
    outline: none !important;
}
textarea::placeholder, input::placeholder {
    color: var(--muted) !important;
    opacity: 0.6 !important;
}

/* ── Button ── */
.ask-btn button, button.primary {
    background: linear-gradient(135deg, var(--accent), #6057d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 14px 28px !important;
    height: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 4px 20px rgba(124,106,245,0.3) !important;
}
.ask-btn button:hover, button.primary:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.ask-btn button:active, button.primary:active {
    transform: translateY(0) !important;
}

/* ── Answer output ── */
.answer-box textarea {
    background: var(--elevated) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 12px !important;
    font-size: 0.96rem !important;
    line-height: 1.75 !important;
    color: var(--text) !important;
    padding: 22px !important;
}

/* ── Sources badge ── */
.sources-box textarea {
    background: rgba(94,234,212,0.04) !important;
    border: 1px solid rgba(94,234,212,0.15) !important;
    border-radius: 10px !important;
    font-family: 'SF Mono', 'Fira Code', monospace !important;
    font-size: 0.78rem !important;
    color: #5eead4 !important;
    line-height: 1.6 !important;
    padding: 14px 18px !important;
}

/* ── Examples ── */
.examples-wrap .label {
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin-bottom: 10px !important;
}
table.gr-samples-table {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    width: 100% !important;
    border-collapse: collapse !important;
}
table.gr-samples-table td {
    font-size: 0.87rem !important;
    color: var(--muted) !important;
    padding: 11px 16px !important;
    border-bottom: 1px solid var(--border) !important;
    cursor: pointer !important;
    transition: background 0.15s, color 0.15s !important;
}
table.gr-samples-table tr:last-child td { border-bottom: none !important; }
table.gr-samples-table tr:hover td {
    background: var(--elevated) !important;
    color: var(--text) !important;
}

/* ── Debug ── */
.debug-box textarea {
    font-family: 'SF Mono', 'Fira Code', monospace !important;
    font-size: 0.78rem !important;
    line-height: 1.65 !important;
    color: var(--muted) !important;
    background: var(--surface) !important;
}

/* ── Footer ── */
.site-footer {
    text-align: center;
    padding: 28px 40px 40px;
    font-size: 0.75rem;
    color: var(--muted);
    border-top: 1px solid var(--border);
    letter-spacing: 0.03em;
    margin-top: 8px;
}
.site-footer a { color: var(--accent); text-decoration: none; }
"""


with gr.Blocks(css=CSS, title="CCNY CS — The Unofficial Guide") as demo:

    gr.HTML("""
    <div class="site-header">
        <div class="pill">CCNY Computer Science</div>
        <h1>The <span class="grad">Unofficial</span> Guide</h1>
        <p>Ask anything about professors, courses, and workload. Answers grounded in real student reviews.</p>
    </div>
    """)

    with gr.Tabs():

        with gr.Tab("Ask"):
            with gr.Row(equal_height=True):
                with gr.Column(scale=5):
                    q_input = gr.Textbox(
                        label="Your question",
                        placeholder="e.g. How do I do well in Troeger's class?",
                        lines=2,
                    )
                with gr.Column(scale=1, min_width=130, elem_classes=["ask-btn"]):
                    ask_btn = gr.Button("Ask →", variant="primary")

            ans_out = gr.Textbox(
                label="Answer",
                lines=10,
                interactive=False,
                elem_classes=["answer-box"],
            )
            src_out = gr.Textbox(
                label="Sources",
                lines=3,
                interactive=False,
                elem_classes=["sources-box"],
            )

            gr.Examples(
                examples=[
                    ["What do students say about Professor Grossberg's exams?"],
                    ["How do I do well in Troeger's class?"],
                    ["Does Skeith curve his exams?"],
                    ["What workload should I expect in upper-level CS courses?"],
                    ["What preparation is recommended before taking Algorithms?"],
                ],
                inputs=q_input,
                label="Try an example",
            )

            ask_btn.click(ask, inputs=q_input, outputs=[ans_out, src_out])
            q_input.submit(ask, inputs=q_input, outputs=[ans_out, src_out])

        with gr.Tab("Inspect Retrieval"):
            gr.Markdown("See the raw chunks retrieved for any query.")
            dbg_input = gr.Textbox(
                label="Query",
                placeholder="Enter any question...",
                lines=2,
            )
            dbg_btn = gr.Button("Retrieve →", variant="primary")
            dbg_out = gr.Textbox(
                label="Retrieved chunks — top 5",
                lines=22,
                interactive=False,
                elem_classes=["debug-box"],
            )
            dbg_btn.click(debug_chunks, inputs=dbg_input, outputs=dbg_out)
            dbg_input.submit(debug_chunks, inputs=dbg_input, outputs=dbg_out)

    gr.HTML("""
    <div class="site-footer">
        Answers are grounded in student reviews only &nbsp;·&nbsp; Not affiliated with CCNY
    </div>
    """)

demo.launch()