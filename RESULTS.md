# MirrorAPI SFT BLEU Reproduction Results

## Reproduction Scope

This is the SFT BLEU reproduction from MirrorAPI Table 3. It evaluates the official MirrorAPI SFT checkpoint on the official MirrorAPI-Bench SFT splits using LLaMA-Factory inference only and the official released conversion and metric scripts.

## Official Paper Results

| Split | Official BLEU-4 |
| ----- | --------------: |
| OOD Successful | 35.6 |
| OOD Failed | 89.9 |
| ID High | 74.2 |
| ID Medium | 80.0 |
| ID Low | 86.3 |

## Reproduced Results

| Split | Official BLEU-4 | Reproduced BLEU-4 | Absolute Difference | Relative Difference | Status |
| ----- | --------------: | ----------------: | ------------------: | ------------------: | ------ |
| OOD Successful | 35.6 | 32.57 | -3.03 | -8.51% | Complete |
| OOD Failed | 89.9 | 88.51 | -1.39 | -1.55% | Complete |
| ID High | 74.2 | 75.81 | +1.61 | +2.17% | Complete |
| ID Medium | 80.0 | 82.27 | +2.27 | +2.84% | Complete |
| ID Low | 86.3 | 87.12 | +0.82 | +0.95% | Complete |

## ID High Details

Samples: 100
BLEU-4: 75.81
ROUGE-1: 76.84
ROUGE-2: 73.84
ROUGE-L: 79.22
Runtime: 841 seconds
Paper difference: +1.61
Relative difference: +2.17%

## Output Quality

| Split | Expected | Predictions | Converted | Missing | Empty | Malformed Raw JSON | Conversion |
| ----- | -------: | ----------: | --------: | ------: | ----: | -----------------: | ---------- |
| OOD Successful | 200 | 200 | 200 | 0 | 0 | 35 | Passed |
| OOD Failed | 100 | 100 | 100 | 0 | 0 | 92 | Passed |
| ID High | 100 | 100 | 100 | 0 | 0 | 42 | Passed |
| ID Medium | 100 | 100 | 100 | 0 | 0 | 50 | Passed |
| ID Low | 100 | 100 | 100 | 0 | 0 | 61 | Passed |

## Environment

- Python: `3.10.12`
- PyTorch: `2.11.0+cu130`
- Transformers: `4.52.4`
- LLaMA-Factory: `v0.9.3`, commit `ca75f1edf3cb50343ed1c98605141c3e22075b5f`
- Model revision: `f181ec673e2346898a0d6453164604bb8372c4fd`
- Dataset revision: `adceeb3a567d1f1714fa65c0772ca95a2b0f7cf7`
- GPU: NVIDIA RTX PRO 6000 Blackwell Max-Q Workstation Edition

## Differences from the Paper

- The exact original LLaMA-Factory revision is not documented in the official sources available during setup.
- The runtime uses newer PyTorch/Transformers and a Blackwell GPU, so byte-for-byte generated text parity is not claimed.
- Greedy decoding was used with `do_sample=false`; Transformers warns that sampling-only fields such as `temperature` and `top_k` are ignored in this mode.
- Raw model outputs are sometimes JSON-like but not strict JSON. The official conversion script accepted every completed split.

## Final Conclusion

All five MirrorAPI SFT Table 3 splits have been reproduced with the official checkpoint, official SFT data, official conversion script, and official BLEU evaluator. The ID and OOD Failed scores are close to the paper values. OOD Successful is lower by 3.03 BLEU-4 points and should be the first target for deeper discrepancy analysis before claiming exact paper parity.
