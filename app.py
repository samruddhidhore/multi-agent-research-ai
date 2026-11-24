import os
import sys
import html
import time
from pathlib import Path
import streamlit as st

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import validate_environment, REPORTS_DIR
from research_pipeline import fast_research

st.set_page_config(
    page_title="ResearchMate - Academic Research Engine",
    layout="centered"
)

# Formal Academic Document Styling (Zero Emojis, Professional Typography)
st.markdown("""
<style>
    .paper-sheet {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 4px;
        padding: 36px 40px;
        font-family: "Georgia", "Times New Roman", serif;
        font-size: 1.05rem;
        line-height: 1.8;
        color: #1e293b;
        white-space: pre-wrap;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .metrics-bar {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px 18px;
        margin-bottom: 15px;
        font-family: Arial, sans-serif;
        font-size: 0.95rem;
        color: #334155;
    }
    .stButton button {
        font-weight: 600;
        border-radius: 4px;
        height: 46px;
    }
</style>
""", unsafe_allow_html=True)

# Minimal Sidebar
with st.sidebar:
    st.subheader("System Status")
    env_status = validate_environment()

    if env_status["gemini"] and env_status["tavily"]:
        st.success("APIs Connected and Active")
    else:
        st.error("API Keys Missing in .env")

    st.markdown("---")
    st.subheader("Research Scope")
    papers_count = st.slider(
        "Number of Research Papers to Review:",
        min_value=3,
        max_value=6,
        value=5,
        step=1,
        help="Target number of academic studies and journal publications to synthesize."
    )

    st.caption("Target Document Length: 3 to 4 Full Pages (~2,000+ words)")

    st.markdown("---")
    st.subheader("Archived Papers")
    saved_reports = sorted(
        list(REPORTS_DIR.glob("*.txt")) + [f for f in REPORTS_DIR.glob("*.md") if f.name != "research_report.txt"],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    if saved_reports:
        selected_report = st.selectbox(
            "Open archived paper:",
            options=["None"] + [p.name for p in saved_reports],
            index=0
        )
    else:
        st.caption("No archived papers.")
        selected_report = "None"


# Header
st.title("ResearchMate")
st.caption("Academic Literature Review and Systematic Research Paper Engine")

# View previous paper if selected
if selected_report != "None":
    report_file = REPORTS_DIR / selected_report
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            saved_text = f.read()

        words = len(saved_text.split())
        est_pages = max(1, round(words / 550, 1))

        st.info(f"Viewing: {selected_report}")
        st.markdown(
            f'<div class="metrics-bar">Document Length: {words} words | Estimated Pages: ~{est_pages} pages | Source File: {selected_report}</div>',
            unsafe_allow_html=True
        )
        st.markdown(f'<div class="paper-sheet">{html.escape(saved_text)}</div>', unsafe_allow_html=True)
        st.download_button(
            label="Download This Research Paper (.txt)",
            data=saved_text,
            file_name=selected_report.replace(".md", ".txt"),
            mime="text/plain",
            use_container_width=True
        )
        st.markdown("---")

# Topic Input
topic = st.text_input(
    "Research Topic / Inquiry:",
    placeholder="e.g. Quantum Machine Learning Algorithms 2026, Post-Quantum Cryptography...",
    label_visibility="visible"
)

start_clicked = st.button("Generate Academic Research Paper", type="primary", use_container_width=True)

# Run research
if start_clicked:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    elif not env_status["gemini"] or not env_status["tavily"]:
        st.error("API keys missing. Please verify GEMINI_API_KEY and TAVILY_API_KEY in .env.")
    else:
        search_topic = topic.strip()
        t0 = time.time()

        status_box = st.status(
            f"Conducting systematic literature review across {papers_count} research papers...",
            expanded=True
        )

        try:
            status_box.write(f"Retrieving and parsing peer-reviewed publications for: {search_topic}")
            res = fast_research(search_topic, max_sources=papers_count)

            if not res["success"]:
                status_box.update(label="Literature Review Failed", state="error", expanded=True)
                st.error(res["error"])
            else:
                elapsed = res["duration"]
                sources = res["sources"]
                report_text = res["report"]
                words = len(report_text.split())
                est_pages = max(1, round(words / 550, 1))

                status_box.update(
                    label=f"Synthesis Complete: {len(sources)} research papers analyzed in {elapsed:.1f}s",
                    state="complete",
                    expanded=False
                )

                # Summary Statistics Bar
                st.markdown(
                    f'<div class="metrics-bar"><b>Research Volume:</b> {words} words | <b>Document Length:</b> ~{est_pages} full pages | <b>Papers Synthesized:</b> {len(sources)} published studies | <b>Execution Time:</b> {elapsed:.1f}s</div>',
                    unsafe_allow_html=True
                )

                # Formal Academic Paper Sheet
                st.subheader("Academic Research Paper")
                st.markdown(f'<div class="paper-sheet">{html.escape(report_text)}</div>', unsafe_allow_html=True)

                # Download Button
                st.download_button(
                    label="Download Complete Research Paper (.txt)",
                    data=report_text,
                    file_name=f"academic_paper_{int(time.time())}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                # Bibliographic Sources Accordion
                if sources:
                    with st.expander(f"Bibliographic Sources and Paper Excerpts ({len(sources)} Studies)"):
                        for s in sources:
                            idx = s.get("index", 1)
                            title = s.get("title", "Research Study")
                            url = s.get("url", "#")
                            content = s.get("content", "")
                            st.write(f"**Study #{idx}: {title}**")
                            st.write(f"URL: {url}")
                            st.caption(content[:450] + "...")
                            st.write("---")

        except Exception as e:
            status_box.update(label="System Error", state="error", expanded=True)
            st.error(f"Error during literature synthesis: {e}")
