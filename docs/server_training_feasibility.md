# Server Training Feasibility

## Hardware Snapshot

- GPUs: 4x NVIDIA RTX PRO 6000 Blackwell, 97,887 MiB VRAM each.
- Driver/CUDA from `nvidia-smi`: driver `580.95.05`, CUDA `13.0`.
- GPU 2 had a VLLM process using about 88 GiB at audit time. Do not use or kill it.
- GPUs 0, 1, and 3 were otherwise idle except for Xorg.
- System RAM: 503 GiB total, 393 GiB available at audit time.
- Disk under `/home/khabibillo`: 19 TB total, 14 TB available.
- `nvcc` reports CUDA 11.5, so runtime CUDA and toolkit CUDA differ. Use PyTorch wheels compatible with the installed driver rather than compiling CUDA extensions blindly.

## Memory Estimate for Full Fine-Tuning Qwen2.5-7B

Approximate parameter count: 7,615,616,512.

- bf16 model weights: ~15.2 GB.
- bf16 gradients: ~15.2 GB.
- Adam optimizer states in fp32: ~60.9 GB.
- Master params or framework overhead may add ~15-30 GB depending on implementation.
- Activations depend on cutoff length, batch size, gradient checkpointing, and attention backend. With cutoff 2560 and per-device batch 2, expect tens of GB.
- Full checkpoint size: ~15-16 GB for safetensors, plus tokenizer/config/trainer metadata. Multiple checkpoints can consume 50+ GB.

## Proposed Setup

- Tiny debug training: 1 idle GPU, per-device batch 1, 3 steps, no paper claim.
- SFT-only full training: prefer 4 GPUs if all are free, with DeepSpeed ZeRO-2 or ZeRO-3 after compatibility validation.
- If only 3 GPUs are free, either wait or use a local adaptation with changed gradient accumulation. Do not use GPU 2 while the VLLM process is present.
- Effective global batch-size calculation: `num_gpus * per_device_train_batch_size * gradient_accumulation_steps`.
- Local 4-GPU adaptation in config: `4 * 2 * 16 = 128`.

## Risks

- Exact official training hyperparameters are not public in the current audited materials.
- LLaMA-Factory config compatibility must be validated before tiny training.
- Full fine-tuning may need DeepSpeed/FSDP; the global `python3` environment currently lacks training packages, and the existing `.venv` import path needs repair or reactivation verification.
- Blackwell/CUDA 13 support requires modern PyTorch; historical package versions may be incompatible.

## Duration

- Tiny debug: expected 5-20 minutes including model load, assuming base model is already local.
- Full SFT: likely several hours on 4 GPUs, depending on dataset rows, DeepSpeed/FSDP, FlashAttention, and IO.
