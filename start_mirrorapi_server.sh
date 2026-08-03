#!/usr/bin/env bash
set -euo pipefail

: "${STABLETOOLBENCH_PATH:?Set STABLETOOLBENCH_PATH in .env}"
: "${TOOLS_PATH:?Set TOOLS_PATH in .env}"
: "${MIRRORAPI_MODEL_NAME:?Set MIRRORAPI_MODEL_NAME in .env}"

VLLM_URL="${VLLM_URL:-http://127.0.0.1:12345/v1}"
VLLM_API_KEY="${VLLM_API_KEY:-EMPTY}"
MIRRORAPI_URL="${MIRRORAPI_URL:-http://127.0.0.1:8080}"
MIRRORAPI_TEMPERATURE="${MIRRORAPI_TEMPERATURE:-0.1}"
MIRRORAPI_PORT="${MIRRORAPI_URL##*:}"
MIRRORAPI_PORT="${MIRRORAPI_PORT%%/*}"

SERVER_DIR="$STABLETOOLBENCH_PATH/server"
CONFIG_FILE="$SERVER_DIR/config_mirrorapi.yml"

test -f "$SERVER_DIR/main_mirrorapi.py" || {
  echo "Official server entry point not found: $SERVER_DIR/main_mirrorapi.py"
  exit 1
}

test -d "$TOOLS_PATH" || {
  echo "Tools path does not exist: $TOOLS_PATH"
  exit 1
}

echo "Checking vLLM endpoint at $VLLM_URL/models"
curl -fsS -H "Authorization: Bearer $VLLM_API_KEY" "$VLLM_URL/models" >/dev/null || {
  echo "vLLM is not reachable. Start ./start_vllm.sh first."
  exit 1
}

cat > "$CONFIG_FILE" <<YAML
api_key: "$VLLM_API_KEY"
api_base: "$VLLM_URL"
temperature: $MIRRORAPI_TEMPERATURE
tools_folder: "$TOOLS_PATH"
port: $MIRRORAPI_PORT
model: "$MIRRORAPI_MODEL_NAME"
YAML

echo "Starting StableToolBench MirrorAPI server at ${MIRRORAPI_URL%/}/virtual"
cd "$SERVER_DIR"
exec python main_mirrorapi.py
