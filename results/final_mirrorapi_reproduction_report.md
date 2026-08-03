# MirrorAPI SFT Benchmark Reproduction Report

This report summarizes the inference-only reproduction of the official MirrorAPI SFT benchmark rows from the paper table. The one-request smoke test, 5-sample validation, 20-sample validation, and ID High run were already completed before the remaining four splits were run.

## Environment

- GPU server: `gpusystem`
- GPU: NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition
- Driver/CUDA: NVIDIA driver `580.95.05`, CUDA `13.0`
- Python: `3.10.12`
- PyTorch: `2.11.0+cu130`
- Transformers: `4.52.4`
- LLaMA-Factory: `0.9.3`, commit `ca75f1edf3cb50343ed1c98605141c3e22075b5f`
- Checkpoint: `/home/khabibillo/models/stabletoolbench-MirrorAPI`
- Checkpoint revision: `f181ec673e2346898a0d6453164604bb8372c4fd`
- Dataset: `stabletoolbench/MirrorAPI-Bench`
- Dataset revision: `adceeb3a567d1f1714fa65c0772ca95a2b0f7cf7`
- Mode: SFT inference only
- Template: `qwen`
- Generation: `do_sample=false`, `temperature=0.0`, `top_p=1.0`, `top_k=0`, `max_new_tokens=2660`, `cutoff_len=2560`, `bf16`, batch size `1`, seed `42`

## Results

| Split | Official BLEU-4 | Mine | Difference | Relative Difference |
| ----- | --------------: | ---: | ---------: | ------------------: |
| ID High | 74.2 | 75.81 | +1.61 | +2.17% |
| ID Medium | 80.0 | 82.27 | +2.27 | +2.84% |
| ID Low | 86.3 | 87.12 | +0.82 | +0.95% |
| OOD Failed | 89.9 | 88.51 | -1.39 | -1.55% |
| OOD Successful | 35.6 | 32.57 | -3.03 | -8.51% |

BLEU-4 is the paper-comparable metric. ROUGE was computed by the released script and retained as a local diagnostic only.

## Runtime Summary

| Split | Samples | Runtime Seconds | Average Latency Seconds |
| ----- | ------: | --------------: | ----------------------: |
| ID High | 100 | 841.000 | 8.410 |
| ID Medium | 100 | 484.300 | 4.843 |
| ID Low | 100 | 316.751 | 3.168 |
| OOD Failed | 100 | 75.277 | 0.753 |
| OOD Successful | 200 | 1743.669 | 8.718 |

Total benchmark runtime for the five complete splits: `3460.997` seconds.

Median per-sample latency is not available because the official LLaMA-Factory prediction output does not emit per-sample timestamps. The averages above are computed from recorded wall-clock split runtimes.

## Output Quality

| Split | Predictions | Converted | References | Missing | Duplicates | Strict JSON | JSON-like Invalid | Tracebacks |
| ----- | ----------: | --------: | ---------: | ------: | ---------: | ----------: | ----------------: | ---------: |
| ID High | 100 | 100 | 100 | 0 | 0 | 56 | 42 | 0 |
| ID Medium | 100 | 100 | 100 | 0 | 0 | 50 | 50 | 0 |
| ID Low | 100 | 100 | 100 | 0 | 0 | 39 | 61 | 0 |
| OOD Failed | 100 | 100 | 100 | 0 | 0 | 8 | 92 | 0 |
| OOD Successful | 200 | 200 | 200 | 0 | 0 | 165 | 35 | 0 |

Every split produced the expected number of predictions, converted outputs, and references. The official conversion script accepted every complete split. The strict JSON counts refer to raw generated model text before official conversion; malformed raw outputs were not manually repaired.

## Difference Analysis

Verified facts:

- The same checkpoint path and recorded Hugging Face checkpoint revision were used for all five splits.
- The same MirrorAPI-Bench dataset revision was used for all five splits.
- The same LLaMA-Factory version, Qwen template, tokenizer path, and generation settings were used for every split.
- All runs were inference-only: `--do_predict` was enabled and no training command, optimizer step, fine-tuning, or checkpoint save was performed.
- The released conversion and metric scripts accepted all prediction files.

Documented environment differences and caveats:

- The exact LLaMA-Factory revision used for the paper was not documented in the official sources available during setup; this run used the pinned compatible `v0.9.3` revision.
- The installed runtime uses PyTorch `2.11.0+cu130` and Transformers `4.52.4`; paper-time dependency versions may differ.
- Greedy decoding was enforced with `do_sample=false` and `temperature=0.0`. Transformers repeatedly warns that `temperature` and `top_k` are ignored when sampling is disabled; this is expected behavior for greedy decoding.
- Raw model outputs are often JSON-like but not strict JSON. The official conversion script handles this with its own extraction path, which is why conversion succeeds despite malformed raw JSON.

Hypotheses for BLEU differences:

- Small positive differences on ID High, ID Medium, and ID Low are consistent with dependency/runtime differences around deterministic generation and official conversion behavior.
- OOD Failed is close to the paper value; this split mostly contains error-like responses, so shorter outputs and extraction details can move BLEU by a small amount.
- OOD Successful has the largest gap. This split contains longer generated successful responses, so BLEU is more sensitive to generation length, truncation, exact wording, tokenizer/runtime differences, and raw-output extraction.

## Final Conclusion

The official MirrorAPI SFT checkpoint was evaluated in inference-only mode on all five official MirrorAPI-Bench SFT test groups using the pinned checkpoint, pinned dataset, Qwen prompt template, deterministic generation settings, official conversion script, and official BLEU evaluator.

The reproduced BLEU-4 scores are close to the paper on ID High, ID Medium, ID Low, and OOD Failed. OOD Successful is lower by `3.03` BLEU-4 points (`-8.51%` relative), which is meaningful and should be investigated before claiming exact paper parity. The benchmark is sufficiently reproduced to proceed with deeper discrepancy analysis or repeated controlled runs, but exact result parity is not claimed.
