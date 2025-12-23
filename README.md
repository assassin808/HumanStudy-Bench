# HS-Bench Control Center 🧬

HS-Bench is a semi-automated pipeline for converting psychological research papers (PDFs) into replicable LLM-based benchmarks.

## 🚀 Quick Start (GUI)

The easiest way to use the pipeline is via the Streamlit GUI.

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set Gemini API Key
export GOOGLE_API_KEY="your-api-key"
```

### 2. Launch GUI
```bash
streamlit run gui.py
```

### 3. Workflow in GUI
1. **Upload PDF**: Use the sidebar/uploader to add your paper.
2. **Generation Pipeline**: 
   - **Stage 1 (Filter)**: Identify replicable experiments. Review MD/JSON.
   - **Stage 2 (Extraction)**: Extract materials and statistics. Review and manually fix JSON if needed.
   - **Stage 3 (Generation)**: Produce final study files in `data/studies/`.
3. **Validation Pipeline**: Run automated agents to verify the study against the original paper.
4. **Quick Fix**: Use the "Quick File Modifier" at the bottom to correct any file using natural language.

---

## 💻 CLI Usage (Advanced)

If you prefer the command line:

### Generation
```bash
# Stage 1: Filter
python generation_pipeline/run.py --stage 1 --study-id study_005

# Stage 2: Extraction (uses latest Stage 1 JSON)
python generation_pipeline/run.py --stage 2 --study-id study_005

# Stage 3: File Generation
python generation_pipeline/run.py --stage 3 --study-id study_005
```

### Validation
```bash
python validation_pipeline/run_validation.py study_005
```

### LLM-based File Modification
```bash
python generation_pipeline/modify_files.py \
  --files data/studies/study_005/specification.json \
  --context "Fix N count for Experiment 1 to 128" \
  --apply
```

---

## 📁 Project Structure

- `data/studies/`: Final generated benchmark files.
- `generation_pipeline/`: PDF analysis and extraction logic.
- `validation_pipeline/`: Automated validation agents.
- `gui.py`: Streamlit control center.
- `src/`: Core benchmark runner and agent logic.
