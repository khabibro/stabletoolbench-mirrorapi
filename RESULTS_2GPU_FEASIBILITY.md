# 2-GPU Full-SFT ZeRO-3 Feasibility Report

## Verdict
PASS

This was a feasibility experiment only. It was not a paper reproduction, did not use the full dataset, did not use CoT or augmentation data, and did not run BLEU/ROUGE evaluation.

## Configuration
- Config: `configs/full_sft_zero3_2gpu_smoke_test.yaml`
- Source config copied from: `configs/full_sft_zero3_smoke_test.yaml`
- Base model: `/home/khabibillo/models/Qwen2.5-7B-Instruct`
- Dataset: `mirrorapi_sft_debug`
- Dataset file: `data/prepared/sft_debug_32.json`
- Samples: 32
- Prompt/template: `qwen`
- Finetuning type: full parameter
- Trainable parameters: 7,615,616,512 / 7,615,616,512
- DeepSpeed: ZeRO-3
- Precision: bf16
- GPUs: physical GPU 0 and GPU 1 only
- World size: 2
- Effective batch: 2 = 2 GPUs x per-device batch 1 x gradient accumulation 1
- Max steps: 2
- Checkpoint save: every step, full model gather enabled by existing DeepSpeed config

## Command
```bash
CUDA_VISIBLE_DEVICES=0,1 \
FORCE_TORCHRUN=1 \
NPROC_PER_NODE=2 \
MASTER_PORT=29541 \
bash scripts/run_sft_training.sh \
--config configs/full_sft_zero3_2gpu_smoke_test.yaml
```

## GPU Use
- GPU 0: used by this run
- GPU 1: used by this run
- GPU 2: not visible to the run and untouched
- GPU 3: not visible to the run and untouched

## DeepSpeed Evidence
- LLaMA-Factory reported world size 2.
- Model loading reported DeepSpeed ZeRO-3 activation.
- DeepSpeed logs reported `DeepSpeedZeroOptimizer_Stage3`.
- DeepSpeed config reported `zero_optimization_stage = 3`.
- Optimizer state initialized successfully.

## Training Result
- Model loaded: YES
- Forward pass: YES
- Backward pass: YES
- Optimizer update: YES
- CUDA OOM: NO
- Steps completed: 2 / 2
- Loss step 1: 0.9536
- Loss step 2: 0.3601
- Final train loss: 0.656881183385849
- Runtime: 721.3536 seconds
- Epoch reached: 0.125

## Memory
- Peak observed GPU memory via `nvidia-smi`: approximately 80.6 GiB on GPU 0 and 81.0 GiB on GPU 1 during checkpoint gather/save.
- DeepSpeed allocator log after ZeRO optimizer initialization: MA 28.4 GB, Max_MA 30.43 GB, CA 34.08 GB on rank 0.
- RAM remained available; heavy usage was primarily filesystem cache during checkpoint writes.

## Checkpoint
- Saved successfully: YES
- Checkpoint path: `/home/khabibillo/checkpoints/full_sft_zero3_2gpu_smoke_test-20260805-153800`
- Checkpoint size: 213 GiB including root loadable weights and two step checkpoints with ZeRO optimizer state
- Expected root files found: config, generation config, tokenizer files, `model-00001-of-00004.safetensors` through `model-00004-of-00004.safetensors`, `model.safetensors.index.json`, trainer state, train results
- ZeRO state found: `checkpoint-1/global_step1` and `checkpoint-2/global_step2`, each with two optimizer shards and two model-state files

## Inference
- Checkpoint reload: YES
- Tokenizer reload: YES
- Simple generation: YES
- Generated output: non-empty JSON-like text

## Evaluation
- Evaluation performed: NO
- Reason: user requested no BLEU comparison; success criterion only required checkpoint reload and simple inference.

## Feasibility Conclusion
Tiny full-parameter MirrorAPI SFT with DeepSpeed ZeRO-3 is feasible on two RTX PRO 6000 Blackwell GPUs for this debug workload. The first optimizer step, second optimizer step, checkpoint save, root checkpoint reload, and simple inference all completed without CUDA OOM.

For full training, two GPUs appear technically feasible from a VRAM perspective with the current validated settings, but checkpoint I/O is very heavy and the safety margin is smaller than the 3-GPU setup. Recommended production configuration remains 3 GPUs when available; use 2 GPUs only if GPU availability requires it and accept slower checkpointing plus higher per-GPU memory pressure.
