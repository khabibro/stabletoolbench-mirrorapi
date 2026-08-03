# MirrorAPI SFT Benchmark Checkpoint

This checkpoint covers the required five-sample preflight and first-20 OOD SFT validation only. It is not a full-split paper comparison.

## Status

- Training performed: NO
- Fine-tuning performed: NO
- Model weights changed: NO
- Inference only: YES
- Official conversion script accepted outputs: YES
- Official metric script ran: YES

## Five-Sample Preflight

Official metrics output: `results/preflight_5_metrics.txt`.

## Twenty-Sample Validation

Official metrics output: `results/metrics_20.txt`.

Result from official script:

```text
{'rouge-1': 37.21, 'rouge-2': 29.65, 'rouge-l': 34.6, 'bleu-4': 22.8}
```

This 20-sample BLEU must not be compared to the full-split paper BLEU.

## Known Differences / Notes

- Exact official LLaMA-Factory revision is not specified by the MirrorAPI model card. Used LLaMA-Factory `v0.9.3` (`ca75f1edf3cb50343ed1c98605141c3e22075b5f`) because current `main` requires Python >=3.11 and the server has Python 3.10.12.
- The first invalid 20-sample attempt used checkpoint generation defaults (`temperature=0.7`) and was stopped before completion. Corrected runs use `--do_sample false --temperature 0.0` for paper-compatible greedy generation.
- Official metrics script was run from `/tmp` with absolute paths to avoid Python 3.10/NLTK current-directory import blocking. The official script code was not modified.
