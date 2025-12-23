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

def infer_study_id(pdf_path: Path):
    if not pdf_path: return ""
    # Check if PDF is already in a study directory
    path_str = str(pdf_path.absolute())
    if "data/studies/" in path_str:
        parts = pdf_path.parts
        for p in parts:
            if p.startswith("study_"):
                return p
    return ""

def get_study_files(study_id):
    if not study_id:
        return []
    study_dir = Path("data/studies") / study_id
    if not study_dir.exists():
        return []
    # Get all files recursively, but filter out some if needed
    files = list(study_dir.rglob("*"))
    return sorted([f for f in files if f.is_file()])

# --- Sidebar ---
st.sidebar.title("🧬 HS-Bench Control")
mode = st.sidebar.radio("Select Mode", ["Generation Pipeline", "Validation Pipeline"])

def infer_paper_id(pdf_path: Path):
    if not pdf_path: return ""
    return pdf_path.stem.replace(' ', '_').replace('-', '_').lower()

# Initialize Pipelines
gen_pipeline = GenerationPipeline()
val_pipeline = ValidationPipeline()
file_modifier = FileModifier()

if mode == "Generation Pipeline":
    st.title("🚀 Generation Pipeline")
    
    # Auto-set paper_id if pdf_path is set
    if st.session_state.pdf_path:
        st.session_state.paper_id = infer_paper_id(st.session_state.pdf_path)
    
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
        # Find index of current pdf_path if it exists
        pdf_index = 0
        if st.session_state.pdf_path in pdf_options:
            pdf_index = pdf_options.index(st.session_state.pdf_path)
            
        selected_pdf = st.selectbox("Select Paper PDF", options=pdf_options, index=pdf_index, format_func=lambda x: x.name)
        
        if selected_pdf != st.session_state.pdf_path:
            st.session_state.pdf_path = selected_pdf
            # Auto-infer study_id when PDF changes
            inferred = infer_study_id(selected_pdf)
            if inferred:
                st.session_state.study_id = inferred
            st.rerun()
        
        # Study ID Selection
        st.markdown("---")
        existing_studies = ["NEW STUDY"] + get_study_ids()
        
        # Try to find current study_id in the list
        study_index = 0
        if st.session_state.study_id in existing_studies:
            study_index = existing_studies.index(st.session_state.study_id)
            
        selected_study_dropdown = st.selectbox("Load Existing Study or Create New", options=existing_studies, index=study_index)
        
        if selected_study_dropdown == "NEW STUDY":
            study_id_input = st.text_input("New Study ID (e.g., study_005)", value=st.session_state.study_id if st.session_state.study_id.startswith("study_") else "")
            if study_id_input != st.session_state.study_id:
                st.session_state.study_id = study_id_input
        else:
            if selected_study_dropdown != st.session_state.study_id:
                st.session_state.study_id = selected_study_dropdown
                st.rerun()

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
                st.markdown("---")
                # 3-column layout for Stage 1
                c1, c2, c3 = st.columns([1, 1, 1])
                
                with c1:
                    st.markdown("### 📝 Edit Review (MD)")
                    content = md_file.read_text(encoding='utf-8')
                    edited_md = st.text_area("Markdown Editor", value=content, height=600, key="stage1_md_editor")
                    if edited_md != content:
                        md_file.write_text(edited_md, encoding='utf-8')
                        st.rerun()
                    
                    if st.button("Refine Stage 1 with Comments"):
                        with st.spinner("Refining Stage 1..."):
                            gen_pipeline.run_stage1(st.session_state.pdf_path)
                            st.rerun()
                            
                with c2:
                    st.markdown("### 👁️ Preview Review")
                    st.markdown(md_file.read_text(encoding='utf-8'))
                    
                with c3:
                    st.markdown("### 🔢 Edit Data (JSON)")
                    json_content = json_file.read_text(encoding='utf-8')
                    # Use text_area for raw JSON editing
                    edited_json_str = st.text_area("JSON Editor", value=json_content, height=600, key="stage1_json_editor")
                    if st.button("Save JSON Changes", key="save_stage1_json"):
                        try:
                            # Validate JSON before saving
                            json_obj = json.loads(edited_json_str)
                            json_file.write_text(json.dumps(json_obj, indent=2, ensure_ascii=False), encoding='utf-8')
                            st.success("JSON saved!")
                        except json.JSONDecodeError as e:
                            st.error(f"Invalid JSON: {e}")
                    
                    st.markdown("#### Visual Data Tree")
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
                st.markdown("---")
                # 3-column layout for Stage 2
                c1, c2, c3 = st.columns([1, 1, 1])
                
                with c1:
                    st.markdown("### 📝 Edit Extraction (MD)")
                    content = md_file.read_text(encoding='utf-8')
                    edited_md = st.text_area("Markdown Editor", value=content, height=600, key="stage2_md_editor")
                    if edited_md != content:
                        md_file.write_text(edited_md, encoding='utf-8')
                        st.rerun()
                    
                    if st.button("Refine Stage 2 with Comments"):
                        with st.spinner("Refining Stage 2..."):
                            gen_pipeline.run_stage2(st.session_state.stage1_json, st.session_state.pdf_path)
                            st.rerun()
                            
                with c2:
                    st.markdown("### 👁️ Preview Extraction")
                    st.markdown(md_file.read_text(encoding='utf-8'))
                    
                with c3:
                    st.markdown("### 🔢 Edit Data (JSON)")
                    json_content = json_file.read_text(encoding='utf-8')
                    edited_json_str = st.text_area("JSON Editor", value=json_content, height=600, key="stage2_json_editor")
                    if st.button("Save JSON Changes", key="save_stage2_json"):
                        try:
                            json_obj = json.loads(edited_json_str)
                            json_file.write_text(json.dumps(json_obj, indent=2, ensure_ascii=False), encoding='utf-8')
                            st.success("JSON saved!")
                        except json.JSONDecodeError as e:
                            st.error(f"Invalid JSON: {e}")
                    
                    st.markdown("#### Visual Data Tree")
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

else:
    st.title("✅ Validation Pipeline")
    
    study_list = get_study_ids()
    selected_study = st.selectbox("Select Study to Validate", options=study_list)
    
    if st.button("Run Full Validation"):
        with st.spinner(f"Validating {selected_study}..."):
            # Update session state for the quick modifier
            st.session_state.study_id = selected_study
            results = val_pipeline.validate_study(selected_study)
            st.success("Validation Complete!")
            
            # Find the latest summary file
            summary_files = list(Path("validation_pipeline/outputs").glob(f"{selected_study}_validation_summary_*.md"))
            if summary_files:
                latest_summary = max(summary_files, key=os.path.getmtime)
                st.markdown("---")
                st.markdown(latest_summary.read_text(encoding='utf-8'))

# --- Quick Edit Helper (Always Available) ---
st.markdown("---")
with st.expander("🛠️ Quick File Modifier"):
    st.info("Use this to fix specific fields in the JSON or text files using LLM.")
    
    # Collect available files to modify
    modifier_options = []
    
    # 1. Add current stage files
    if st.session_state.stage1_json:
        modifier_options.append(st.session_state.stage1_json)
    if st.session_state.stage2_json:
        modifier_options.append(st.session_state.stage2_json)
        
    # 2. Add files from the selected study
    current_study = st.session_state.study_id
    if current_study:
        study_files = get_study_files(current_study)
        for f in study_files:
            if f not in modifier_options:
                modifier_options.append(f)
    
    target_file = st.selectbox("Select File to Modify", 
                              options=modifier_options,
                              format_func=lambda x: str(x),
                              key="quick_modifier_selectbox")
    context = st.text_area("What should be changed?", placeholder="e.g. The participant count for Study 1 should be 120, not 100.", key="quick_modifier_context")
    if st.button("Apply Modification", key="quick_modifier_button"):
        if target_file and context:
            with st.spinner(f"Modifying {target_file}..."):
                file_modifier.modify_files(
                    file_paths=[target_file],
                    context=context,
                    apply_changes=True,
                    pdf_path=st.session_state.pdf_path
                )
                st.success("File modified successfully!")
                st.rerun()
