# Quick Setup Commands

## Standard Workflow

### 1. Prepare Study Directory

```bash
# Create study directory and place PDF file
mkdir -p data/studies/study_002
cp your_paper.pdf data/studies/study_002/
```

### 2. Run Generation Pipeline (Interactive)

```bash
# Run with pauses for manual review
./setup_pipelines.sh study_002
```

This will:
- Run Stage 1 (Filter) → **Pause for review**
- Run Stage 2 (Extraction) → **Pause for review**
- Run Stage 3 (Generate files) → **Pause for review**
- Run Validation

Between each stage, you can:
- Review files in `generation_pipeline/outputs/`
- Modify the `.md` review files if needed
- Press Enter to continue

### 3. Run Generation Pipeline (Auto - No Pauses)

```bash
# Run without pauses (for batch processing)
./setup_pipelines_auto.sh study_002
```

## Manual Step-by-Step

If you prefer to run commands manually:

```bash
# Activate virtual environment
source .venv/bin/activate

# Make sure PDF is in data/studies/{study_id}/
# Copy PDF to current directory for processing
cp data/studies/study_002/*.pdf .

# Stage 1: Filter
python generation_pipeline/run.py --stage 1
# Review: generation_pipeline/outputs/*_stage1_filter.md

# Stage 2: Extraction
python generation_pipeline/run.py --stage 2
# Review: generation_pipeline/outputs/*_stage2_extraction.md

# Stage 3: Generate study files
python generation_pipeline/run.py --stage 3 --study-id study_002

# Validation
python validation_pipeline/run_validation.py study_002

# Clean up
rm *.pdf
```

## Workflow Summary

1. **Place PDF**: `data/studies/{study_id}/*.pdf`
2. **Run Generation**: `./setup_pipelines.sh {study_id}`
3. **Review & Modify**: Edit files in `generation_pipeline/outputs/` between stages
4. **Validation**: Automatically runs after Stage 3

## Example

```bash
# Setup study_002
mkdir -p data/studies/study_002
cp paper.pdf data/studies/study_002/jacowitz-kahneman-1995-measures-of-anchoring-in-estimation-tasks.pdf

# Run pipeline
./setup_pipelines.sh study_002
```
