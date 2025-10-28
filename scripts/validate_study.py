"""
Script to validate a study's data integrity.

Usage:
    python scripts/validate_study.py study_001
"""

import sys
import json
from pathlib import Path
import jsonschema


def validate_study(study_id: str, data_dir: Path = Path("data")) -> bool:
    """
    Validate a study's data integrity.
    
    Args:
        study_id: Study identifier
        data_dir: Path to data directory
        
    Returns:
        True if valid, False otherwise
    """
    print(f"Validating {study_id}...")
    print("=" * 60)
    
    study_path = data_dir / "studies" / study_id
    schemas_dir = data_dir / "schemas"
    
    errors = []
    warnings = []
    
    # Check study directory exists
    if not study_path.exists():
        errors.append(f"Study directory not found: {study_path}")
        return False
    
    # Load schemas
    try:
        with open(schemas_dir / "metadata_schema.json") as f:
            metadata_schema = json.load(f)
        with open(schemas_dir / "specification_schema.json") as f:
            specification_schema = json.load(f)
        with open(schemas_dir / "ground_truth_schema.json") as f:
            ground_truth_schema = json.load(f)
    except Exception as e:
        errors.append(f"Failed to load schemas: {e}")
        return False
    
    # Validate metadata.json
    print("\n[1/5] Validating metadata.json...")
    metadata_path = study_path / "metadata.json"
    if not metadata_path.exists():
        errors.append("metadata.json not found")
    else:
        try:
            with open(metadata_path) as f:
                metadata = json.load(f)
            jsonschema.validate(metadata, metadata_schema)
            print("  ✓ metadata.json is valid")
            
            # Check ID matches
            if metadata.get("id") != study_id:
                errors.append(f"ID mismatch in metadata: {metadata.get('id')} != {study_id}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in metadata.json: {e}")
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed for metadata.json: {e.message}")
    
    # Validate specification.json
    print("\n[2/5] Validating specification.json...")
    spec_path = study_path / "specification.json"
    if not spec_path.exists():
        errors.append("specification.json not found")
    else:
        try:
            with open(spec_path) as f:
                specification = json.load(f)
            jsonschema.validate(specification, specification_schema)
            print("  ✓ specification.json is valid")
            
            if specification.get("study_id") != study_id:
                errors.append(f"ID mismatch in specification: {specification.get('study_id')} != {study_id}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in specification.json: {e}")
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed for specification.json: {e.message}")
    
    # Validate ground_truth.json
    print("\n[3/5] Validating ground_truth.json...")
    gt_path = study_path / "ground_truth.json"
    if not gt_path.exists():
        errors.append("ground_truth.json not found")
    else:
        try:
            with open(gt_path) as f:
                ground_truth = json.load(f)
            jsonschema.validate(ground_truth, ground_truth_schema)
            print("  ✓ ground_truth.json is valid")
            
            if ground_truth.get("study_id") != study_id:
                errors.append(f"ID mismatch in ground_truth: {ground_truth.get('study_id')} != {study_id}")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in ground_truth.json: {e}")
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed for ground_truth.json: {e.message}")
    
    # Check materials directory
    print("\n[4/5] Checking materials directory...")
    materials_path = study_path / "materials"
    if not materials_path.exists():
        warnings.append("materials/ directory not found")
    else:
        print("  ✓ materials/ directory exists")
        
        # Check for instructions
        if not (materials_path / "instructions.txt").exists():
            warnings.append("materials/instructions.txt not found")
        
        # Check for stimuli directory
        if not (materials_path / "stimuli").exists():
            warnings.append("materials/stimuli/ directory not found")
    
    # Check registry entry
    print("\n[5/5] Checking registry entry...")
    registry_path = data_dir / "registry.json"
    if registry_path.exists():
        with open(registry_path) as f:
            registry = json.load(f)
        
        found = False
        for study_info in registry["studies"]:
            if study_info["id"] == study_id:
                found = True
                print("  ✓ Study found in registry")
                break
        
        if not found:
            warnings.append(f"Study {study_id} not found in registry.json")
    else:
        warnings.append("registry.json not found")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ {len(errors)} Error(s):")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} Warning(s):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("\n✅ Study is valid!")
        return True
    elif not errors:
        print("\n✅ Study is valid (with warnings)")
        return True
    else:
        print("\n❌ Study validation failed")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_study.py <study_id>")
        print("Example: python scripts/validate_study.py study_001")
        sys.exit(1)
    
    study_id = sys.argv[1]
    data_dir = Path("data")
    
    success = validate_study(study_id, data_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
