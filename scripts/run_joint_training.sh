#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
audit="$repo_root/docs/training_data_audit.md"
if ! grep -q "joint_sft_cot status: VERIFIED" "$audit" 2>/dev/null; then
  echo "Joint training is blocked: official SFT+CoT(+augment) composition is not fully verified in docs/training_data_audit.md" >&2
  exit 3
fi
exec bash "$repo_root/scripts/run_sft_training.sh" --config configs/joint_sft_cot_full.yaml
