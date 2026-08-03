#!/usr/bin/env bash
set -euo pipefail

: "${MIRRORAPI_MODEL_PATH:?Set MIRRORAPI_MODEL_PATH in .env}"
: "${MIRRORAPI_MODEL_NAME:?Set MIRRORAPI_MODEL_NAME in .env}"

VLLM_API_KEY="${VLLM_API_KEY:-EMPTY}"
VLLM_PORT="${VLLM_PORT:-12345}"

if [ -n "${CUDA_VISIBLE_DEVICES:-}" ]; then
  export CUDA_VISIBLE_DEVICES
  echo "CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES"
else
  echo "CUDA_VISIBLE_DEVICES is unset; vLLM will use default GPU visibility."
fi

command -v vllm >/dev/null || {
  echo "vllm command not found. Install vLLM for this server's CUDA/Python environment first."
  exit 1
}

echo "Starting vLLM on port $VLLM_PORT"
echo "Health check: curl -H 'Authorization: Bearer $VLLM_API_KEY' http://127.0.0.1:$VLLM_PORT/v1/models"

exec vllm serve "$MIRRORAPI_MODEL_PATH" \
  --api-key "$VLLM_API_KEY" \
  --port "$VLLM_PORT" \
  --served-model-name "$MIRRORAPI_MODEL_NAME"
