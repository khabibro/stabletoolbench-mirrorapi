#!/usr/bin/env python3
"""Prepare and audit official MirrorAPI training data without modifying raw files."""
import argparse
import hashlib
import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw" / "MirrorAPI-Training"
PREPARED_DIR = REPO_ROOT / "data" / "prepared"
LLAMAFACTORY_DATASET_INFO = REPO_ROOT / "LLaMA-Factory" / "data" / "dataset_info.json"
DATASET_REPO = "https://huggingface.co/datasets/stabletoolbench/MirrorAPI-Training"
REVISION = "94d2a05cbd7f52621c358e0e843bdfa1fd22f945"
REQUIRED_FIELDS = ("system", "instruction", "output")
TRAINING_FILES = {
    "train_sft.json": {"dataset": "mirrorapi_sft_train", "purpose": "standard SFT MirrorAPI examples"},
    "train_cot.json": {"dataset": "mirrorapi_cot_train", "purpose": "CoT-mode MirrorAPI examples"},
    "train_augment.json": {"dataset": "mirrorapi_augment_train", "purpose": "augmentation data; official role in final checkpoint is partially documented"},
    "train_cache.json": {"dataset": "mirrorapi_cache_train", "purpose": "MirrorAPI-Cache data; excluded from MirrorAPI SFT reproduction"},
}


def load_official_training_file(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON list in {path}")
    return data


def validate_training_record(record: dict, index: int, source: str) -> list[str]:
    errors = []
    if not isinstance(record, dict):
        return [f"{source}[{index}] is not an object"]
    for field in REQUIRED_FIELDS:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{source}[{index}] has missing/empty {field}")
    return errors


def count_duplicate_records(records: list[dict]) -> int:
    seen = set()
    duplicates = 0
    for record in records:
        key = json.dumps(record, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        if digest in seen:
            duplicates += 1
        else:
            seen.add(digest)
    return duplicates


def create_deterministic_subset(records: list[dict], output_path: Path, count: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subset = records[:count]
    output_path.write_text(json.dumps(subset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def register_llamafactory_dataset(dataset_info_path: Path, entries: dict[str, str]) -> None:
    dataset_info_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(dataset_info_path.read_text(encoding="utf-8")) if dataset_info_path.exists() else {}
    backup = dataset_info_path.with_suffix(".json.bak")
    if dataset_info_path.exists() and not backup.exists():
        shutil.copy2(dataset_info_path, backup)
    for name, file_name in entries.items():
        data[name] = {"file_name": file_name, "columns": {"prompt": "instruction", "response": "output", "system": "system"}}
    dataset_info_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_dataset_report(report: dict) -> None:
    PREPARED_DIR.mkdir(parents=True, exist_ok=True)
    (PREPARED_DIR / "training_data_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_data(download: bool) -> None:
    if RAW_DIR.exists() and all((RAW_DIR / f).exists() for f in TRAINING_FILES):
        return
    if not download:
        missing = [f for f in TRAINING_FILES if not (RAW_DIR / f).exists()]
        raise FileNotFoundError(f"Missing official training files under {RAW_DIR}: {missing}. Re-run with --download after disk/path review.")
    RAW_DIR.parent.mkdir(parents=True, exist_ok=True)
    if not RAW_DIR.exists():
        subprocess.run(["git", "clone", DATASET_REPO, str(RAW_DIR)], check=True)
    subprocess.run(["git", "-C", str(RAW_DIR), "checkout", REVISION], check=True)
    subprocess.run(["git", "-C", str(RAW_DIR), "lfs", "pull"], check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Download official training dataset to data/raw/ after disk/path review.")
    parser.add_argument("--validate-only", action="store_true", help="Validate existing files without creating subsets or registration.")
    parser.add_argument("--llamafactory-dataset-info", type=Path, default=LLAMAFACTORY_DATASET_INFO)
    args = parser.parse_args()

    ensure_data(args.download)
    report = {"dataset_id": "stabletoolbench/MirrorAPI-Training", "revision": REVISION, "files": {}}
    registration = {}
    overall_errors = []
    loaded = {}
    for filename, meta in TRAINING_FILES.items():
        path = RAW_DIR / filename
        records = load_official_training_file(path)
        loaded[filename] = records
        errors = []
        for index, record in enumerate(records):
            errors.extend(validate_training_record(record, index, filename))
        field_names = sorted({key for record in records[:1000] if isinstance(record, dict) for key in record.keys()})
        report["files"][filename] = {
            "rows": len(records),
            "bytes": path.stat().st_size,
            "fields_seen_first_1000": field_names,
            "duplicate_exact_records": count_duplicate_records(records),
            "empty_or_invalid_records": len(errors),
            "sample_indices_inspected": list(range(min(5, len(records)))),
            "purpose": meta["purpose"],
        }
        overall_errors.extend(errors[:20])
        rel = os.path.relpath(path, args.llamafactory_dataset_info.parent).replace(os.sep, chr(47))
        registration[meta["dataset"]] = rel

    if not args.validate_only:
        create_deterministic_subset(loaded["train_sft.json"], PREPARED_DIR / "sft_debug_32.json", 32)
        create_deterministic_subset(loaded["train_cot.json"], PREPARED_DIR / "cot_debug_16.json", 16)
        registration.update({
            "mirrorapi_sft_debug": "../../data/prepared/sft_debug_32.json",
            "mirrorapi_cot_debug": "../../data/prepared/cot_debug_16.json",
            "mirrorapi_joint_train": "../../data/prepared/joint_sft_cot_train.json",
        })
        register_llamafactory_dataset(args.llamafactory_dataset_info, registration)
    write_dataset_report(report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if overall_errors:
        print("Validation errors (first 20):", file=sys.stderr)
        print("\n".join(overall_errors[:20]), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
