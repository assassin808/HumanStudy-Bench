#!/bin/bash
# Automated setup script for Generation and Validation Pipelines
# Workflow:
# 1. Place PDF in data/studies/{study_id}/
# 2. Run generation stages 1, 2, 3 (can modify outputs between stages)
# 3. Run validation pipeline

# Don't use set -e, handle errors manually

cd "$(dirname "$0")"
source .venv/bin/activate

echo "=========================================="
echo "Generation & Validation Pipeline Setup"
echo "=========================================="
echo ""

# Check if study_id is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <study_id>"
    echo "Example: $0 study_001"
    echo ""
    echo "Make sure:"
    echo "  1. PDF file is placed in data/studies/{study_id}/"
    echo "  2. Review and modify outputs between stages if needed"
    exit 1
fi

STUDY_ID="$1"
STUDY_DIR="data/studies/$STUDY_ID"

if [ ! -d "$STUDY_DIR" ]; then
    echo "⚠️  Study directory not found: $STUDY_DIR"
    echo "Please create the directory and place PDF file there first"
    exit 1
fi

# Find PDF file in study directory
PDF_FILE=$(find "$STUDY_DIR" -name "*.pdf" -type f | head -n 1)

if [ -z "$PDF_FILE" ]; then
    echo "⚠️  No PDF file found in $STUDY_DIR"
    echo "Please place a PDF file in the study directory"
    exit 1
fi

echo "📄 Found PDF: $(basename "$PDF_FILE")"
echo "📁 Study ID: $STUDY_ID"
echo ""

# Copy PDF to current directory for processing (pipeline expects it in current dir)
cp "$PDF_FILE" ./
PDF_NAME=$(basename "$PDF_FILE")

# Generation Pipeline - Stage 1
echo "=========================================="
echo "Stage 1: Replicability Filter"
echo "=========================================="
if ! python generation_pipeline/run.py --stage 1; then
    echo "⚠️  Stage 1 failed for $STUDY_ID"
    rm -f "$PDF_NAME"
    exit 1
fi

# Get paper_id from generated file
PAPER_ID=$(ls generation_pipeline/outputs/*_stage1_filter.json 2>/dev/null | head -1 | xargs basename | sed 's/_stage1_filter.json//')
if [ -z "$PAPER_ID" ]; then
    echo "⚠️  Could not find stage1 output file"
    rm -f "$PDF_NAME"
    exit 1
fi

echo ""
echo "✓ Stage 1 complete. Paper ID: $PAPER_ID"
echo "📝 Review file: generation_pipeline/outputs/${PAPER_ID}_stage1_filter.md"
echo ""
echo "💡 You can now review and modify the output file if needed."
echo "   Press Enter to continue to Stage 2, or Ctrl+C to exit..."
read

# Generation Pipeline - Stage 2
echo ""
echo "=========================================="
echo "Stage 2: Data Extraction"
echo "=========================================="
if ! python generation_pipeline/run.py --stage 2; then
    echo "⚠️  Stage 2 failed for $STUDY_ID"
    rm -f "$PDF_NAME"
    exit 1
fi

echo ""
echo "✓ Stage 2 complete"
echo "📝 Review file: generation_pipeline/outputs/${PAPER_ID}_stage2_extraction.md"
echo ""
echo "💡 You can now review and modify the output file if needed."
echo "   Press Enter to continue to Stage 3, or Ctrl+C to exit..."
read

# Generation Pipeline - Stage 3
echo ""
echo "=========================================="
echo "Stage 3: Generate Study Files"
echo "=========================================="
if ! python generation_pipeline/run.py --stage 3 --study-id "$STUDY_ID"; then
    echo "⚠️  Stage 3 failed for $STUDY_ID"
    rm -f "$PDF_NAME"
    exit 1
fi

echo ""
echo "✓ Stage 3 complete"
echo "📁 Study files generated in: $STUDY_DIR"
echo ""
echo "💡 Review the generated files if needed."
echo "   Press Enter to continue to Validation, or Ctrl+C to exit..."
read

# Validation Pipeline
echo ""
echo "=========================================="
echo "Validation: Validate $STUDY_ID"
echo "=========================================="
if ! python validation_pipeline/run_validation.py "$STUDY_ID"; then
    echo "⚠️  Validation failed for $STUDY_ID"
    rm -f "$PDF_NAME"
    exit 1
fi

echo ""
echo "✓ Validation complete"
echo "📝 Validation report: validation_pipeline/outputs/${STUDY_ID}_validation_summary_*.md"

# Clean up PDF from current directory
rm -f "$PDF_NAME"

echo ""
echo "=========================================="
echo "✅ All pipelines completed for $STUDY_ID!"
echo "=========================================="
echo ""
echo "Generated files:"
echo "  ✓ $STUDY_DIR/"
echo "  ✓ generation_pipeline/outputs/"
echo "  ✓ validation_pipeline/outputs/"
echo ""
