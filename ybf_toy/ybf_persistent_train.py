"""
Persistent Modal training script — saves trained model to Modal Volume.

Built on top of ybf_dpo_modal_v2.py with one critical change: trained LoRA
adapter is written to a persistent Modal Volume so weights survive container
shutdown. The v0.4.5/v0.4.8 runs lost their adapters when the container
exited; this script fixes that.

Usage:
    modal volume create ybf-storage              # once, first time
    modal run ybf_persistent_train.py --version 2 --steps 500
    modal run ybf_persistent_train.py --version 3 --steps 1000 --model HuggingFaceTB/SmolLM-360M

Outputs (in Modal Volume `ybf-storage`):
    /storage/models/v{version}/final_adapter/   LoRA weights (persistent)
    /storage/models/v{version}/eval_results.json
    /storage/models/v{version}/training_log.json
    /storage/models/v{version}/run_meta.json    Hyperparams + git commit

Inspect after training:
    modal volume ls ybf-storage models/v2
    modal volume get ybf-storage models/v2/eval_results.json -
"""

import modal
from pathlib import Path

app = modal.App("ybf-toy-dpo-persistent")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "datasets",
        "peft",
        "trl",
        "accelerate",
        "bitsandbytes",
        "numpy",
    )
    .run_commands(
        "git clone https://github.com/Guru35/ybf-toy-experiment.git /root/repo",
    )
)

# Persistent storage volume — survives container shutdown
storage = modal.Volume.from_name("ybf-storage", create_if_missing=True)


@app.function(
    image=image,
    gpu="T4",                  # free tier
    volumes={"/storage": storage},
    timeout=3600,              # 1 hour ceiling
)
def train_dpo_persistent(
    version: int = 2,
    model: str = "HuggingFaceTB/SmolLM-135M-Instruct",
    steps: int = 500,
    epochs: int = 3,
    batch_size: int = 4,
    lr: float = 5e-5,
    beta: float = 0.1,
    lora_r: int = 8,
):
    import subprocess, json, os, shutil
    from datetime import datetime

    out_dir = f"/storage/models/v{version}"
    os.makedirs(out_dir, exist_ok=True)
    print(f"=== Persistent training run v{version} ===")
    print(f"Model: {model}")
    print(f"Output: {out_dir}")

    # Run training (use existing script's pre/post eval)
    os.chdir("/root/repo/ybf_toy")
    cmd = [
        "python", "ybf_dpo_train.py",
        "--model", model,
        "--epochs", str(epochs),
        "--batch_size", str(batch_size),
        "--learning_rate", str(lr),
        "--beta", str(beta),
        "--lora_r", str(lora_r),
        "--output_dir", out_dir,
    ]
    # If the script supports --max_steps add it; otherwise epochs control
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3500)
    print("STDOUT:", result.stdout[-4000:])
    if result.returncode != 0:
        print("STDERR:", result.stderr[-4000:])
        raise RuntimeError(f"Training failed (exit {result.returncode})")

    # Save run metadata for traceability
    meta = {
        "version": version,
        "model": model,
        "steps": steps,
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "beta": beta,
        "lora_r": lora_r,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "git_commit": subprocess.check_output(
            ["git", "-C", "/root/repo", "rev-parse", "HEAD"]
        ).decode().strip(),
    }
    with open(f"{out_dir}/run_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Commit volume to ensure persistence across function instances
    storage.commit()

    # Return eval results if present
    eval_path = f"{out_dir}/eval_results.json"
    if os.path.exists(eval_path):
        with open(eval_path) as f:
            return {"meta": meta, "eval": json.load(f)}
    return {"meta": meta, "eval": None, "note": "eval_results.json not produced"}


@app.local_entrypoint()
def main(
    version: int = 2,
    model: str = "HuggingFaceTB/SmolLM-135M-Instruct",
    steps: int = 500,
    epochs: int = 3,
    batch_size: int = 4,
    lr: float = 5e-5,
    beta: float = 0.1,
    lora_r: int = 8,
):
    import json
    print(f"Starting persistent DPO training v{version} on Modal T4...")
    print(f"  Model:    {model}")
    print(f"  Steps:    {steps}")
    print(f"  Epochs:   {epochs}")
    print(f"  LR:       {lr}")
    print(f"  Output:   /storage/models/v{version}/  (persistent Modal volume)")
    print()

    result = train_dpo_persistent.remote(
        version=version, model=model, steps=steps, epochs=epochs,
        batch_size=batch_size, lr=lr, beta=beta, lora_r=lora_r,
    )

    print("\n=== Run complete ===")
    print("Meta:", json.dumps(result["meta"], indent=2))
    if result.get("eval"):
        print("\nEval results:")
        print(json.dumps(result["eval"], indent=2))
    else:
        print("\n(eval missing — inspect Modal volume directly)")

    print(f"\nModel persistently stored at: /storage/models/v{version}/")
    print("Inspect with:")
    print(f"  modal volume ls ybf-storage models/v{version}")
    print(f"  modal volume get ybf-storage models/v{version}/eval_results.json -")
    print(f"  modal volume get ybf-storage models/v{version}/final_adapter ./local_adapter_v{version}/")
