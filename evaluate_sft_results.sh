#!/usr/bin/env bash
set -euo pipefail

split="${1:-}"
if [[ -z "$split" ]]; then
  echo "Usage: $0 <id_high|id_medium|id_low|ood_failed|ood_successful>" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
config="$repo_root/benchmark_config.json"

python_bin="${PYTHON:-python}"
dataset_path="$($python_bin -c 'import json; print(json.load(open("'"$config"'"))["dataset_path"])')"
test_file="$($python_bin -c 'import json; c=json.load(open("'"$config"'")); print(c["splits"]["'"$split"'"]["test_file"])')"
reference_file="$($python_bin -c 'import json; c=json.load(open("'"$config"'")); print(c["splits"]["'"$split"'"]["reference_file"])')"

result_dir="$repo_root/results/$split"
predictions="$result_dir/predictions.jsonl"
converted="$result_dir/converted_predictions.jsonl"
metrics="$result_dir/metrics.txt"

if [[ ! -f "$predictions" ]]; then
  echo "Missing predictions: $predictions" >&2
  exit 1
fi
if [[ ! -f "$dataset_path/$test_file" ]]; then
  echo "Missing official test file: $dataset_path/$test_file" >&2
  exit 1
fi
if [[ ! -f "$dataset_path/$reference_file" ]]; then
  echo "Missing official reference file: $dataset_path/$reference_file" >&2
  exit 1
fi

mkdir -p "$result_dir"
"$python_bin" "$dataset_path/scripts/convert_format.py" \
  --input_file "$predictions" \
  --output_file "$converted"

(
  cd /tmp
  "$python_bin" "$dataset_path/scripts/compute_metrics.py" \
    --predictions "$converted" \
    --references "$dataset_path/$reference_file"
) | tee "$metrics"

prediction_count="$(grep -cve '^[[:space:]]*$' "$predictions")"
converted_count="$(grep -cve '^[[:space:]]*$' "$converted")"
reference_count="$(grep -cve '^[[:space:]]*$' "$dataset_path/$reference_file")"

echo "prediction_count=$prediction_count"
echo "converted_count=$converted_count"
echo "reference_count=$reference_count"
grep -E "'(rouge-1|rouge-2|rouge-l|bleu-4)'" "$metrics" || true
