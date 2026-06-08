import modal
import json
import os

app = modal.App("ybf-dpo-training")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        "transformers>=4.40.0",
        "trl>=0.8.0",
        "peft>=0.10.0",
        "datasets>=2.18.0",
        "torch>=2.2.0",
        "accelerate>=0.28.0",
    )
    .run_commands("git clone https://github.com/Guru35/ybf-toy-experiment /repo")
)


@app.function(image=image, gpu="T4", timeout=3600)
def train(quick: bool = False):
    import json
    import torch
    from datasets import Dataset
    from peft import LoraConfig, get_peft_model, TaskType
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl import DPOTrainer, DPOConfig

    MODEL = "HuggingFaceTB/SmolLM-135M-Instruct"
    DATA = "/repo/ybf_toy/data"

    def load(p):
        with open(p) as f:
            return [json.loads(l) for l in f if l.strip()]

    train_r = load(f"{DATA}/ybf_dpo_train.jsonl")
    test_r = load(f"{DATA}/ybf_dpo_test.jsonl")
    ood_r = load(f"{DATA}/ybf_dpo_ood.jsonl")
    print(f"Train:{len(train_r)} Test:{len(test_r)} OOD:{len(ood_r)}")

    def fmt(r):
        return (
            f"Situation: {r.get('situation', '')}\n"
            f"Intention: {r.get('intention', '')}\n"
            f"Action?"
        )

    def make_ds(records):
        return Dataset.from_list([
            {"prompt": fmt(r), "chosen": r["chosen"], "rejected": r["rejected"]}
            for r in records
        ])

    tok = AutoTokenizer.from_pretrained(MODEL)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    base = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16)
    model = get_peft_model(base, LoraConfig(
        task_type=TaskType.CAUSAL_LM, r=16, lora_alpha=32,
        lora_dropout=0.05, target_modules=["q_proj", "v_proj"], bias="none"
    ))
    ref = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16)

    def evaluate(m, records, label):
        m.eval()
        dev = next(m.parameters()).device
        ok = 0
        with torch.no_grad():
            for r in records:
                p = fmt(r)
                def lp(text):
                    enc = tok(text, return_tensors="pt", truncation=True, max_length=512).to(dev)
                    return -m(**enc, labels=enc["input_ids"]).loss.item()
                if lp(p + " " + r["chosen"]) > lp(p + " " + r["rejected"]):
                    ok += 1
        acc = ok / len(records)
        print(f"  [{label}] {acc:.3f} ({ok}/{len(records)})")
        return acc

    pre_t = evaluate(model, test_r, "TEST pre")
    pre_o = evaluate(model, ood_r, "OOD  pre")

    DPOTrainer(
        model=model,
        ref_model=ref,
        args=DPOConfig(
            output_dir="/tmp/out",
            num_train_epochs=1 if quick else 3,
            max_steps=50 if quick else -1,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=2,
            learning_rate=5e-5,
            beta=0.1,
            max_length=512,
            remove_unused_columns=False,
            logging_steps=10,
            seed=42,
            report_to="none",
        ),
        train_dataset=make_ds(train_r),
        eval_dataset=make_ds(test_r),
        processing_class=tok,
    ).train()

    post_t = evaluate(model, test_r, "TEST post")
    post_o = evaluate(model, ood_r, "OOD  post")

    return {
        "pre_test": round(pre_t, 3),
        "post_test": round(post_t, 3),
        "pre_ood": round(pre_o, 3),
        "post_ood": round(post_o, 3),
        "delta_test": round(post_t - pre_t, 3),
        "delta_ood": round(post_o - pre_o, 3),
    }


@app.local_entrypoint()
def main(quick: bool = False):
    r = train.remote(quick=quick)
    print("\n=== RESULTS ===")
    print(json.dumps(r, indent=2))
    os.makedirs("modal_outputs", exist_ok=True)
    with open("modal_outputs/ybf_dpo_results.json", "w") as f:
        json.dump(r, f, indent=2)
    print("Saved -> modal_outputs/ybf_dpo_results.json")
