# JSON Output Analysis

This file summarizes raw-output JSON validity for the completed paper-comparable MirrorAPI SFT splits. The official prediction conversion accepted every generated prediction and no outputs were manually repaired.

| Split | Predictions | Strict Valid Outer JSON | JSON-Like Invalid Outer | Empty Outputs | Tracebacks | Conversion |
| ----- | ----------: | ----------------------: | ----------------------: | ------------: | ---------: | ---------- |
| ID High | 100 | 56 | 42 | 0 | 0 | PASS |
| ID Medium | 100 | 50 | 50 | 0 | 0 | PASS |
| ID Low | 100 | 39 | 61 | 0 | 0 | PASS |
| OOD Failed | 100 | 8 | 92 | 0 | 0 | PASS |
| OOD Successful | 200 | 165 | 35 | 0 | 0 | PASS |

Notes:

- `Strict Valid Outer JSON` counts predictions where the raw generated text parses directly as JSON.
- `JSON-Like Invalid Outer` counts non-empty generations that do not parse as strict JSON but were still accepted by the official conversion path for BLEU/ROUGE scoring.
- The benchmark comparison uses the official converted prediction files and official metric scripts; malformed raw JSON was not manually repaired.
