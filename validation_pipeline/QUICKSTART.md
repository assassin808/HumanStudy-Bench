# Quick Start Guide

## 1. Setup (One-time)

```bash
# Install dependencies
pip install -r validation_pipeline/requirements.txt

# Add API key to .env file in project root
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

## 2. Run Validation

```bash
# Validate study_001
python validation_pipeline/run_validation.py study_001
```

## 3. Check Results

Results are saved in `validation_pipeline/outputs/`:
- `{study_id}_validation_{timestamp}.json` - Full results
- `{study_id}_validation_summary_{timestamp}.md` - Summary report

## Example Output

```
================================================================================
Starting validation for study_001
================================================================================

Loading documents...
Loading config code from src/studies/study_001_config.py...

[1/4] Running Experiment Completeness Agent...
✓ Completeness validation completed

[2/4] Running Experiment Consistency Agent...
✓ Consistency validation completed

[3/4] Running Data Validation Agent...
✓ Data validation completed

[4/4] Generating Validation Checklist...
✓ Checklist generation completed

✓ Results saved to: validation_pipeline/outputs/study_001_validation_20250127_120000.json
✓ Summary saved to: validation_pipeline/outputs/study_001_validation_summary_20250127_120000.md

================================================================================
Validation completed for study_001
================================================================================
```

## Troubleshooting

**API Key Error:**
- Make sure `.env` file exists in project root
- Check that `GOOGLE_API_KEY` is set correctly

**PDF Reading Error:**
- Some PDFs may not extract perfectly
- Check that PDF file exists and is readable

**Import Error:**
- Run: `pip install google-generativeai PyPDF2 python-dotenv`

