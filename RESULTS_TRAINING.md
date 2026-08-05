# MirrorAPI Training Results Template

No local training checkpoint has been produced yet.

| Split | Base Qwen BLEU-4 | My Checkpoint BLEU-4 | Official Checkpoint BLEU-4 | Paper BLEU-4 |
|---|---:|---:|---:|---:|
| ID High | | | 75.81 | 74.2 |
| ID Medium | | | | 80.0 |
| ID Low | | | | 86.3 |
| OOD Failed | | | | 89.9 |
| OOD Successful | | | | 35.6 |

| Model | Training data | Training method | Trainable parameters | Checkpoint size |
|---|---|---|---:|---:|
| Qwen/Qwen2.5-7B-Instruct | Qwen upstream instruction data | upstream instruct tuning | | |
| My SFT-only checkpoint | train_sft.json | full_sft, local SFT-only baseline | | |
| My closest-paper checkpoint | UNVERIFIED joint mixture | full_sft, closest public reproduction | | |
| stabletoolbench/MirrorAPI | train_sft.json, train_cot.json, train_augment.json per model card | supervised fine-tuning with SFT and CoT modes | 7,615,616,512 | ~15.2 GB safetensors |
