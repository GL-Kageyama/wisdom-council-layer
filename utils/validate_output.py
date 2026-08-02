#!/usr/bin/env python3
"""Validate a Wisdom Council evaluator output against the shared JSON schema.

Usage:
    python utils/validate_output.py < evaluator_output.json
    cat output.json | python utils/validate_output.py
    python utils/validate_output.py output.json

Exit codes:
    0  valid
    1  invalid (with a report of the errors)
    2  usage / IO error

This script has no third-party dependencies: it vendors a minimal JSON
Schema validator for the single schema used in this project.
"""

import json
import os
import sys
import re

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "value-output.schema.json")

VECTOR_DIMENSIONS = [
    "originality",
    "quality",
    "aesthetic",
    "emotional_impact",
    "future_potential",
    "business_value",
    "scientific_novelty",
    "philosophical_depth",
    "meaning",
]

CLASSIFICATIONS = ["current_success", "discovery_target", "trend_object", "low_signal"]
DOMAINS = ["creative", "scientific", "business", "social", "digital", "cultural"]


def load_json(path_or_none):
    """Load JSON from a file path, or from stdin if path_or_none is None."""
    if path_or_none:
        with open(path_or_none, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def validate_basic(obj):
    """Validate the top-level structure and required fields."""
    errors = []

    if not isinstance(obj, dict):
        return ["Root must be a JSON object"]

    required = [
        "evaluator_id",
        "evaluator_name",
        "content_summary",
        "domain",
        "primary_score",
        "primary_score_rationale",
        "dimension_scores",
        "value_vector_contribution",
        "classification",
        "confidence",
        "strengths",
        "weaknesses",
        "unique_perspective",
        "expected_disagreement_points",
        "narrative",
    ]
    for field in required:
        if field not in obj:
            errors.append(f"Missing required field: '{field}'")

    if "evaluator_id" in obj and not re.match(r"^[a-z0-9-]+$", str(obj["evaluator_id"])):
        errors.append(f"evaluator_id '{obj['evaluator_id']}' must be lowercase kebab-case")

    if "domain" in obj and obj["domain"] not in DOMAINS:
        errors.append(f"domain '{obj['domain']}' not in {DOMAINS}")

    for field in ("primary_score", "confidence"):
        if field in obj:
            v = obj[field]
            if not isinstance(v, int) or isinstance(v, bool):
                errors.append(f"{field} must be an integer, got {type(v).__name__}")
            elif not (0 <= v <= 100):
                errors.append(f"{field} must be 0-100, got {v}")

    if "classification" in obj and obj["classification"] not in CLASSIFICATIONS:
        errors.append(f"classification '{obj['classification']}' not in {CLASSIFICATIONS}")

    for field in ("strengths", "weaknesses", "improvement_suggestions"):
        if field in obj and not isinstance(obj[field], list):
            errors.append(f"{field} must be an array")

    if "expected_disagreement_points" in obj and not isinstance(
        obj["expected_disagreement_points"], list
    ):
        errors.append("expected_disagreement_points must be an array")

    if "value_vector_contribution" in obj:
        vec = obj["value_vector_contribution"]
        if not isinstance(vec, dict):
            errors.append("value_vector_contribution must be an object")
        else:
            unknown = set(vec.keys()) - set(VECTOR_DIMENSIONS)
            if unknown:
                errors.append(f"value_vector_contribution has unknown dimensions: {sorted(unknown)}")
            non_null = 0
            for dim in VECTOR_DIMENSIONS:
                v = vec.get(dim)
                if v is not None:
                    if not isinstance(v, int) or isinstance(v, bool) or not (0 <= v <= 100):
                        errors.append(f"value_vector_contribution.{dim} must be an int 0-100 or null")
                    else:
                        non_null += 1
            # An evaluator should contribute at least one dimension.
            if non_null == 0:
                errors.append("value_vector_contribution must have at least one non-null dimension")

    if "dimension_scores" in obj:
        ds = obj["dimension_scores"]
        if not isinstance(ds, dict):
            errors.append("dimension_scores must be an object")
        else:
            for dim, entry in ds.items():
                if not isinstance(entry, dict):
                    errors.append(f"dimension_scores.{dim} must be an object")
                    continue
                for sub in ("score", "weight", "evidence", "judgment"):
                    if sub not in entry:
                        errors.append(f"dimension_scores.{dim} missing '{sub}'")
                if isinstance(entry.get("score"), int) and not (
                    0 <= entry["score"] <= 100
                ):
                    errors.append(f"dimension_scores.{dim}.score must be 0-100")

    if "evaluator_id" in obj:
        evaluator_id = obj["evaluator_id"]
        # Check the evaluator scored exactly its own dimension (a soft sanity check).
        expected_dim = {
            "originality": "originality",
            "anti-generic-filter": "quality",
            "aesthetic-critic": "aesthetic",
            "emotional-impact": "emotional_impact",
            "future-potential": "future_potential",
            "business-value": "business_value",
            "scientific-novelty": "scientific_novelty",
            "philosophical-evaluator": "philosophical_depth",
            "quality-evaluator": "quality",
            "meaning-evaluator": "meaning",
        }.get(evaluator_id)
        vec = obj.get("value_vector_contribution", {}) if isinstance(
            obj.get("value_vector_contribution"), dict
        ) else {}
        if expected_dim and vec.get(expected_dim) is None:
            errors.append(
                f"evaluator_id '{evaluator_id}' is expected to score "
                f"'{expected_dim}' but that dimension is null"
            )

    return errors


def validate_report(obj):
    """Validate a council Value Report (produced by council/SKILL.md)."""
    errors = []

    if not isinstance(obj, dict):
        return ["Root must be a JSON object"]

    for field in ("executive_summary", "synthesis_narrative", "classification"):
        if field not in obj:
            errors.append(f"Missing report field: '{field}'")

    if "classification" in obj and obj["classification"] not in CLASSIFICATIONS + ["innovation"]:
        errors.append(f"report classification '{obj['classification']}' not recognized")

    if "disagreement_map" in obj and not isinstance(obj["disagreement_map"], list):
        errors.append("disagreement_map must be an array")

    if "value_vector" in obj:
        vec = obj["value_vector"]
        if not isinstance(vec, dict):
            errors.append("value_vector must be an object")
        else:
            unknown = set(vec.keys()) - set(VECTOR_DIMENSIONS)
            if unknown:
                errors.append(f"value_vector has unknown dimensions: {sorted(unknown)}")

    if "individual_reports" in obj:
        reports = obj["individual_reports"]
        if not isinstance(reports, list):
            errors.append("individual_reports must be an array")
        else:
            for i, report in enumerate(reports):
                for err in validate_basic(report):
                    errors.append(f"individual_reports[{i}]: {err}")

    return errors


def main():
    if len(sys.argv) > 2:
        print("Usage: python utils/validate_output.py [output.json]", file=sys.stderr)
        return 2

    try:
        obj = load_json(sys.argv[1] if len(sys.argv) == 2 else None)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Could not read input: {e}", file=sys.stderr)
        return 2

    # Detect whether this is an evaluator output or a council report.
    if isinstance(obj, dict) and "evaluator_id" in obj:
        errors = validate_basic(obj)
        kind = "evaluator output"
    elif isinstance(obj, dict) and "report_id" in obj:
        errors = validate_report(obj)
        kind = "council report"
    else:
        errors = [
            "Input is neither an evaluator output (missing 'evaluator_id') "
            "nor a council report (missing 'report_id')"
        ]
        kind = "unknown"

    if errors:
        print(f"INVALID {kind} — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1

    print(f"✓ VALID {kind}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
