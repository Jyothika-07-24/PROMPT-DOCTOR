"""Prompt Doctor — Streamlit two-panel prompt engineering lab with domain-specific levels."""

import os
import base64
import streamlit as st
from levels import get_domain_names, get_domain, get_level, get_principles_text
from runner import run_prompt
from examiner import grade_prompt

# Load background image as base64
bg_path = os.path.join(os.path.dirname(__file__), "bg.png")
bg_data_uri = ""
if os.path.exists(bg_path):
    with open(bg_path, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()
        bg_data_uri = f"data:image/png;base64,{bg_b64}"

# Page config
st.set_page_config(
    page_title="Prompt Doctor",
    page_icon="\U0001FA79",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS for light theme ───────────────────────────────────────────
CSS = """
<style>
    /* Main background and text */
    .stApp {
        background: linear-gradient(rgba(245, 247, 250, 0.90), rgba(195, 207, 226, 0.90)), url('BG_PLACEHOLDER') no-repeat center center fixed;
        background-size: cover;
    }
    
    /* Title styling */
    .main-title {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 800 !important;
    }
    .main-subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Card-like containers */
    .card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.8);
    }
    .card-header {
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 0.8rem;
        color: #333;
    }
    
    /* Level badges */
    .level-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        text-align: center;
    }
    .level-active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 2px 8px rgba(102,126,234,0.4);
    }
    .level-cleared {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
    }
    .level-locked {
        background: #e8e8e8;
        color: #999;
    }
    
    /* Domain selector */
    .domain-select {
        background: white;
        border-radius: 12px;
        padding: 0.3rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        font-size: 0.95rem !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1) !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: #f8f9fa !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        color: #444 !important;
    }
    .streamlit-expanderContent {
        border: 1px solid #eee !important;
        border-radius: 0 0 10px 10px !important;
        padding: 1rem !important;
        background: #fafbfc !important;
    }
    
    /* Verdict panel */
    .verdict-pass {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 4px 15px rgba(17,153,142,0.3);
    }
    .verdict-revise {
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 4px 15px rgba(245,87,108,0.3);
    }
    .verdict-error {
        background: linear-gradient(135deg, #4facfe, #00f2fe);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3rem;
        box-shadow: 0 4px 15px rgba(79,172,254,0.3);
    }
    
    /* Principle items */
    .principle-pass {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    .principle-fail {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    
    /* Progress bar */
    .level-progress-container {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    .level-dot {
        flex: 1;
        height: 6px;
        border-radius: 3px;
        transition: all 0.3s ease;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0 !important;
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, #667eea, transparent) !important;
    }
    
    /* Code blocks */
    .stCode {
        border-radius: 10px !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
</style>
"""
st.markdown(CSS.replace("BG_PLACEHOLDER", bg_data_uri) if bg_data_uri else CSS, unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────
for key, default in [
    ("level", 1),
    ("domain", None),
    ("verdict", None),
    ("model_output", ""),
    ("submitted", False),
    ("cleared_levels", set()),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Title ────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">\U0001FA79 Prompt Doctor</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Write a prompt. Get graded by an AI examiner. Level up through 5 techniques.</div>', unsafe_allow_html=True)

# ── Left column: Editor ──────────────────────────────────────────────────
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="card"><div class="card-header">\U0001F4DD Your Prompt Lab</div>', unsafe_allow_html=True)

    # Domain dropdown selector
    domain_names = get_domain_names()
    selected_domain = st.selectbox(
        "Choose your domain",
        [""] + domain_names,
        format_func=lambda x: "Select a domain..." if x == "" else f"{x} \u2014 {get_domain(x)['description']}" if x else "",
        key="domain_selector",
    )

    if selected_domain:
        if st.session_state.domain != selected_domain:
            st.session_state.domain = selected_domain
            st.session_state.level = 1
            st.session_state.verdict = None
            st.session_state.model_output = ""
            st.session_state.submitted = False
            st.session_state.cleared_levels = set()
            st.rerun()

        domain_data = get_domain(selected_domain)

        # Domain badge
        domain_colors = {
            "Healthcare": ("#ff6b6b", "#ee5a24"),
            "Legal": ("#667eea", "#764ba2"),
            "Customer Support": ("#11998e", "#38ef7d"),
            "Education": ("#f093fb", "#f5576c"),
            "Finance": ("#4facfe", "#00f2fe"),
        }
        dc = domain_colors.get(selected_domain, ("#667eea", "#764ba2"))
        st.markdown(
            f'<div style="background: linear-gradient(135deg, {dc[0]}, {dc[1]}); color: white; '
            f'padding: 0.6rem 1rem; border-radius: 10px; margin: 0.5rem 0;">'
            f'<strong>{selected_domain}</strong> &mdash; {domain_data["base_scenario"]}</div>',
            unsafe_allow_html=True
        )

        if st.button("\U0001F504 Change Domain", use_container_width=True):
            st.session_state.domain = None
            st.session_state.verdict = None
            st.session_state.model_output = ""
            st.session_state.submitted = False
            st.session_state.cleared_levels = set()
            st.rerun()

        # Level progress bar
        st.markdown("### Level Progress")
        progress_html = '<div class="level-progress-container">'
        for i in range(1, 6):
            if i in st.session_state.cleared_levels:
                progress_html += f'<div class="level-dot" style="background: linear-gradient(135deg, #11998e, #38ef7d);"></div>'
            elif i == st.session_state.level:
                progress_html += f'<div class="level-dot" style="background: linear-gradient(135deg, #667eea, #764ba2);"></div>'
            else:
                progress_html += f'<div class="level-dot" style="background: #e0e0e0;"></div>'
        progress_html += '</div>'
        st.markdown(progress_html, unsafe_allow_html=True)

        level_cols = st.columns(5)
        level_names = {1: "Basic", 2: "Structured", 3: "Few-shot", 4: "Reasoning", 5: "Robust"}
        for i in range(1, 6):
            with level_cols[i - 1]:
                if i in st.session_state.cleared_levels:
                    st.markdown(f'<div class="level-badge level-cleared">\u2705 L{i}</div>', unsafe_allow_html=True)
                elif i == st.session_state.level:
                    st.markdown(f'<div class="level-badge level-active">L{i}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="level-badge level-locked">L{i}</div>', unsafe_allow_html=True)
                st.caption(level_names[i])

        level = st.session_state.level
        level_data = get_level(selected_domain, level)

        if level_data:
            st.markdown("---")
            
            # Level header with gradient
            level_gradients = {
                1: "linear-gradient(135deg, #667eea, #764ba2)",
                2: "linear-gradient(135deg, #f093fb, #f5576c)",
                3: "linear-gradient(135deg, #4facfe, #00f2fe)",
                4: "linear-gradient(135deg, #11998e, #38ef7d)",
                5: "linear-gradient(135deg, #fa709a, #fee140)",
            }
            lg = level_gradients.get(level, "linear-gradient(135deg, #667eea, #764ba2)")
            st.markdown(
                f'<div style="background: {lg}; color: white; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">'
                f'<div style="font-size: 1.3rem; font-weight: 700;">Level {level}: {level_data["name"]}</div>'
                f'<div style="opacity: 0.9; margin-top: 0.3rem;">{level_data["description"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.markdown(level_data["task"])

            # Sample input
            with st.expander("\U0001F4C4 Sample Input", expanded=True):
                st.text(level_data["sample_input"])

            # Output expectation
            with st.expander("\U0001F3AF Expected Output", expanded=True):
                st.info(level_data.get("output_expectation", "No specific output expectation defined."))

            # Example output
            with st.expander("\U0001F4DD Example Output", expanded=True):
                example = level_data.get("example_output", "")
                if example:
                    st.code(example, language="text")
                else:
                    st.info("No example output defined for this level.")

            # Principles being judged
            with st.expander("\U0001F4CB What the Examiner Checks", expanded=True):
                st.markdown(get_principles_text(selected_domain, level))

            # Prompt editor
            st.markdown("### \u270F\uFE0F Your Prompt")
            domain_lower = selected_domain.lower()
            prompt = st.text_area(
                "Write your prompt below. It will be run against the sample input.",
                height=250,
                placeholder=(
                    f"You are a {domain_lower} expert...\n\n"
                    f"Analyze the following input and..."
                ),
                key="prompt_editor",
            )

            # Submit and Reset buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.button("\U0001F680 Submit Prompt", type="primary", use_container_width=True)
            with col2:
                if st.button("\U0001F504 Reset Level", use_container_width=True):
                    st.session_state.verdict = None
                    st.session_state.model_output = ""
                    st.session_state.submitted = False
                    st.rerun()

            if submitted and prompt.strip():
                with st.spinner("Running your prompt against the sample input..."):
                    st.session_state.submitted = True
                    model_output = run_prompt(prompt.strip(), level_data["sample_input"])
                    st.session_state.model_output = model_output

                if model_output.startswith("ERROR"):
                    st.error(model_output)
                else:
                    with st.spinner("The Examiner is grading your prompt..."):
                        principles_text = get_principles_text(selected_domain, level)
                        verdict = grade_prompt(
                            domain_name=selected_domain,
                            level_num=level,
                            level_name=level_data["name"],
                            principles_text=principles_text,
                            output_expectation=level_data.get("output_expectation", ""),
                            example_output=level_data.get("example_output", ""),
                            student_prompt=prompt.strip(),
                            sample_input=level_data["sample_input"],
                            model_output=model_output,
                        )
                        st.session_state.verdict = verdict
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ── Right column: Verdict panel ──────────────────────────────────────────
with right:
    st.markdown('<div class="card"><div class="card-header">\U0001F50D Examiner Verdict</div>', unsafe_allow_html=True)

    if not st.session_state.submitted:
        st.info(
            "\U0001F4A1 **Ready to start?** Select a domain above, write a prompt in the left panel, "
            "and submit it. The Examiner will grade it against this level's principles."
        )
        # Show a decorative placeholder
        st.markdown(
            '<div style="text-align: center; padding: 3rem 1rem; color: #aaa;">'
            '\U0001F3AF\n\n'
            '<div style="font-size: 1.1rem; margin-top: 0.5rem;">Your verdict will appear here</div>'
            '</div>',
            unsafe_allow_html=True
        )

    elif st.session_state.verdict:
        verdict = st.session_state.verdict

        # Verdict banner
        if verdict.get("verdict") == "pass":
            st.markdown(
                '<div class="verdict-pass">\u2705 PASS \u2014 All principles satisfied!</div>',
                unsafe_allow_html=True
            )
        elif verdict.get("verdict") == "error":
            st.markdown(
                '<div class="verdict-error">\u26A0\uFE0F ERROR \u2014 Something went wrong during grading.</div>',
                unsafe_allow_html=True
            )
            if verdict.get("raw_response"):
                with st.expander("\U0001F4C4 Raw Judge Response", expanded=True):
                    st.code(verdict["raw_response"], language="text")
        else:
            st.markdown(
                '<div class="verdict-revise">\U0001F4DD REVISE \u2014 Some principles need work.</div>',
                unsafe_allow_html=True
            )

        st.markdown("### Per-Principle Check")
        principles = verdict.get("principles", [])
        for p in principles:
            passed = p.get("pass", False)
            name = p.get("name", "unknown")
            weakness = p.get("weakness", "")
            question = p.get("question", "")

            if passed:
                st.markdown(
                    f'<div class="principle-pass">'
                    f'\u2705 <strong>{p.get("label", name)}</strong> \u2014 Pass'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                fail_html = (
                    f'<div class="principle-fail">'
                    f'\u274C <strong>{p.get("label", name)}</strong> \u2014 Fail'
                )
                if weakness:
                    fail_html += f'<br><span style="color: #dc2626; font-size: 0.9rem;">\U0001F3AF Weakness: {weakness}</span>'
                if question:
                    fail_html += f'<br><span style="color: #6366f1; font-size: 0.9rem;">\u2753 Question: {question}</span>'
                fail_html += '</div>'
                st.markdown(fail_html, unsafe_allow_html=True)

        # Model output
        with st.expander("\U0001F4E4 Live Model Output", expanded=True):
            st.text(st.session_state.model_output)

        # Advance level button
        if verdict.get("verdict") == "pass":
            st.markdown(
                '<div style="background: linear-gradient(135deg, #11998e, #38ef7d); color: white; '
                'padding: 1rem; border-radius: 12px; text-align: center; font-weight: 700; font-size: 1.1rem; '
                'margin: 1rem 0;">\U0001F389 You passed this level!</div>',
                unsafe_allow_html=True
            )
            level = st.session_state.level
            if level < 5:
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("\u27A1\uFE0F Next Level", type="primary", use_container_width=True):
                        st.session_state.cleared_levels.add(level)
                        st.session_state.level = level + 1
                        st.session_state.verdict = None
                        st.session_state.model_output = ""
                        st.session_state.submitted = False
                        st.rerun()
                with col2:
                    st.button(f"\u2713 Level {level} Complete", disabled=True, use_container_width=True)
            else:
                st.balloons()
                st.markdown(
                    '<div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; '
                    'padding: 2rem; border-radius: 16px; text-align: center; margin: 1rem 0;">'
                    '<div style="font-size: 2rem; font-weight: 800;">\U0001F3C6 Congratulations!</div>'
                    f'<div style="margin-top: 0.5rem;">You\'ve completed all 5 levels of Prompt Doctor in '
                    f'<strong>{st.session_state.domain}</strong>!</div>'
                    '<div style="margin-top: 0.5rem; opacity: 0.9;">You\'ve built prompts using: role & instruction, '
                    'structured output, few-shot learning, chain-of-thought reasoning, and defensive constraints.</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

    elif st.session_state.submitted and st.session_state.model_output:
        st.info("\u23F3 Waiting for the Examiner's verdict...")
        st.markdown("### Model Output So Far")
        st.text(st.session_state.model_output)
        st.caption("The verdict should appear momentarily. If not, try submitting again.")

    else:
        st.info("Submit a prompt to see the verdict.")

    if st.session_state.verdict:
        with st.expander("\u2699\uFE0F Raw Verdict JSON", expanded=False):
            st.json(st.session_state.verdict)
    
    st.markdown('</div>', unsafe_allow_html=True)