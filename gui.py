import streamlit as st
import json
import os
from pathlib import Path
import sys
from datetime import datetime

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generation_pipeline.pipeline import GenerationPipeline
from validation_pipeline.pipeline import ValidationPipeline
from generation_pipeline.utils.review_parser import ReviewParser
from generation_pipeline.utils.file_modifier import FileModifier

st.set_page_config(
    page_title="HS-Bench Pipeline Control Center",
    page_icon="🧬",
    layout="wide"
)

# --- Session State Initialization ---
if "study_id" not in st.session_state:
    st.session_state.study_id = ""
if "paper_id" not in st.session_state:
    st.session_state.paper_id = ""
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
if "stage1_json" not in st.session_state:
    st.session_state.stage1_json = None
if "stage2_json" not in st.session_state:
    st.session_state.stage2_json = None

# --- Helpers ---
def get_pdf_files():
    pdfs = list(Path(".").glob("*.pdf"))
    for study_dir in Path("data/studies").glob("study_*"):
        pdfs.extend(list(study_dir.glob("*.pdf")))
    # Also include data/uploads if it exists
    upload_dir = Path("data/uploads")
    if upload_dir.exists():
        pdfs.extend(list(upload_dir.glob("*.pdf")))
    return sorted(list(set(pdfs)))

def get_study_ids():
    studies = [d.name for d in Path("data/studies").glob("study_*") if d.is_dir()]
    return sorted(studies)

# --- Sidebar ---
st.sidebar.title("🧬 HS-Bench Control")
mode = st.sidebar.radio("Select Mode", ["Generation Pipeline", "Validation Pipeline"])

# Initialize Pipelines
gen_pipeline = GenerationPipeline()
val_pipeline = ValidationPipeline()
file_modifier = FileModifier()

if mode == "Generation Pipeline":
    st.title("🚀 Generation Pipeline")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Input Configuration")
        
        # PDF Upload Section
        uploaded_file = st.file_uploader("Upload Paper PDF", type=['pdf'])
        if uploaded_file is not None:
            upload_dir = Path("data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
            save_path = upload_dir / uploaded_file.name
            if not save_path.exists():
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Uploaded: {uploaded_file.name}")
                st.rerun()

        pdf_options = get_pdf_files()
        selected_pdf = st.selectbox("Select Paper PDF", options=pdf_options, format_func=lambda x: x.name)
        st.session_state.pdf_path = selected_pdf
        
        study_id_input = st.text_input("Target Study ID (e.g., study_005)", value=st.session_state.study_id)
        if study_id_input:
            st.session_state.study_id = study_id_input

    # Tabs for Stages
    tab1, tab2, tab3 = st.tabs(["Stage 1: Filter", "Stage 2: Extraction", "Stage 3: Generation"])
    
    with tab1:
        st.header("Stage 1: Replicability Filter")
        if st.button("Run Stage 1 Analysis"):
            with st.spinner("Running Stage 1..."):
                md_path, json_path, result = gen_pipeline.run_stage1(st.session_state.pdf_path)
                st.session_state.paper_id = result.get('paper_id', '')
                st.session_state.stage1_json = json_path
                st.success(f"Stage 1 Complete: {json_path.name}")
        
        # Display Stage 1 Results if they exist
        if st.session_state.paper_id:
            paper_id = st.session_state.paper_id
            md_file = Path(f"generation_pipeline/outputs/{paper_id}_stage1_filter.md")
            json_file = Path(f"generation_pipeline/outputs/{paper_id}_stage1_filter.json")
            
            if md_file.exists() and json_file.exists():
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Review (Markdown)")
                    content = md_file.read_text(encoding='utf-8')
                    
                    # Markdown Rendering Preview
                    with st.expander("👁️ Preview Rendered Markdown", expanded=True):
                        st.markdown(content)
                        
                    # Editable text area for refinement
                    edited_md = st.text_area("Edit Review for Refinement", value=content, height=400)
                    if edited_md != content:
                        md_file.write_text(edited_md, encoding='utf-8')
                    
                    if st.button("Refine Stage 1"):
                        with st.spinner("Refining Stage 1..."):
                            gen_pipeline.run_stage1(st.session_state.pdf_path)
                            st.rerun()
                            
                with c2:
                    st.markdown("### Data (JSON)")
                    st.json(json.loads(json_file.read_text(encoding='utf-8')))

    with tab2:
        st.header("Stage 2: Study Data Extraction")
        # Find latest stage1 json if not in state
        if not st.session_state.stage1_json and st.session_state.paper_id:
            p = Path(f"generation_pipeline/outputs/{st.session_state.paper_id}_stage1_filter.json")
            if p.exists(): st.session_state.stage1_json = p

        if st.button("Run Stage 2 Extraction", disabled=not st.session_state.stage1_json):
            with st.spinner("Running Stage 2..."):
                md_path, json_path, result = gen_pipeline.run_stage2(st.session_state.stage1_json, st.session_state.pdf_path)
                st.session_state.stage2_json = json_path
                st.success(f"Stage 2 Complete: {json_path.name}")

        if st.session_state.paper_id:
            paper_id = st.session_state.paper_id
            md_file = Path(f"generation_pipeline/outputs/{paper_id}_stage2_extraction.md")
            json_file = Path(f"generation_pipeline/outputs/{paper_id}_stage2_extraction.json")
            
            if md_file.exists() and json_file.exists():
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Review (Markdown)")
                    content = md_file.read_text(encoding='utf-8')
                    
                    # Markdown Rendering Preview
                    with st.expander("👁️ Preview Rendered Markdown", expanded=True):
                        st.markdown(content)
                        
                    edited_md = st.text_area("Edit Stage 2 Review", value=content, height=400, key="stage2_md")
                    if edited_md != content:
                        md_file.write_text(edited_md, encoding='utf-8')
                    
                    if st.button("Refine Stage 2"):
                        with st.spinner("Refining Stage 2..."):
                            gen_pipeline.run_stage2(st.session_state.stage1_json, st.session_state.pdf_path)
                            st.rerun()
                with c2:
                    st.markdown("### Data (JSON)")
                    st.json(json.loads(json_file.read_text(encoding='utf-8')))

    with tab3:
        st.header("Stage 3: Study File Generation")
        if not st.session_state.stage2_json and st.session_state.paper_id:
            p = Path(f"generation_pipeline/outputs/{st.session_state.paper_id}_stage2_extraction.json")
            if p.exists(): st.session_state.stage2_json = p

        if st.button("Generate Study Files", disabled=not (st.session_state.stage2_json and st.session_state.study_id)):
            with st.spinner("Generating files..."):
                result = gen_pipeline.generate_study(st.session_state.stage2_json, st.session_state.study_id)
                st.success(f"Study {st.session_state.study_id} generated successfully!")
                st.write(result)

    # Quick Edit Helper
    with st.expander("🛠️ Quick File Modifier"):
        st.info("Use this to fix specific fields in the JSON files using LLM.")
        target_file = st.selectbox("Select File to Modify", 
                                  options=[st.session_state.stage1_json, st.session_state.stage2_json],
                                  format_func=lambda x: x.name if x else "None")
        context = st.text_area("What should be changed?", placeholder="e.g. The participant count for Study 1 should be 120, not 100.")
        if st.button("Apply Modification"):
            if target_file and context:
                with st.spinner("Modifying file..."):
                    file_modifier.modify_files(
                        file_paths=[target_file],
                        context=context,
                        apply_changes=True,
                        pdf_path=st.session_state.pdf_path
                    )
                    st.success("File modified successfully!")
                    st.rerun()

else:
    st.title("✅ Validation Pipeline")
    
    study_list = get_study_ids()
    selected_study = st.selectbox("Select Study to Validate", options=study_list)
    
    if st.button("Run Full Validation"):
        with st.spinner(f"Validating {selected_study}..."):
            results = val_pipeline.validate_study(selected_study)
            st.success("Validation Complete!")
            
            # Find the latest summary file
            summary_files = list(Path("validation_pipeline/outputs").glob(f"{selected_study}_validation_summary_*.md"))
            if summary_files:
                latest_summary = max(summary_files, key=os.path.getmtime)
                st.markdown("---")
                st.markdown(latest_summary.read_text(encoding='utf-8'))

