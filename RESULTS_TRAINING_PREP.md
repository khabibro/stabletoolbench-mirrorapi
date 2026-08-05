# Tiny SFT Training Prep Report

This report tracks the corrected launcher, LoRA diagnostic smoke test, and multi-GPU full-SFT preparation.

## Launcher
- LLaMA-Factory YAML invocation bug fixed: YES
- Evidence: LLaMA-Factory v0.9.3 parser reads `sys.argv[1]` when it ends with `.yaml`; official examples use `llamafactory-cli train examples/...yaml key=value`.

## LoRA Smoke Test
- Configuration: `configs/lora_sft_smoke_test.yaml`
- Purpose: diagnostic only; not paper reproduction.
- Result: PASSED
- Checkpoint created: YES, `/home/khabibillo/checkpoints/lora_sft_smoke_test-20260805-143057`
- Checkpoint reload successful: YES
- Inference successful: YES; generated JSON-like output for a simple API prompt
- Evaluation successful: YES on `id_high` via merged checkpoint `/home/khabibillo/checkpoints/lora_sft_smoke_test-20260805-143057-merged`; artifacts saved under `/home/khabibillo/checkpoints/lora_sft_smoke_test-20260805-143057/eval_id_high`


## LoRA Smoke Metrics
- Dataset: `mirrorapi_sft_debug`
- Samples: 32
- Max steps: 3
- Trainable parameters: 20,185,088 / 7,635,801,600 (0.2643%)
- Losses: 0.4915, 1.4075, 1.8892
- Final train loss: 1.2627
- Runtime: 2.605 seconds
- Adapter checkpoint size: 339 MB
- Merged evaluation checkpoint size: 15 GB
- Evaluation split used only for pipeline validation: `id_high`
- Evaluation completed: YES; BLEU/ROUGE were produced but are not performance claims.

## Multi-GPU Full SFT
- Configuration: `configs/full_sft_zero3.yaml`
- Method: full-parameter SFT with LLaMA-Factory-supported DeepSpeed ZeRO-3.
- GPUs: 0,1,3 only; GPU 2 remains excluded.
- Launch status: NOT LAUNCHED.

## Expected VRAM Usage
- Qwen2.5-7B parameters: ~7.62B.
- bf16 model weights: ~15.2 GB total.
- bf16 gradients: ~15.2 GB total.
- Adam optimizer states: ~60.9 GB total for fp32 exp_avg and exp_avg_sq.
- ZeRO-3 shards parameters, gradients, and optimizer states across 3 GPUs, so the persistent model/grad/optimizer state is roughly 30-35 GB/GPU before activations and framework overhead.
- Activations with cutoff 2560 and per-device batch 1 should fit more comfortably than the failed one-GPU full Adam run, but must still be validated with a short ZeRO-3 dry/smoke run before full training.

## Remaining Blockers Before Official Full Training
- Exact official hyperparameters and data-mixture recipe remain partially unverified.
- DeepSpeed package was not present in the global Python check; it must be confirmed in the actual training venv before ZeRO-3 launch.
- The expensive full-SFT run has not been launched.
