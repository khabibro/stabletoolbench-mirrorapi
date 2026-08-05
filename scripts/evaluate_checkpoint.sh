#!/usr/bin/env bash
set -euo pipefail
checkpoint=""; split=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --checkpoint) checkpoint="$2"; shift 2 ;;
    --split) split="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$checkpoint" && -n "$split" ]] || { echo "Usage: bash scripts/evaluate_checkpoint.sh --checkpoint <base|official|/path> --split <split>" >&2; exit 2; }
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
case "$checkpoint" in
  base) model_path="${MIRRORAPI_BASE_MODEL:-/home/khabibillo/models/Qwen2.5-7B-Instruct}" ;;
  official) model_path="${MIRRORAPI_OFFICIAL_MODEL:-/home/khabibillo/models/stabletoolbench-MirrorAPI}" ;;
  *) model_path="$checkpoint" ;;
esac
[[ -d "$model_path" ]] || { echo "Missing checkpoint: $model_path" >&2; exit 1; }
export MIRRORAPI_MODEL_PATH="$model_path"
python3 "$repo_root/run_sft_benchmark.py" --split "$split" --force
