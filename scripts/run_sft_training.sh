#!/usr/bin/env bash
set -euo pipefail
config=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config) config="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$config" ]] || { echo "Usage: bash scripts/run_sft_training.sh --config configs/sft_smoke_test.yaml" >&2; exit 2; }
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ -f "$repo_root/$config" || -f "$config" ]] || { echo "Missing config: $config" >&2; exit 1; }
config_path="$config"; [[ -f "$config_path" ]] || config_path="$repo_root/$config"
config_path="$(readlink -f "$config_path")"
llamafactory_dir="${LLAMAFACTORY_DIR:-$repo_root/LLaMA-Factory}"
base_model="${MIRRORAPI_BASE_MODEL:-/home/khabibillo/models/Qwen2.5-7B-Instruct}"
output_root="${MIRRORAPI_OUTPUT_ROOT:-/home/khabibillo/checkpoints}"
run_name="$(basename "$config_path" .yaml)-$(date +%Y%m%d-%H%M%S)"
output_dir="$output_root/$run_name"
log_dir="$repo_root/logs/training/$run_name"
[[ -d "$llamafactory_dir" ]] || { echo "Missing LLaMA-Factory: $llamafactory_dir" >&2; exit 1; }
[[ -f "$llamafactory_dir/src/train.py" ]] || { echo "Missing LLaMA-Factory train.py" >&2; exit 1; }
[[ -d "$base_model" ]] || { echo "Missing base model: $base_model" >&2; exit 1; }
[[ ! -e "$output_dir" ]] || { echo "Refusing to overwrite checkpoint dir: $output_dir" >&2; exit 1; }
python3 "$repo_root/scripts/validate_training_setup.py" --base-model "$base_model" --output-dir "$output_dir"
mkdir -p "$log_dir" "$output_dir"
nvidia-smi > "$log_dir/nvidia-smi.before.txt"
python3 --version > "$log_dir/python-version.txt"
(cd "$repo_root" && git status --short && git log -1 --oneline) > "$log_dir/git-state.txt"
(cd "$llamafactory_dir" && git rev-parse HEAD && git describe --tags --always --dirty) > "$log_dir/llamafactory-revision.txt"
echo "Resolved config: $config_path" | tee "$log_dir/command.txt"
echo "Output dir: $output_dir" | tee -a "$log_dir/command.txt"
cd "$llamafactory_dir"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
nproc_per_node="${NPROC_PER_NODE:-1}"
master_port="${MASTER_PORT:-29531}"
if [[ "${FORCE_TORCHRUN:-0}" == "1" || "$nproc_per_node" != "1" ]]; then
  cmd=(torchrun --nnodes "${NNODES:-1}" --nproc_per_node "$nproc_per_node" --master_port "$master_port" src/train.py "$config_path" do_train=true model_name_or_path="$base_model" output_dir="$output_dir")
else
  cmd=(python3 src/train.py "$config_path" do_train=true model_name_or_path="$base_model" output_dir="$output_dir")
fi
printf '%q ' "${cmd[@]}" | tee -a "$log_dir/command.txt"; echo | tee -a "$log_dir/command.txt"
"${cmd[@]}" 2>&1 | tee "$log_dir/train.log"
cp -f "$output_dir/trainer_state.json" "$log_dir/trainer_state.json" 2>/dev/null || true
find "$output_dir" -name trainer_state.json -print -quit | xargs -r -I{} cp -f {} "$log_dir/trainer_state.json"
