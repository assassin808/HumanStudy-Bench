# File Modifier Tool

Use LLM to modify files based on context and instructions. **Automatically includes original paper PDF** for better accuracy.

## Usage

### Basic Usage

```bash
# Modify single file (auto-detects PDF from study directory)
python generation_pipeline/modify_files.py \
  --files data/studies/study_001/specification.json \
  --context "Fix participant N values - should be 504 total, not 824"
# PDF is automatically found in data/studies/study_001/ or backup/data/studies/study_001/

# Modify multiple files
python generation_pipeline/modify_files.py \
  --files file1.json file2.md file3.txt \
  --context "Update all participant demographics to include age_range [18, 22]"

# Apply changes directly (creates .backup files)
python generation_pipeline/modify_files.py \
  --files data/studies/study_001/specification.json \
  --context "Fix participant N values" \
  --apply

# Save to custom output directory
python generation_pipeline/modify_files.py \
  --files file1.json \
  --context "Update metadata" \
  --output-dir modified_files/

# Manually specify PDF (if auto-detection doesn't work)
python generation_pipeline/modify_files.py \
  --files data/studies/study_001/specification.json \
  --context "Fix participant data" \
  --pdf data/studies/study_001/paper.pdf

# Disable auto PDF detection
python generation_pipeline/modify_files.py \
  --files file1.json \
  --context "Update metadata" \
  --no-auto-pdf
```

## Examples

### Fix Participant Data

```bash
python generation_pipeline/modify_files.py \
  --files data/studies/study_001/specification.json \
  --context "The total N should be 504, not 824. Update the total N and verify by_sub_study Ns sum correctly."
```

### Update Multiple Files

```bash
python generation_pipeline/modify_files.py \
  --files \
    data/studies/study_001/metadata.json \
    data/studies/study_001/specification.json \
    data/studies/study_001/ground_truth.json \
  --context "Add year 1977 to all files. Update domain to social_psychology and subdomain to social_cognition."
```

### Modify Review Files

```bash
python generation_pipeline/modify_files.py \
  --files generation_pipeline/outputs/paper_stage1_filter.md \
  --context "Mark all experiments as replicable=YES and update checklists accordingly"
```

## Workflow

1. **Review Mode (default)**: 
   - Saves modified files with `.modified` extension
   - Review changes before applying
   - Manually copy or merge changes

2. **Apply Mode (`--apply`)**:
   - Creates `.backup` files for originals
   - Applies changes directly
   - Use with caution!

## Key Features

- **Auto PDF Detection**: Automatically finds and includes original paper PDF from study directory
- **PDF Context**: LLM can reference the original paper for accurate modifications
- **Multiple Files**: Modify multiple files simultaneously with shared context
- **Safe by Default**: Saves to `.modified` files for review (use `--apply` to apply directly)

## Safety Features

- Always creates backups when using `--apply`
- Default mode saves to separate files for review
- Can specify custom output directory
- Preserves original file structure and formatting
- PDF is automatically included for better accuracy

