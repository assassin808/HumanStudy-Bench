# Generation Pipeline

Semi-manual pipeline for extracting study information from PDF papers and generating compatible study configurations.

## Usage

### Stage 1: Replicability Filter

```bash
# Place PDF file in current directory, then run:
python generation_pipeline/run.py --stage 1
```

This will:
- Extract paper title, authors, abstract
- Identify all experiments
- Determine replicability for each experiment
- Generate `{paper_id}_stage1_filter.md` and `.json` in `generation_pipeline/outputs/`

### Review Stage 1

1. Open `generation_pipeline/outputs/{paper_id}_stage1_filter.md`
2. Review and fill in checklists and comments
3. Set action in "Review Status" section:
   - `continue_to_stage2` - Proceed to stage 2
   - `refine_stage1` - Re-run stage 1
   - `exclude` - Stop processing

### Stage 2: Study & Data Extraction

```bash
python generation_pipeline/run.py --stage 2
```

This will:
- Extract all studies/problems
- Extract phenomena
- Extract research questions with statistical data
- Extract statistical methods and results
- Extract participant profiles
- Generate `{paper_id}_stage2_extraction.md` and `.json`

### Review Stage 2

1. Open `generation_pipeline/outputs/{paper_id}_stage2_extraction.md`
2. Review and fill in checklists and comments
3. Set action:
   - `continue_to_final` - Generate study files
   - `refine_stage2` - Re-run stage 2
   - `back_to_stage1` - Go back to stage 1

### Refine Stages

```bash
# Refine stage 1
python generation_pipeline/run.py --stage 1 --refine

# Refine stage 2
python generation_pipeline/run.py --stage 2 --refine
```

### Generate Study Files

After stage 2 review is approved, use the pipeline programmatically:

```python
from generation_pipeline.pipeline import GenerationPipeline

pipeline = GenerationPipeline()
stage2_json = Path("generation_pipeline/outputs/{paper_id}_stage2_extraction.json")

# Generate study files
pipeline.generate_study(stage2_json, study_id="study_005")
```

This generates:
- `data/studies/{study_id}/metadata.json`
- `data/studies/{study_id}/specification.json`
- `data/studies/{study_id}/ground_truth.json`
- `src/studies/{study_id}_config.py`

**Note**: Generated config class needs manual refinement. Also update `get_study_config()` factory function in `src/core/study_config.py`.

## Requirements

- Google Gemini API key (set `GOOGLE_API_KEY` environment variable)
- PDF file in current directory (or specify path in code)

## Output Format

All outputs are saved to `generation_pipeline/outputs/`:
- `{paper_id}_stage1_filter.md` - Review file for stage 1
- `{paper_id}_stage1_filter.json` - JSON data for stage 1
- `{paper_id}_stage2_extraction.md` - Review file for stage 2
- `{paper_id}_stage2_extraction.json` - JSON data for stage 2

