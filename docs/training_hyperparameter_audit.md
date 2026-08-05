# MirrorAPI Training Hyperparameter Audit

## Verified Facts

- Base model: `Qwen/Qwen2.5-7B-Instruct`.
- Base revision checked on 2026-08-05: `a09a35458c702b33eeacc393d103063234e8bc28`.
- Official checkpoint revision: `f181ec673e2346898a0d6453164604bb8372c4fd`.
- Official training dataset revision: `94d2a05cbd7f52621c358e0e843bdfa1fd22f945`.
- Official benchmark revision: `adceeb3a567d1f1714fa65c0772ca95a2b0f7cf7`.
- Paper method: supervised fine-tuning on API request-response pairs, with CoT rationales for CoT mode.
- Model card evaluation command uses LLaMA-Factory `stage: sft`, `finetuning_type: full`, `template: qwen`, `bf16`, `cutoff_len: 2560`, `seed: 42`, `max_new_tokens: 2660`.

## Missing Official Training Values

The current public paper, model card, dataset card, and local repo audit did not expose an exact training command with learning rate, epochs, optimizer, scheduler, warmup, batch size, GPU count, or DeepSpeed/FSDP config. Historical model-card revisions may have contained training hyperparameters, but the exact values must remain historical-only unless the revision is cited and captured.

See `configs/official_training_settings.json` for field-level confidence labels.

## Local Adaptations

- `configs/sft_smoke_test.yaml` is a tiny full-parameter training diagnostic with 32 examples and 3 optimizer steps. It is not paper-comparable.
- `configs/sft_full.yaml` preserves a 128 effective batch size when launched on 4 GPUs with per-device batch 2 and gradient accumulation 16. This is a local adaptation, not an official value.
- `configs/joint_sft_cot_full.yaml` is blocked until the public data mixture is verified.
