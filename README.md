# stabletoolbench-mirrorapi

This repository reproduces only the minimal MirrorAPI virtual API execution part of StableToolBench.

It runs one ToolBench-style API request through:

```text
run_test_request.py
        ↓
StableToolBench MirrorAPI server
        ↓
vLLM
        ↓
MirrorAPI model
        ↓
simulated JSON response
```

The goal is to verify that the open-source StableToolBench MirrorAPI server can accept one ToolBench-style call and return a structured simulated response without a live RapidAPI endpoint or paid OpenAI API.

## Included

```text
ToolBench-style request
→ StableToolBench MirrorAPI server
→ MirrorAPI model through vLLM
→ simulated structured API response
```

## Excluded

- Full StableToolBench evaluation
- ToolLLaMA inference
- API retriever training
- Paid OpenAI APIs
- GPT evaluation
- SoPR / SoWR
- Full datasets
- All benchmark tasks

## Verified Upstream Details

Official StableToolBench repository:

```text
https://github.com/THUNLP-MT/StableToolBench
```

Pinned commit:

```text
aa4ed9f4737ad98bd706663f01d63623c3427812
```

Verified official server entry point at that commit:

```text
server/main_mirrorapi.py
```

Verified config path:

```text
server/config_mirrorapi.yml
```

Verified request endpoint:

```text
POST http://127.0.0.1:8080/virtual
```

The README says `python main_mirrorapi.py`, but the actual file is under `server/`. This repo runs it from inside the official `server` directory so its relative config lookup works.

Paper vs repository scope:

- The ACL 2024 StableToolBench paper describes the original virtual API server as a response cache plus real API fallback plus GPT-based API simulator.
- The current official repository later adds MirrorAPI as an open-source simulator path.
- This repository targets only that later MirrorAPI smoke-test path. It does not reproduce the original paper cache path, real API fallback, GPT-based simulator, SoPR, or SoWR.

## Test Request

`test_request.json` uses the official README test request:

```json
{
  "category": "Artificial_Intelligence_Machine_Learning",
  "tool_name": "TTSKraken",
  "api_name": "List Languages",
  "tool_input": "{}",
  "strip": "truncate",
  "toolbench_key": ""
}
```

Selected request:

- Category: `Artificial_Intelligence_Machine_Learning`
- Tool: `TTSKraken`
- API endpoint: `List Languages`
- Endpoint description: `Get a list of currently supported languages. We are constantly adding more every few weeks.`
- Required parameters: none
- Optional parameters: none
- Official tool-definition path after extracting ToolEnv2404: `toolenv2404_filtered/Artificial_Intelligence_Machine_Learning/ttskraken.json`
- Request URL: `POST /virtual`
- Expected outer response format: `{"error": "...", "response": ...}`

The full tool metadata is not committed here. The official `stabletoolbench/ToolEnv2404` archive is about 11.7 MB and contains the verified `TTSKraken` definition. On the GPU server, download or locate that tools folder and set `TOOLS_PATH` to the extracted `toolenv2404_filtered` directory.

## Mac Preparation

The Mac only prepares and validates this small codebase. Do not install vLLM, CUDA packages, model checkpoints, or large datasets on the Mac.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m py_compile run_test_request.py
bash -n start_vllm.sh start_mirrorapi_server.sh
python run_test_request.py --dry-run
```

## GPU Server Setup

Clone and prepare:

```bash
git clone https://github.com/khabibro/stabletoolbench-mirrorapi.git
cd stabletoolbench-mirrorapi
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

Clone the pinned official StableToolBench source:

```bash
git clone https://github.com/THUNLP-MT/StableToolBench stabletoolbench
git -C stabletoolbench checkout aa4ed9f4737ad98bd706663f01d63623c3427812
python -m pip install -r stabletoolbench/server/requirements.txt
```

Install vLLM only after checking your server CUDA/Python compatibility:

```bash
python -m pip install vllm
```

Download or locate these server-side resources manually:

- MirrorAPI checkpoint: `stabletoolbench/MirrorAPI` from Hugging Face.
- Tools folder: official StableToolBench ToolEnv2404 tools or ToolBench tools.

Do not commit model files, tools data, caches, logs, or generated responses.

Create `.env`:

```bash
cp .env.example .env
```

Edit `.env` with real server paths:

```bash
MIRRORAPI_URL=http://127.0.0.1:8080
VLLM_URL=http://127.0.0.1:12345/v1
VLLM_API_KEY=EMPTY
MIRRORAPI_MODEL_PATH=/path/to/MirrorAPI
MIRRORAPI_MODEL_NAME=MirrorAPI
MIRRORAPI_TEMPERATURE=0.1
STABLETOOLBENCH_PATH=/path/to/stabletoolbench
TOOLS_PATH=/path/to/tools
CUDA_VISIBLE_DEVICES=
```

Load it:

```bash
set -a
. ./.env
set +a
```

## Terminal Layout

Terminal 1: start vLLM

```bash
cd stabletoolbench-mirrorapi
set -a
. ./.env
set +a
. .venv/bin/activate
./start_vllm.sh
```

Terminal 2: start StableToolBench MirrorAPI server

```bash
cd stabletoolbench-mirrorapi
set -a
. ./.env
set +a
. .venv/bin/activate
./start_mirrorapi_server.sh
```

Terminal 3: run test request

```bash
cd stabletoolbench-mirrorapi
set -a
. ./.env
set +a
. .venv/bin/activate
python run_test_request.py
```

## Expected Success Output

```text
MirrorAPI reachable: PASS
Request accepted: PASS
Valid JSON returned: PASS
Response structure valid: PASS
Paid API used: NO
Overall test: PASS
```

The response is saved to `test_response.json`, which is ignored by Git.

## Troubleshooting

- vLLM endpoint unavailable: confirm Terminal 1 is still running and `VLLM_URL` ends in `/v1`.
- Wrong model path: confirm `MIRRORAPI_MODEL_PATH` points to the downloaded MirrorAPI checkpoint.
- Wrong tools path: confirm `TOOLS_PATH` points to the official tools folder and contains the selected tool definition.
- MirrorAPI server not running: confirm Terminal 2 printed the `/virtual` endpoint and did not exit.
- Wrong request schema: compare `test_request.json` with the schema in `stabletoolbench/server/main_mirrorapi.py`.
- Port already in use: change `MIRRORAPI_URL` or vLLM port and restart the matching service.
- Insufficient GPU memory: use a server with more VRAM or a vLLM configuration appropriate for your hardware.

## Reproducibility Notes

This repo pins the official StableToolBench source by commit and keeps the codebase minimal. The MirrorAPI checkpoint and tools data are external resources and must be provided on the GPU server.

Simulated responses are structurally realistic MirrorAPI outputs. They are not guaranteed real-world facts.
