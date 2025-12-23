#!/bin/bash
# Automated setup script (no pauses) for Generation and Validation Pipelines
# Use this for batch processing without manual review pauses

cd "$(dirname "$0")"
source .venv/bin/activate

echo "=========================================="
echo "Generation & Validation Pipeline (Auto)"
echo "=========================================="
echo ""

# Check if study_id is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <study_id>"
    echo "Example: $0 study_001"
    exit 1
fi

STUDY_ID="$1"
STUDY_DIR="data/studies/$STUDY_ID"

if [ ! -d "$STUDY_DIR" ]; then
    echo "⚠️  Study directory not found: $STUDY_DIR"
    exit 1
fi

# Find PDF file in study directory
PDF_FILE=$(find "$STUDY_DIR" -name "*.pdf" -type f | head -n 1)

if [ -z "$PDF_FILE" ]; then
    echo "⚠️  No PDF file found in $STUDY_DIR"
    exit 1
fi

echo "📄 PDF: $(basename "$PDF_FILE")"
echo "📁 Study ID: $STUDY_ID"
echo ""

# Copy PDF to current directory for processing
cp "$PDF_FILE" ./
PDF_NAME=$(basename "$PDF_FILE")

# Generation Pipeline - Stage 1
echo "Stage 1: Replicability Filter"
if ! python generation_pipeline/run.py --stage 1; then
    echo "⚠️  Stage 1 failed"
    rm -f "$PDF_NAME"
    exit 1
fi

PAPER_ID=$(ls generation_pipeline/outputs/*_stage1_filter.json 2>/dev/null | head -1 | xargs basename | sed 's/_stage1_filter.json//')
echo "✓ Stage 1 complete"

# Generation Pipeline - Stage 2
echo ""
echo "Stage 2: Data Extraction"
if ! python generation_pipeline/run.py --stage 2; then
    echo "⚠️  Stage 2 failed"
    rm -f "$PDF_NAME"
    exit 1
fi
echo "✓ Stage 2 complete"

# Generation Pipeline - Stage 3
echo ""
echo "Stage 3: Generate Study Files"
if ! python generation_pipeline/run.py --stage 3 --study-id "$STUDY_ID"; then
    echo "⚠️  Stage 3 failed"
    rm -f "$PDF_NAME"
    exit 1
fi
echo "✓ Stage 3 complete"

# Validation Pipeline
echo ""
echo "Validation: Validate $STUDY_ID"
if ! python validation_pipeline/run_validation.py "$STUDY_ID"; then
    echo "⚠️  Validation failed"
    rm -f "$PDF_NAME"
    exit 1
fi
echo "✓ Validation complete"

# Clean up
rm -f "$PDF_NAME"

echo ""
echo "✅ Completed: $STUDY_ID"
echo ""

