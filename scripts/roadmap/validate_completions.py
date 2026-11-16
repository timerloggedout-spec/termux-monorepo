#!/usr/bin/env python3
"""
Validate Completion Records
Validates completion records against the schema and checks for consistency.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from jsonschema import validate, ValidationError, Draft7Validator
from typing import Dict, List, Tuple, Optional

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
COMPLETIONS_DIR = REPO_ROOT / "completions"
SCHEMA_FILE = REPO_ROOT / "schemas" / "roadmap-completion.schema.json"
ROADMAP_INDEX = REPO_ROOT / "roadmaps" / "metadata" / "roadmap-index.json"


def load_schema() -> Dict:
    """Load the completion schema."""
    if not SCHEMA_FILE.exists():
        print(f"⚠️  Schema file not found: {SCHEMA_FILE}")
        return {}
    
    with open(SCHEMA_FILE, 'r') as f:
        return json.load(f)


def load_roadmap_index() -> Dict:
    """Load the roadmap index."""
    if not ROADMAP_INDEX.exists():
        print(f"⚠️  Roadmap index not found: {ROADMAP_INDEX}")
        return {}
    
    with open(ROADMAP_INDEX, 'r') as f:
        return json.load(f)


def get_completion_files() -> List[Path]:
    """Get all completion files."""
    if not COMPLETIONS_DIR.exists():
        return []
    
    files = []
    for ext in ['*.json', '*.jsonl']:
        files.extend(COMPLETIONS_DIR.glob(f"**/{ext}"))
    
    return files


def validate_record(record: Dict, schema: Dict) -> Tuple[bool, List[str]]:
    """Validate a single completion record against the schema."""
    errors = []
    
    try:
        validate(instance=record, schema=schema)
        return True, errors
    except ValidationError as e:
        errors.append(f"Validation error: {e.message} (path: {e.path})")
        return False, errors
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        return False, errors


def check_roadmap_exists(record: Dict, roadmap_index: Dict) -> Tuple[bool, List[str]]:
    """Check if the roadmap in the record exists in the index."""
    errors = []
    roadmap_slug = record.get("roadmap_slug", "")
    
    if not roadmap_slug:
        errors.append("Missing roadmap_slug")
        return False, errors
    
    if not roadmap_index.get("roadmaps", {}).get(roadmap_slug):
        errors.append(f"Unknown roadmap: {roadmap_slug}")
        return False, errors
    
    return True, errors


def check_required_fields(record: Dict) -> Tuple[bool, List[str]]:
    """Check for required fields."""
    errors = []
    required_fields = ["user_id", "roadmap_slug", "topic_id", "completion_status", "last_updated"]
    
    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required field: {field}")
    
    return len(errors) == 0, errors


def check_completion_status(record: Dict) -> Tuple[bool, List[str]]:
    """Check that completion_status is valid."""
    errors = []
    valid_statuses = ["not_started", "in_progress", "completed", "mastered"]
    status = record.get("completion_status", "")
    
    if status not in valid_statuses:
        errors.append(f"Invalid completion_status: {status}. Must be one of {valid_statuses}")
    
    return len(errors) == 0, errors


def check_percentage(record: Dict) -> Tuple[bool, List[str]]:
    """Check that completion_percentage is valid."""
    errors = []
    percentage = record.get("completion_percentage")
    
    if percentage is not None:
        if not isinstance(percentage, (int, float)):
            errors.append(f"completion_percentage must be a number, got {type(percentage)}")
        elif not (0 <= percentage <= 100):
            errors.append(f"completion_percentage must be between 0 and 100, got {percentage}")
    
    return len(errors) == 0, errors


def validate_completions(schema_only: bool = False) -> Dict:
    """Validate all completion records."""
    schema = load_schema()
    roadmap_index = load_roadmap_index()
    completion_files = get_completion_files()
    
    results = {
        "total_records": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "errors": [],
        "warnings": [],
        "details": []
    }
    
    if not schema:
        results["warnings"].append("No schema found, skipping schema validation")
        schema_only = True
    
    if not roadmap_index:
        results["warnings"].append("No roadmap index found, skipping roadmap validation")
    
    for completion_file in completion_files:
        try:
            with open(completion_file, 'r') as f:
                content = json.load(f)
            
            # Handle both single record and array of records
            if isinstance(content, list):
                records = content
            else:
                records = [content]
            
            for i, record in enumerate(records):
                results["total_records"] += 1
                record_errors = []
                record_warnings = []
                is_valid = True
                
                # Schema validation
                if schema and not schema_only:
                    valid, errors = validate_record(record, schema)
                    if not valid:
                        is_valid = False
                        record_errors.extend(errors)
                
                # Required fields
                if not schema_only:
                    valid, errors = check_required_fields(record)
                    if not valid:
                        is_valid = False
                        record_errors.extend(errors)
                
                # Roadmap exists
                if roadmap_index and not schema_only:
                    valid, errors = check_roadmap_exists(record, roadmap_index)
                    if not valid:
                        is_valid = False
                        record_warnings.extend(errors)
                
                # Completion status
                if not schema_only:
                    valid, errors = check_completion_status(record)
                    if not valid:
                        is_valid = False
                        record_errors.extend(errors)
                
                # Percentage
                if not schema_only:
                    valid, errors = check_percentage(record)
                    if not valid:
                        is_valid = False
                        record_errors.extend(errors)
                
                if is_valid:
                    results["valid_records"] += 1
                else:
                    results["invalid_records"] += 1
                
                if record_errors:
                    results["errors"].append({
                        "file": str(completion_file),
                        "record_index": i,
                        "errors": record_errors
                    })
                
                if record_warnings:
                    results["warnings"].append({
                        "file": str(completion_file),
                        "record_index": i,
                        "warnings": record_warnings
                    })
                
                results["details"].append({
                    "file": str(completion_file),
                    "record_index": i,
                    "valid": is_valid,
                    "user_id": record.get("user_id", "unknown"),
                    "roadmap_slug": record.get("roadmap_slug", "unknown"),
                    "topic_id": record.get("topic_id", "unknown"),
                    "completion_status": record.get("completion_status", "unknown")
                })
                
        except json.JSONDecodeError as e:
            results["errors"].append({
                "file": str(completion_file),
                "error": f"Invalid JSON: {str(e)}"
            })
        except Exception as e:
            results["errors"].append({
                "file": str(completion_file),
                "error": f"Error reading file: {str(e)}"
            })
    
    return results


def validate_schema_only() -> Dict:
    """Validate schema only (check if schema file is valid)."""
    schema = load_schema()
    
    if not schema:
        return {
            "valid": False,
            "error": "Schema file not found"
        }
    
    # Try to validate the schema itself
    try:
        # This is a simple check - in production, use a proper schema validator
        required_keys = ["$schema", "type", "properties"]
        for key in required_keys:
            if key not in schema:
                return {
                    "valid": False,
                    "error": f"Missing required key in schema: {key}"
                }
        
        return {
            "valid": True,
            "message": "Schema is valid"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="Validate completion records")
    parser.add_argument("--schema-only", action="store_true", help="Validate schema only")
    parser.add_argument("--quiet", action="store_true", help="Quiet output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if args.schema_only:
        result = validate_schema_only()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result["valid"]:
                print("✅ Schema is valid")
            else:
                print(f"❌ Schema validation failed: {result.get('error', 'Unknown error')}")
        sys.exit(0 if result["valid"] else 1)
    
    results = validate_completions(args.schema_only)
    
    if args.json:
        print(json.dumps(results, indent=2))
        sys.exit(0 if results["invalid_records"] == 0 else 1)
    
    if not args.quiet:
        print("=" * 60)
        print("Completion Records Validation Report")
        print("=" * 60)
        print()
        
        print(f"📊 Total Records: {results['total_records']}")
        print(f"✅ Valid: {results['valid_records']}")
        print(f"❌ Invalid: {results['invalid_records']}")
        print()
        
        if results["warnings"]:
            print("⚠️  Warnings:")
            for warning in results["warnings"][:5]:  # Show first 5
                print(f"  - {warning.get('file', 'unknown')}: {warning.get('warnings', [''])[0]}")
            if len(results["warnings"]) > 5:
                print(f"  ... and {len(results['warnings']) - 5} more warnings")
            print()
        
        if results["errors"]:
            print("❌ Errors:")
            for error in results["errors"][:10]:  # Show first 10
                if "errors" in error:
                    for err in error["errors"][:3]:
                        print(f"  - {error.get('file', 'unknown')}: {err}")
                else:
                    print(f"  - {error.get('file', 'unknown')}: {error.get('error', 'Unknown error')}")
            if len(results["errors"]) > 10:
                print(f"  ... and {len(results['errors']) - 10} more errors")
            print()
        
        if results["invalid_records"] == 0:
            print("✅ All completion records are valid!")
        else:
            print(f"⚠️  {results['invalid_records']} invalid records found")
        
        print("=" * 60)
    
    sys.exit(0 if results["invalid_records"] == 0 else 1)


if __name__ == "__main__":
    main()
