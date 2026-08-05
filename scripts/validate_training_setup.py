#!/usr/bin/env python3
"""Validate MirrorAPI training setup without starting training."""
import argparse, json, os, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def status(name, ok, detail=""):
    suffix = f" - {detail}" if detail else ""
    print(f"{name}: {'PASS' if ok else 'FAIL'}{suffix}")
    return ok

def warn(name, detail):
    print(f"{name}: WARNING - {detail}")
    return True

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--base-model', default=os.environ.get('MIRRORAPI_BASE_MODEL','/home/khabibillo/models/Qwen2.5-7B-Instruct'))
    p.add_argument('--training-data-dir', default=str(REPO_ROOT/'data/raw/MirrorAPI-Training'))
    p.add_argument('--llamafactory-dir', default=str(REPO_ROOT/'LLaMA-Factory'))
    p.add_argument('--output-dir', default=os.environ.get('MIRRORAPI_OUTPUT_DIR','/home/khabibillo/checkpoints/mirrorapi-sft-smoke'))
    args=p.parse_args()
    checks=[]
    base=Path(args.base_model)
    checks.append(status('Base model', base.exists(), str(base)))
    tok_files=['tokenizer.json','tokenizer_config.json','vocab.json','merges.txt']
    checks.append(status('Tokenizer', all((base/f).exists() for f in tok_files), ', '.join(tok_files)))
    data_dir=Path(args.training_data_dir)
    needed=['train_sft.json','train_cot.json','train_augment.json']
    checks.append(status('Training data', all((data_dir/f).exists() for f in needed), str(data_dir)))
    try:
        rec=json.loads((data_dir/'train_sft.json').read_text(encoding='utf-8'))[0]
        checks.append(status('Dataset fields', all(k in rec for k in ['system','instruction','output']), sorted(rec.keys())))
        prompt=f"SYSTEM:\n{rec.get('system','')[:120]}\nUSER:\n{rec.get('instruction','')[:120]}\nASSISTANT TARGET:\n{rec.get('output','')[:120]}"
        checks.append(status('Prompt rendering', bool(prompt.strip()), 'qwen template expected in LLaMA-Factory'))
    except Exception as e:
        checks.append(status('Dataset fields', False, str(e)))
        checks.append(status('Prompt rendering', False, str(e)))
    ds_info=Path(args.llamafactory_dir)/'data/dataset_info.json'
    try:
        info=json.loads(ds_info.read_text(encoding='utf-8'))
        names=['mirrorapi_sft_train','mirrorapi_cot_train','mirrorapi_sft_debug','mirrorapi_cot_debug']
        checks.append(status('Dataset registration', all(n in info for n in names), ', '.join(names)))
    except Exception as e:
        checks.append(status('Dataset registration', False, str(e)))
    try:
        out=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,memory.total,utilization.gpu','--format=csv,noheader'], text=True)
        freeish=[line for line in out.splitlines() if int(line.split(',')[1].strip().split()[0]) < 1024]
        checks.append(status('GPU readiness', bool(freeish), freeish[0] if freeish else 'no GPU under 1 GiB used'))
    except Exception as e:
        checks.append(status('GPU readiness', False, str(e)))
    checks.append(warn('Trainable parameters', 'UNVERIFIED until LLaMA-Factory loads model; expected full finetuning for paper-oriented configs'))
    checks.append(warn('Training/test overlap check', 'UNVERIFIED unless raw training and benchmark records are both present with comparable IDs'))
    checks.append(status('Output directory', not Path(args.output_dir).exists(), args.output_dir))
    print(f"Overall setup: {'PASS' if all(checks) else 'FAIL'}")
    return 0 if all(checks) else 1
if __name__=='__main__': sys.exit(main())
