#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent


def load_benchmark_config() -> dict:
    with (REPO_ROOT / "benchmark_config.json").open() as handle:
        return json.load(handle)


def resolve_path(config: dict, key: str) -> Path:
    path = Path(config[key])
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def load_sft_split(config: dict, split: str) -> tuple[dict, list, list]:
    split_config = config["splits"][split]
    dataset_path = resolve_path(config, "dataset_path")
    test_file = dataset_path / split_config["test_file"]
    reference_file = dataset_path / split_config["reference_file"]
    if not test_file.exists():
        raise FileNotFoundError(f"Official test file not found: {test_file}")
    if not reference_file.exists():
        raise FileNotFoundError(f"Official reference file not found: {reference_file}")
    samples = json.loads(test_file.read_text())
    references = [json.loads(line) for line in reference_file.read_text().splitlines() if line.strip()]
    return split_config, samples, references


def verify_checkpoint_and_tools(config: dict) -> tuple[Path, Path, Path]:
    model_path = resolve_path(config, "model_path")
    dataset_path = resolve_path(config, "dataset_path")
    llamafactory_path = resolve_path(config, "llamafactory_path")
    if not model_path.exists():
        raise FileNotFoundError(f"MirrorAPI checkpoint not found: {model_path}")
    if not dataset_path.exists():
        raise FileNotFoundError(f"MirrorAPI-Bench checkout not found: {dataset_path}")
    if not llamafactory_path.exists():
        raise FileNotFoundError(f"LLaMA-Factory checkout not found: {llamafactory_path}")
    if not (llamafactory_path / "src/train.py").exists():
        raise FileNotFoundError(f"LLaMA-Factory train.py not found: {llamafactory_path / 'src/train.py'}")
    return model_path, dataset_path, llamafactory_path


def register_llamafactory_dataset(config: dict, split_config: dict, llamafactory_path: Path) -> None:
    dataset_info = llamafactory_path / "data/dataset_info.json"
    data = json.loads(dataset_info.read_text())
    data[split_config["dataset_name"]] = {
        "file_name": f"../../benchmark/MirrorAPI-Bench/{split_config['test_file']}",
        "columns": {"prompt": "instruction", "response": "output", "system": "system"},
    }
    dataset_info.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def build_llamafactory_command(config: dict, split: str, split_config: dict, model_path: Path) -> list[str]:
    output_dir = f"../benchmark/runs/sft_{split}/output"
    command = [
        "torchrun",
        "--master_port", "29521",
        "--nproc_per_node", "1",
        "--nnodes", "1",
        "src/train.py",
        "--do_predict",
        "--predict_with_generate",
        "--model_name_or_path", str(model_path),
        "--eval_dataset", split_config["dataset_name"],
        "--stage", "sft",
        "--template", config["template"],
        "--preprocessing_num_workers", "16",
        "--finetuning_type", "full",
        "--output_dir", output_dir,
        "--max_new_tokens", str(config["max_new_tokens"]),
        "--bf16",
        "--report_to", "none",
        "--flash_attn", "auto",
        "--cutoff_len", str(config["cutoff_len"]),
        "--seed", str(config["seed"]),
        "--per_device_eval_batch_size", str(config["batch_size"]),
        "--overwrite_cache",
        "--do_sample", str(config["do_sample"]).lower(),
        "--temperature", str(config["temperature"]),
        "--top_p", str(config["top_p"]),
        "--top_k", str(config["top_k"]),
    ]
    return command


def run_logged_command(command: list[str], cwd: Path, log_file: Path | None = None) -> str:
    print("$ " + " ".join(command), flush=True)
    output_lines = []
    with subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
        for line in proc.stdout:
            print(line, end="", flush=True)
            output_lines.append(line)
            if log_file is not None:
                with log_file.open("a", encoding="utf-8") as handle:
                    handle.write(line)
        code = proc.wait()
    if code != 0:
        raise subprocess.CalledProcessError(code, command)
    return "".join(output_lines)


def run_sft_inference(config: dict, split: str, split_config: dict, model_path: Path, llamafactory_path: Path, force: bool) -> float:
    output_dir = REPO_ROOT / f"benchmark/runs/sft_{split}/output"
    result_dir = REPO_ROOT / f"results/{split}"
    runtime_log = result_dir / "runtime.log"
    if output_dir.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing output directory: {output_dir}")
    if result_dir.exists() and any(result_dir.iterdir()) and not force:
        raise FileExistsError(f"Refusing to overwrite existing result directory: {result_dir}")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    if result_dir.exists() and force:
        shutil.rmtree(result_dir)
    output_dir.mkdir(parents=True)
    result_dir.mkdir(parents=True)
    command = build_llamafactory_command(config, split, split_config, model_path)
    runtime_log.write_text(" ".join(command) + "\n")
    start = time.monotonic()
    run_logged_command(command, cwd=llamafactory_path, log_file=runtime_log)
    elapsed = round(time.monotonic() - start, 3)
    with runtime_log.open("a", encoding="utf-8") as handle:
        handle.write(f"TOTAL_RUNTIME_SECONDS={elapsed}\n")
        handle.write("Training performed: NO\n")
        handle.write("Inference only: YES\n")
    shutil.copyfile(output_dir / "generated_predictions.jsonl", result_dir / "predictions.jsonl")
    return elapsed


def convert_official_predictions(config: dict, split: str) -> None:
    dataset_path = resolve_path(config, "dataset_path")
    result_dir = REPO_ROOT / f"results/{split}"
    command = [
        sys.executable,
        str(dataset_path / "scripts/convert_format.py"),
        "--input_file", str(result_dir / "predictions.jsonl"),
        "--output_file", str(result_dir / "converted_predictions.jsonl"),
    ]
    run_logged_command(command, cwd=REPO_ROOT)


def run_official_metrics(config: dict, split: str, split_config: dict) -> None:
    dataset_path = resolve_path(config, "dataset_path")
    result_dir = REPO_ROOT / f"results/{split}"
    command = [
        sys.executable,
        str(dataset_path / "scripts/compute_metrics.py"),
        "--predictions", str(result_dir / "converted_predictions.jsonl"),
        "--references", str(dataset_path / split_config["reference_file"]),
    ]
    output = run_logged_command(command, cwd=Path("/tmp"))
    (result_dir / "metrics.txt").write_text(output)


def parse_metric(metrics_text: str, key: str) -> float | None:
    match = re.search(rf"'{re.escape(key)}':\s*([0-9.]+)", metrics_text)
    return float(match.group(1)) if match else None


def validate_prediction_count(split: str, expected: int, references: list) -> tuple[list, list]:
    result_dir = REPO_ROOT / f"results/{split}"
    predictions = [json.loads(line) for line in (result_dir / "predictions.jsonl").read_text().splitlines() if line.strip()]
    converted = [json.loads(line) for line in (result_dir / "converted_predictions.jsonl").read_text().splitlines() if line.strip()]
    if len(predictions) != expected:
        raise ValueError(f"Prediction count mismatch: expected {expected}, got {len(predictions)}")
    if len(converted) != expected:
        raise ValueError(f"Converted count mismatch: expected {expected}, got {len(converted)}")
    if len(references) != expected:
        raise ValueError(f"Reference count mismatch: expected {expected}, got {len(references)}")
    prompts = [item.get("prompt") for item in predictions]
    if len(prompts) != len(set(prompts)):
        raise ValueError("Duplicate prompts detected")
    return predictions, converted


def analyze_json_outputs(predictions: list) -> dict:
    strict_valid = 0
    json_like_invalid = 0
    empty_outputs = 0
    tracebacks = 0
    for record in predictions:
        text = record.get("predict") or ""
        if not text.strip():
            empty_outputs += 1
        if "Traceback (most recent call last)" in text:
            tracebacks += 1
        try:
            parsed = json.loads(text)
            if parsed:
                strict_valid += 1
        except Exception:
            if text.strip().startswith("{") or "RESPONSE:" in text or "ERROR:" in text:
                json_like_invalid += 1
    return {
        "strict_valid_json_outer": strict_valid,
        "json_like_invalid_outer": json_like_invalid,
        "empty_outputs": empty_outputs,
        "traceback_outputs": tracebacks,
    }


def save_split_summary(config: dict, split: str, split_config: dict, samples: list, references: list, elapsed: float, predictions: list, converted: list) -> None:
    result_dir = REPO_ROOT / f"results/{split}"
    metrics_text = (result_dir / "metrics.txt").read_text()
    all_results = REPO_ROOT / f"benchmark/runs/sft_{split}/output/all_results.json"
    llamafactory_metrics = json.loads(all_results.read_text()) if all_results.exists() else {}
    bleu = parse_metric(metrics_text, "bleu-4")
    official = split_config["official_bleu4"]
    difference = bleu - official if bleu is not None else None
    json_analysis = analyze_json_outputs(predictions)
    summary = {
        "split": split_config["test_file"],
        "official_reference": split_config["reference_file"],
        "paper_official_bleu4": official,
        "reproduced_bleu4": bleu,
        "absolute_difference": difference,
        "relative_difference_percent": difference / official * 100 if difference is not None else None,
        "input_count": len(samples),
        "prediction_count": len(predictions),
        "converted_count": len(converted),
        "reference_count": len(references),
        "duplicate_prompts": 0,
        "missing_outputs": 0,
        "prediction_failures": json_analysis["empty_outputs"] + json_analysis["traceback_outputs"],
        "rouge": {
            "rouge-1": parse_metric(metrics_text, "rouge-1"),
            "rouge-2": parse_metric(metrics_text, "rouge-2"),
            "rouge-l": parse_metric(metrics_text, "rouge-l"),
        },
        "llamafactory_metrics": llamafactory_metrics,
        "total_runtime_seconds_wall": elapsed,
        "average_latency_seconds_from_wall": elapsed / len(predictions),
        "average_latency_seconds_from_predict_runtime": (
            llamafactory_metrics.get("predict_runtime") / len(predictions)
            if isinstance(llamafactory_metrics.get("predict_runtime"), (int, float))
            else None
        ),
        "median_latency_seconds": None,
        "median_latency_note": "Not available: official LLaMA-Factory prediction output does not emit per-sample timestamps.",
        "training_performed": False,
        "inference_only": True,
        "checkpoint_path": config["model_path"],
        "model_revision": config["model_revision"],
        "dataset_revision": config["dataset_revision"],
        "llamafactory_revision": config["llamafactory_commit"],
        "generation": {
            "do_sample": config["do_sample"],
            "temperature": config["temperature"],
            "top_p": config["top_p"],
            "top_k": config["top_k"],
            "max_new_tokens": config["max_new_tokens"],
            "cutoff_len": config["cutoff_len"],
            "template": config["template"],
            "seed": config["seed"],
            "precision": config["precision"],
        },
        **json_analysis,
    }
    (result_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one official MirrorAPI-Bench SFT split through LLaMA-Factory do_predict.")
    parser.add_argument("--split", required=True, choices=["id_high", "id_medium", "id_low", "ood_failed", "ood_successful"])
    parser.add_argument("--force", action="store_true", help="Overwrite existing result directory and LLaMA-Factory output for this split.")
    args = parser.parse_args()

    config = load_benchmark_config()
    split_config, samples, references = load_sft_split(config, args.split)
    model_path, _, llamafactory_path = verify_checkpoint_and_tools(config)
    register_llamafactory_dataset(config, split_config, llamafactory_path)
    elapsed = run_sft_inference(config, args.split, split_config, model_path, llamafactory_path, args.force)
    convert_official_predictions(config, args.split)
    run_official_metrics(config, args.split, split_config)
    predictions, converted = validate_prediction_count(args.split, split_config["samples"], references)
    save_split_summary(config, args.split, split_config, samples, references, elapsed, predictions, converted)
    print(f"{args.split}: complete")


if __name__ == "__main__":
    main()
