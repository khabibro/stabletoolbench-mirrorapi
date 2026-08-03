# MirrorAPI SFT BLEU Reproduction

Local project name: `mirrorapi-sft-bleu`  
GitHub repository: `stabletoolbench-mirrorapi`

## Goal

This repository reproduces the MirrorAPI SFT BLEU-4 results reported in Table 3 of the paper “StableToolBench-MirrorAPI: Modeling Tool Environments as Mirrors of 7,000+ Real-World APIs.”

## What Was Reproduced

- Official MirrorAPI checkpoint: `stabletoolbench/MirrorAPI`
- Official MirrorAPI-Bench SFT splits: `stabletoolbench/MirrorAPI-Bench`
- LLaMA-Factory inference-only `do_predict` path
- Official prediction conversion script
- Official BLEU-4 and ROUGE metric script
- Paper comparison for all five SFT rows

## What Was Not Reproduced

This repository does not reproduce the original StableToolBench GPT simulator, StableToolBench response cache, real API fallback, ToolLLaMA, API retrieval, SoPR, SoWR, FAC, MirrorAPI CoT, model training, fine-tuning, RapidAPI, paid GPT evaluation, or paid cosine similarity.

## Architecture

```text
MirrorAPI-Bench SFT split
        ↓
LLaMA-Factory do_predict
        ↓
Official MirrorAPI checkpoint
        ↓
Raw predictions
        ↓
Official conversion
        ↓
Official BLEU-4 / ROUGE
        ↓
Paper comparison
```

## Repository Structure

```text
README.md                    project overview and run instructions
RESULTS.md                   human-readable reproduced scores
requirements.txt             lightweight local orchestration note
benchmark_config.json        pinned paths, revisions, splits, and generation settings
run_sft_benchmark.py         runs one official SFT split end to end
evaluate_sft_results.sh      reruns official conversion and metrics for an existing split
official_sources.md          official papers, repositories, revisions, and scripts
results/                     committed reproduction artifacts
```

The downloaded `LLaMA-Factory/` checkout and `benchmark/MirrorAPI-Bench/` dataset repository are intentionally ignored by Git and must be reconstructed from the documented revisions.

## Environment

The completed reproduction used:

- GPU: NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition
- Driver/CUDA: NVIDIA driver `580.95.05`, CUDA `13.0`
- Python: `3.10.12`
- PyTorch: `2.11.0+cu130`
- Transformers: `4.52.4`
- LLaMA-Factory: `v0.9.3`, commit `ca75f1edf3cb50343ed1c98605141c3e22075b5f`
- MirrorAPI checkpoint revision: `f181ec673e2346898a0d6453164604bb8372c4fd`
- MirrorAPI-Bench revision: `adceeb3a567d1f1714fa65c0772ca95a2b0f7cf7`

## Installation

```bash
git clone https://github.com/khabibro/stabletoolbench-mirrorapi.git mirrorapi-sft-bleu
cd mirrorapi-sft-bleu
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

Install LLaMA-Factory from the verified compatible revision:

```bash
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
git checkout ca75f1edf3cb50343ed1c98605141c3e22075b5f
pip install -e '.[torch,metrics]'
cd ..
```

Fetch the official benchmark dataset repository without committing it:

```bash
mkdir -p benchmark
git clone https://huggingface.co/datasets/stabletoolbench/MirrorAPI-Bench benchmark/MirrorAPI-Bench
cd benchmark/MirrorAPI-Bench
git checkout adceeb3a567d1f1714fa65c0772ca95a2b0f7cf7
cd ../..
```

Place or verify the MirrorAPI checkpoint outside the repository:

```text
/home/khabibillo/models/stabletoolbench-MirrorAPI
```

The exact paper-time LLaMA-Factory revision was not documented in the official sources available during setup. Revision `ca75f1edf3cb50343ed1c98605141c3e22075b5f` was selected because it is a compatible `v0.9.3` release for Python `3.10.12`.

## Running One Split

```bash
source .venv/bin/activate
CUDA_VISIBLE_DEVICES=0 python run_sft_benchmark.py --split id_high
```

The runner refuses to overwrite an existing split result unless `--force` is passed.

## Running All Splits

Run sequentially:

```bash
CUDA_VISIBLE_DEVICES=0 python run_sft_benchmark.py --split id_high
CUDA_VISIBLE_DEVICES=0 python run_sft_benchmark.py --split id_medium
CUDA_VISIBLE_DEVICES=0 python run_sft_benchmark.py --split id_low
CUDA_VISIBLE_DEVICES=0 python run_sft_benchmark.py --split ood_failed
CUDA_VISIBLE_DEVICES=0 python run_sft_benchmark.py --split ood_successful
```

## Evaluation

To rerun official conversion and metrics for an existing prediction file:

```bash
source .venv/bin/activate
bash evaluate_sft_results.sh id_high
```

This uses the official `convert_format.py` and `compute_metrics.py` from MirrorAPI-Bench. It does not implement a custom BLEU metric.

## Results

See `RESULTS.md`.

## Reproduction Status

```text
ID High: completed
ID Medium: completed
ID Low: completed
OOD Failed: completed
OOD Successful: completed
```

## Limitations

- The exact original LLaMA-Factory revision used by the paper was unavailable.
- Paid cosine similarity was not run.
- GPT observation-following score was not run.
- Raw model outputs can be malformed strict JSON while still being accepted by the official conversion script.
- Exact byte-for-byte output parity is not claimed.

## Citation

Use the MirrorAPI paper, StableToolBench paper/repository, the `stabletoolbench/MirrorAPI` model card, and the `stabletoolbench/MirrorAPI-Bench` dataset card. Exact sources and revisions are listed in `official_sources.md`.
