# MirrorAPI SFT ID High Result

This is the first complete paper-comparable split run for the MirrorAPI SFT benchmark.

## Scope

- Split: `test_sft/id_high.json`
- Official reference: `reference/id_high.jsonl`
- Samples: 100
- Inference only: YES
- Training/fine-tuning: NO
- Manual output repair: NO

## Official Comparison

| Metric | Official | Mine | Difference | Relative Difference |
| ------ | -------: | ---: | ---------: | ------------------: |
| BLEU-4 | 74.2 | 75.81 | 1.61 | 2.17% |

ROUGE is reported below only as a local diagnostic metric because the MirrorAPI paper table used here reports BLEU-4 for this split.

## Official Metric Script Output

```text
0it [00:00, ?it/s]Building prefix dict from the default dictionary ...
Loading model from cache /tmp/jieba.cache
Loading model cost 0.515 seconds.
Prefix dict has been built successfully.

1it [00:00,  1.30it/s]
4it [00:01,  4.68it/s]
5it [00:01,  4.63it/s]
11it [00:01, 11.70it/s]
14it [00:03,  3.40it/s]
18it [00:03,  4.69it/s]
20it [00:04,  3.52it/s]
24it [00:05,  5.33it/s]
28it [00:05,  7.02it/s]
33it [00:05,  9.97it/s]
39it [00:05, 14.76it/s]
44it [00:05, 14.45it/s]
47it [00:07,  5.67it/s]
52it [00:08,  6.98it/s]
55it [00:08,  8.17it/s]
60it [00:08, 10.95it/s]
63it [00:08,  8.85it/s]
67it [00:09,  8.03it/s]
69it [00:09,  7.50it/s]
77it [00:10, 12.13it/s]
79it [00:10, 11.84it/s]
87it [00:10, 18.53it/s]
93it [00:10, 23.02it/s]
97it [00:11, 11.16it/s]
100it [00:11, 12.27it/s]
100it [00:11,  8.52it/s]
{'rouge-1': 76.84, 'rouge-2': 73.84, 'rouge-l': 79.22, 'bleu-4': 75.81}
```

## Validation

- Inputs: 100
- Predictions: 100
- Converted outputs: 100
- References: 100
- Duplicate prompts: 0
- Missing outputs: 0
- Empty outputs: 0
- Traceback outputs: 0
- Strict valid outer JSON predictions: 56
- JSON-like but invalid outer predictions: 42
- Prediction failures: 0

The official conversion script accepted the complete prediction file and produced 100 converted outputs. The invalid outer JSON count refers to strict parsing of the raw generated text before official conversion; these outputs were not manually repaired.

## Runtime

- Wall runtime: 841 seconds
- LLaMA-Factory predict runtime: 822.9382 seconds
- Average latency from wall runtime: 8.4100 seconds/sample
- Average latency from predict runtime: 8.2294 seconds/sample
- Median latency: unavailable because the official LLaMA-Factory prediction log does not emit per-sample timestamps

## Generation

- Template: `qwen`
- Max new tokens: 2660
- Cutoff length: 2560
- do_sample: False
- Temperature: 0.0
- top_p: 1.0
- top_k: 0
- Seed: 42
- Precision: `bf16`

## Revisions

- Model revision: `f181ec673e2346898a0d6453164604bb8372c4fd`
- Dataset revision: `adceeb3a567d1f1714fa65c0772ca95a2b0f7cf7`
- LLaMA-Factory revision: `ca75f1edf3cb50343ed1c98605141c3e22075b5f`
