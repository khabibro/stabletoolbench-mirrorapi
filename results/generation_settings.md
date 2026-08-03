# Generation Verification

| Parameter | Official value/source | Current value | Match |
|---|---|---:|---|
| temperature | Paper reports temperature 0 for all models; model card omits explicit value | `0.0` | Match via explicit override |
| do_sample | Greedy decoding implied by temperature 0; not explicitly in model card | `False` | Match/inference correction |
| top_p | Not used under greedy decoding; checkpoint default is 0.8 | `1.0` | Safe, ignored because do_sample=false |
| top_k | Not used under greedy decoding; checkpoint default is 20 | `0` | Safe, ignored because do_sample=false |
| max_new_tokens | Model card command uses 2660 | `2660` | Match |
| cutoff_len | Model card command uses 2560 | `2560` | Match |
| template | Model card command uses qwen | `qwen` | Match |
| seed | Not clearly specified in paper/model card for inference | `42` | Local reproducibility setting |
| precision | Model card command uses bf16 | `bf16` | Match |

Note: Transformers warns that `temperature` and `top_k` are ignored when `do_sample=false`; this is expected for greedy decoding and preserves temperature-0 behavior.
