# Human Study Benchmark (HS_bench)

A benchmark for evaluating LLM agents' ability to replicate human psychological studies.

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r validation_pipeline/requirements.txt

# Set up environment
export GOOGLE_API_KEY="your-api-key"  # For Gemini API
```

### 2. Generate New Studies from Papers

**Workflow:**
1. Place PDF file in `data/studies/{study_id}/`
2. Run generation pipeline (with review pauses)
3. Modify outputs between stages if needed
4. Validation runs automatically

```bash
# Create study directory and place PDF
mkdir -p data/studies/study_002
cp paper.pdf data/studies/study_002/

# Run pipeline (interactive with pauses for review)
./setup_pipelines.sh study_002

# Or run without pauses (auto mode)
./setup_pipelines_auto.sh study_002
```

**Output**: Study files in `data/studies/{study_id}/`:
- `metadata.json` - Study metadata
- `specification.json` - Experimental design and participants
- `ground_truth.json` - Human data and validation criteria
- `materials/` - Scenario/questionnaire files

**Review Files** (can be modified between stages):
- `generation_pipeline/outputs/{paper_id}_stage1_filter.md`
- `generation_pipeline/outputs/{paper_id}_stage2_extraction.md`

### 3. Validate Existing Studies

Use the **Validation Pipeline** to check if study implementations match original papers:

```bash
# Validate a specific study
python validation_pipeline/run_validation.py study_001

# Validate with custom output directory
python validation_pipeline/run_validation.py study_001 --output-dir custom_outputs
```

**Output**: Validation reports in `validation_pipeline/outputs/`:
- `{study_id}_validation_{timestamp}.json` - Detailed validation results
- `{study_id}_validation_summary_{timestamp}.md` - Human-readable summary

## Pipeline Overview

### Generation Pipeline

Semi-manual pipeline for creating new studies from research papers:

1. **Stage 1: Replicability Filter**
   - Extracts paper metadata (title, authors, abstract)
   - Identifies all experiments
   - Determines which experiments can be replicated with LLM agents
   - Excludes: visual input, time perception, vague participant profiles

2. **Stage 2: Data Extraction**
   - Extracts all sub-studies/scenarios
   - Extracts materials (scenarios, questionnaires)
   - Extracts participant information (N, demographics)
   - Extracts human data (means, percentages, statistical results)
   - Extracts statistical tests

3. **Stage 3: Study Generation**
   - Generates JSON files (metadata, specification, ground_truth)
   - Generates materials files
   - Generates Config class template

**Refinement**: Use `--refine` flag to re-run stages based on review feedback.

### Validation Pipeline

Automated validation to ensure study implementations match original papers:

- **Experiment Completeness**: Checks if all experiments from paper are included
- **Data Validation**: Verifies human data matches paper tables/figures
- **Experiment Consistency**: Ensures design matches original study

## Project Structure

```
HS_bench/
├── data/
│   └── studies/
│       └── study_001/          # Study files
│           ├── metadata.json
│           ├── specification.json
│           ├── ground_truth.json
│           └── materials/
├── generation_pipeline/        # Study generation from PDFs
│   ├── run.py                   # CLI: --stage {1,2,3}
│   ├── filters/                 # Stage 1: Replicability filter
│   ├── extractors/              # Stage 2: Data extraction
│   └── generators/              # Stage 3: File generation
├── validation_pipeline/         # Study validation
│   ├── run_validation.py        # CLI: --study-id or --all
│   └── agents/                  # Validation agents
└── src/                         # Core benchmark code
    ├── core/
    ├── agents/
    └── studies/
```

## Examples

### Generate Study from PDF

```bash
# 1. Place PDF in study directory
mkdir -p data/studies/study_005
cp paper.pdf data/studies/study_005/

# 2. Run pipeline (interactive)
./setup_pipelines.sh study_005

# Or run manually:
cp data/studies/study_005/*.pdf .
python generation_pipeline/run.py --stage 1 --study-id study_005
# Review: generation_pipeline/outputs/*_stage1_filter.md

python generation_pipeline/run.py --stage 2 --study-id study_005
# Review: generation_pipeline/outputs/*_stage2_extraction.md

python generation_pipeline/run.py --stage 3 --study-id study_005
python validation_pipeline/run_validation.py study_005
rm *.pdf
```

### Modify Files with LLM

```bash
# Modify single file (saves to .modified for review)
python generation_pipeline/modify_files.py \
  --files data/studies/study_001/specification.json \
  --context "Fix participant N: total should be 504, update by_sub_study accordingly"

# Modify multiple files
python generation_pipeline/modify_files.py \
  --files file1.json file2.md \
  --context "Add year 1977 and update domain to social_psychology"

# Apply changes directly (creates .backup)
python generation_pipeline/modify_files.py \
  --files data/studies/study_001/specification.json \
  --context "Fix participant N values" \
  --apply
```

### Validate Study

```bash
# Validate single study
python validation_pipeline/run_validation.py study_001

# Check results
cat validation_pipeline/outputs/study_001_validation_summary_*.md
```

## Requirements

- Python 3.10+
- Google Gemini API key (for generation and validation pipelines)
- See `requirements.txt` and `validation_pipeline/requirements.txt`

## Additional Tools

### File Modifier

Use LLM to modify files based on context:

```bash
python generation_pipeline/modify_files.py --files file1.json --context "Fix participant data"
```

See `generation_pipeline/README_FILE_MODIFIER.md` for details.

## Documentation

- **Generation Pipeline**: See `generation_pipeline/README.md`
- **File Modifier**: See `generation_pipeline/README_FILE_MODIFIER.md`
- **Validation Pipeline**: See `validation_pipeline/QUICKSTART.md`
- **API Reference**: See `docs/api_reference.md`

## License

[Add license information]
