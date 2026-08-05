# Tiny Full-SFT ZeRO-3 Smoke Test Report

## Verdict
FULL SFT SMOKE TEST PASSED

## Environment
- GPUs used for training: physical GPU 0, GPU 1, GPU 3 only.
- Physical-to-local rank mapping: CUDA_VISIBLE_DEVICES=0,1,3 mapped local rank 0 -> physical 0, local rank 1 -> physical 1, local rank 2 -> physical 3.
- GPU 2: untouched by this run; it remained occupied by an unrelated VLLM process.
- CUDA/driver: CUDA 13.0, NVIDIA driver 580.95.05.
- PyTorch: 2.11.0+cu130.
- DeepSpeed: 0.16.9. DeepSpeed 0.19.3 was rejected by LLaMA-Factory v0.9.3 because that checkout requires deepspeed>=0.10.0,<=0.16.9.
- Transformers: 4.52.4.
- LLaMA-Factory: local checkout used by `LLaMA-Factory/src/train.py`.

## Configuration
- Base model: `/home/khabibillo/models/Qwen2.5-7B-Instruct`.
- Dataset: `mirrorapi_sft_debug` from `data/prepared/sft_debug_32.json`.
- Sample count: 32.
- Finetuning type: full; all parameters trainable.
- Trainable parameters reported: 7,615,616,512.
- ZeRO stage: 3, via `configs/deepspeed_zero3.json`.
- Batch size: per-device 1, world size 3, gradient accumulation 1, effective global batch 3.
- Cutoff length: 2560.
- Gradient checkpointing: not enabled in this smoke config.
- Offload: no CPU parameter or optimizer offload.
- Precision: bf16.
- Smoke-only config: `configs/full_sft_zero3_smoke_test.yaml`; this is not paper-comparable and does not use the full dataset.

## Distributed Validation
- Launch command used: `CUDA_VISIBLE_DEVICES=0,1,3 FORCE_TORCHRUN=1 NPROC_PER_NODE=3 MASTER_PORT=29541 bash scripts/run_sft_training.sh --config configs/full_sft_zero3_smoke_test.yaml`.
- Number of processes: 3 LLaMA-Factory worker processes under torchrun.
- NCCL status: initialized successfully through DeepSpeed/Torch distributed backend.
- ZeRO-3 activation evidence: logs reported `DeepSpeedZeroOptimizer_Stage3`, `zero_optimization_stage = 3`, `world_size = 3`, parameter partitioning, fp32 optimizer partition creation, and optimizer state initialization.
- Peak observed GPU memory during training/checkpoint save: approximately 60.7 GiB on each selected GPU.

## Training
- Steps completed: 2 / 2.
- Optimizer updates completed: YES; step 1 and step 2 both completed.
- Loss values: step 1 loss 1.2663, step 2 loss 0.6426.
- Final train loss: 0.9544.
- Learning rates: step 1 2.0e-5, step 2 1.0e-5.
- Epoch reached: 0.1818.
- Runtime: 672.4378 seconds.
- CUDA OOM: NO.
- Errors: initial launch failed before model loading because DeepSpeed 0.19.3 exceeded LLaMA-Factory v0.9.3 dependency cap; fixed by installing DeepSpeed 0.16.9 in the training venv.

## Checkpoint
- Saved: YES.
- Final checkpoint path: `/home/khabibillo/checkpoints/full_sft_zero3_smoke_test-20260805-145432`.
- Original ZeRO checkpoint paths: `checkpoint-1/global_step1` and `checkpoint-2/global_step2` under the final checkpoint directory.
- Consolidated/loadable checkpoint path: `/home/khabibillo/checkpoints/full_sft_zero3_smoke_test-20260805-145432`.
- Directly loadable: YES; LLaMA-Factory gathered 16-bit weights on save and wrote root `model-00001-of-00004.safetensors` through `model-00004-of-00004.safetensors` plus `model.safetensors.index.json`.
- Checkpoint size: 213 GiB including root loadable weights, two step checkpoints, and ZeRO optimizer states.
- Expected files found: config, generation config, tokenizer files, four safetensor shards, trainer state, train results, ZeRO shard directories, and `zero_to_fp32.py` in step checkpoints.

## Inference
- Checkpoint loaded: YES, using Transformers on one GPU.
- Output generated: YES.
- Simple output was non-empty JSON-like text. Quality was not interpreted because this was a tiny smoke test.

## Evaluation Pipeline
- Command: `bash scripts/evaluate_checkpoint.sh --checkpoint /home/khabibillo/checkpoints/full_sft_zero3_smoke_test-20260805-145432 --split id_high`.
- Loaded checkpoint: YES.
- Prediction pipeline completed: YES, 100 `id_high` examples.
- Metrics produced: YES; artifacts archived at `/home/khabibillo/checkpoints/full_sft_zero3_smoke_test-20260805-145432/eval_id_high`.
- Existing `results/id_high` was backed up before evaluation and restored afterward.
- Paper comparison performed: NO.

## Final Conclusion
The project is ready for a full-data, full-parameter MirrorAPI SFT run after choosing the exact production DeepSpeed checkpoint-save policy. The tiny ZeRO-3 run proved full-model loading, full-parameter training, optimizer state sharding, optimizer updates, checkpoint saving, checkpoint reload, inference, and benchmark pipeline compatibility.

## Remaining Blockers Before Official Full Training
- Exact official hyperparameters and data-mixture recipe remain partially unverified; do not claim exact paper parity.
- Full-data run should decide whether to keep optimizer-state checkpointing at every save step, because the tiny 2-step diagnostic consumed 213 GiB with two full ZeRO checkpoints.
- DeepSpeed must remain within the LLaMA-Factory v0.9.3 supported range unless LLaMA-Factory is upgraded and revalidated.
