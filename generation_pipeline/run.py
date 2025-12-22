"""
CLI for Generation Pipeline

Usage:
    python generation_pipeline/run.py --stage 1
    python generation_pipeline/run.py --stage 2
    python generation_pipeline/run.py --stage 1 --refine
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from generation_pipeline.pipeline import GenerationPipeline
from generation_pipeline.utils.review_parser import ReviewParser


def find_pdf_in_current_dir() -> Path:
    """Find PDF file in current directory"""
    current_dir = Path.cwd()
    pdf_files = list(current_dir.glob("*.pdf"))
    
    if len(pdf_files) == 0:
        raise FileNotFoundError("No PDF file found in current directory")
    elif len(pdf_files) > 1:
        raise ValueError(f"Multiple PDF files found: {[f.name for f in pdf_files]}")
    
    return pdf_files[0]


def find_latest_stage_file(stage: int, output_dir: Path) -> Path:
    """Find latest stage file"""
    pattern = f"*_stage{stage}_*.json"
    json_files = list(output_dir.glob(pattern))
    
    if not json_files:
        raise FileNotFoundError(f"No stage {stage} JSON file found in {output_dir}")
    
    # Return most recent
    return max(json_files, key=lambda p: p.stat().st_mtime)


def main():
    parser = argparse.ArgumentParser(description="Semi-Manual Study Generation Pipeline")
    parser.add_argument(
        "--stage",
        type=int,
        required=True,
        choices=[1, 2, 3],
        help="Stage to run (1=Filter, 2=Extraction, 3=Generate Study Files)"
    )
    parser.add_argument(
        "--refine",
        action="store_true",
        help="Refine current stage (re-run with existing review)"
    )
    parser.add_argument(
        "--study-id",
        type=str,
        help="Study ID for stage 3 (e.g., study_001). If not provided, will be inferred from paper_id"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generation_pipeline/outputs"),
        help="Output directory for review files"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="models/gemini-3-flash-preview",
        help="Gemini model to use"
    )
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = GenerationPipeline(
        model=args.model,
        output_dir=args.output_dir
    )
    
    try:
        if args.stage == 1:
            if args.refine:
                # Find latest stage1 review file
                review_file = find_latest_stage_file(1, args.output_dir)
                review_file = review_file.with_suffix('.md')
                
                if not review_file.exists():
                    raise FileNotFoundError(f"Review file not found: {review_file}")
                
                print(f"Refining Stage 1 based on {review_file.name}")
                review_status = pipeline.check_stage1_review(review_file)
                print(f"Review status: {review_status['action']}")
                
                # Re-run stage1
                pdf_path = find_pdf_in_current_dir()
                pipeline.run_stage1(pdf_path)
            else:
                # Run stage1
                pdf_path = find_pdf_in_current_dir()
                pipeline.run_stage1(pdf_path)
        
        elif args.stage == 2:
            if args.refine:
                # Find latest stage2 review file
                review_file = find_latest_stage_file(2, args.output_dir)
                review_file = review_file.with_suffix('.md')
                
                if not review_file.exists():
                    raise FileNotFoundError(f"Review file not found: {review_file}")
                
                print(f"Refining Stage 2 based on {review_file.name}")
                review_status = pipeline.check_stage2_review(review_file)
                print(f"Review status: {review_status['action']}")
                
                # Re-run stage2
                stage1_json = find_latest_stage_file(1, args.output_dir)
                pdf_path = find_pdf_in_current_dir()
                pipeline.run_stage2(stage1_json, pdf_path)
            else:
                # Run stage2
                stage1_json = find_latest_stage_file(1, args.output_dir)
                pdf_path = find_pdf_in_current_dir()
                pipeline.run_stage2(stage1_json, pdf_path)
        
        elif args.stage == 3:
            # Generate study files
            stage2_json = find_latest_stage_file(2, args.output_dir)
            
            # Determine study_id
            if args.study_id:
                study_id = args.study_id
            else:
                # Infer from stage2 JSON
                import json
                stage2_result = json.loads(stage2_json.read_text(encoding='utf-8'))
                paper_id = stage2_result.get('paper_id', 'unknown')
                # Convert paper_id to study_id format
                study_id = f"study_{paper_id.split('_')[-1]}" if '_' in paper_id else f"study_{paper_id}"
                # If paper_id doesn't have number, use 001 as default
                if not any(c.isdigit() for c in study_id):
                    study_id = "study_001"
            
            print(f"Generating study files for {study_id}")
            result = pipeline.generate_study(stage2_json, study_id)
            print(f"\n✓ Study generated successfully!")
            print(f"  Study directory: {result['study_dir']}")
            print(f"  Materials: {len(result.get('materials', []))} files")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

