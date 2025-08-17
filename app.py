import streamlit as st
from utils.pdf_loader import extract_pdf_sections
from services.llm import llm_call
import time

# ----------------- Session State -----------------
if "paper_text" not in st.session_state:
    st.session_state.paper_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "problem_contributions" not in st.session_state:
    st.session_state.problem_contributions = ""
if "methods_keywords" not in st.session_state:
    st.session_state.methods_keywords = ""
if "limitations" not in st.session_state:
    st.session_state.limitations = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------- Helper Functions -----------------
def run_chat_prompt(prompt_file, paper_text, user_question):
    with open(prompt_file) as f:
        template = f.read()
    prompt = template.replace("{paper_text}", paper_text[:6000])
    prompt = prompt.replace("{user_question}", user_question)
    return llm_call(prompt)

def run_prompt(prompt_file, text):
    with open(prompt_file) as f:
        template = f.read()
    prompt = template.replace("{paper_text}", text[:5000])
    return llm_call(prompt)

def is_research_paper(text):
    keywords = ["abstract", "introduction", "methodology", "results", "discussion", "conclusion", "references"]
    found = sum(1 for kw in keywords if kw.lower() in text.lower())
    return found >= 3

# ----------------- Page Config -----------------
st.set_page_config(
    page_title="ResearchMate – AI Research Companion",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- Sidebar -----------------
with st.sidebar:
    st.title("📚 ResearchMate")
    st.markdown("Your AI-powered assistant to analyze research papers quickly.")
    st.markdown("---")
    st.markdown("### 🔹 Instructions")
    st.markdown("""
    1. Upload a PDF research paper.
    2. Click 'Analyze Paper' to get a summary, methods, contributions, and limitations.
    3. Use the Q&A section to ask questions about the paper.
    4. Download sections if needed.
    """)
    st.markdown("---")
    st.markdown("### 🔹 Quick Links")
    st.markdown("- [Upload Paper](#file-upload)")
    st.markdown("- [Summary](#summary)")
    st.markdown("- [Problem & Contributions](#problem--contributions)")
    st.markdown("- [Methods & Keywords](#methods--keywords)")
    st.markdown("- [Limitations](#limitations--future-research)")
    st.markdown("- [Q&A](#ask-researchmate-about-this-paper)")

# ----------------- Header -----------------
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📚 ResearchMate</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: grey;'>Your AI-powered academic assistant for research papers</h4>", unsafe_allow_html=True)
st.markdown("---")

# ----------------- File Upload -----------------
st.markdown("## 📂 Upload Paper")
uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type=["pdf"])
if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("🚀 Analyze Paper", use_container_width=True):
        text = extract_pdf_sections("temp.pdf")

        if not is_research_paper(text):
            st.error("❌ This document is not recognized as a research paper. Please upload a valid academic paper.")
        else:
            st.session_state.paper_text = text
            progress_text = "Analyzing the paper..."
            my_bar = st.progress(0, text=progress_text)

            # Simulate progress while running prompts
            for i in range(1, 6):
                time.sleep(0.2)
                my_bar.progress(i*20, text=progress_text)

            st.session_state.summary = run_prompt("prompts/summary.txt", text)
            st.session_state.problem_contributions = run_prompt("prompts/problem_contributions.txt", text)
            st.session_state.methods_keywords = run_prompt("prompts/methods_keywords.txt", text)
            st.session_state.limitations = run_prompt("prompts/limitations.txt", text)
            st.success("✅ Analysis Complete!")

# ----------------- Display Results -----------------
if st.session_state.paper_text:
    st.markdown("## 📄 Summary")
    with st.expander("View Summary"):
        st.info(st.session_state.summary)
        st.download_button("💾 Download Summary", st.session_state.summary, "summary.txt")

    st.markdown("## 🎯 Problem & Contributions")
    with st.expander("View Problem & Contributions"):
        st.success(st.session_state.problem_contributions)
        st.download_button("💾 Download Problem & Contributions", st.session_state.problem_contributions, "problem_contributions.txt")

    st.markdown("## 🛠 Methods & Keywords")
    with st.expander("View Methods & Keywords"):
        st.warning(st.session_state.methods_keywords)
        st.download_button("💾 Download Methods & Keywords", st.session_state.methods_keywords, "methods_keywords.txt")

    st.markdown("## ⚠️ Limitations & Future Research")
    with st.expander("View Limitations & Future Research"):
        st.error(st.session_state.limitations)
        st.download_button("💾 Download Limitations", st.session_state.limitations, "limitations.txt")

    # Collapsible Q&A section
    st.markdown("## 💬 Ask ResearchMate about this paper")
    with st.expander("Open Q&A"):
        user_q = st.text_input("Type your question:", key="qa_input")
        if st.button("Ask", key="ask_button"):
            if user_q.strip():
                with st.spinner("Thinking..."):
                    chat_answer = run_chat_prompt("prompts/chat_mode.txt", st.session_state.paper_text, user_q)
                st.session_state.chat_history.append((user_q, chat_answer))
            else:
                st.warning("Please enter a question.")

       # Display chat history in chat-bubble style with better visibility
for q, a in reversed(st.session_state.chat_history):
    st.markdown(
        f"""
        <div style='background-color:#116466; color:white; padding:12px; border-radius:12px; margin-bottom:5px;'>
            <b>Q:</b> {q}
        </div>
        """, unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style='background-color:#FF6B6B; color:white; padding:12px; border-radius:12px; margin-bottom:10px;'>
            <b>A:</b> {a}
        </div>
        """, unsafe_allow_html=True
    )
