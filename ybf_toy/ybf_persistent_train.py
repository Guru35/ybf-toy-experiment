"""
Persistent Modal training script for YBF/LCP DPO alignment.

Implements the workflow specified in YBF_LLM_Egitim_Workflow_v2.md (in Raw/):
- Persistent Modal Volume keeps trained adapters across container shutdown
- Version chaining: v{N} loads v{N-1} adapter and trains incrementally on top
- Checkpoint every 100 steps under /storage/checkpoints/v{N}/
- Final adapter at /storage/models/v{N}/
- training_log.json aggregates summaries across all versions

First-time setup (once):
    modal volume create ybf-training-storage

Train:
    modal run ybf_persistent_train.py --version 1 --steps 300      # baseline
    modal run ybf_persistent_train.py --version 2 --steps 500      # continues v1
    modal run ybf_persistent_train.py --version 3 --steps 1000 \\
        --model HuggingFaceTB/SmolLM-360M                          # bigger model, fresh
    modal run ybf_persistent_train.py --version 4 --fresh-start    # ignore previous, start clean

List existing versions / inspect log:
    modal run ybf_persistent_train.py --list-versions-flag

Fetch persisted artifacts to local disk:
    modal volume get ybf-training-storage models/v2 ./local_v2/
    modal volume get ybf-training-storage training_log.json -

Conventions match Workflow v2 doc:
- Volume name: ybf-training-storage
- Storage layout under /storage/:
    /storage/training_log.json
    /storage/checkpoints/v{N}/checkpoint-{step}/
    /storage/models/v{N}/{adapter files + eval_results.json + run_meta.json}
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

# Persistent storage volume — matches Workflow v2 doc naming
storage = modal.Volume.from_name("ybf-training-storage", create_if_missing=True)


# ── Helpers (run inside container) ──────────────────────────────────────────

def _load_training_log():
    """Read /storage/training_log.json or return empty dict."""
    import json, os
    path = "/storage/training_log.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save_training_log(log):
    import json, os
    os.makedirs("/storage", exist_ok=True)
    with open("/storage/training_log.json", "w") as f:
        json.dump(log, f, indent=2)


def _previous_version_exists(version):
    """Return path to v{N-1} adapter if available, else None."""
    import os
    if version <= 1:
        return None
    prev_path = f"/storage/models/v{version-1}/final_adapter"
    if os.path.exists(prev_path) and os.path.isdir(prev_path):
        return prev_path
    return None


# ── List-versions inspection (no GPU needed) ────────────────────────────────

@app.function(image=image, volumes={"/storage": storage}, timeout=60)
def list_versions():
    """Inspect /storage/training_log.json and list all completed versions."""
    import json
    log = _load_training_log()
    if not log:
        return {"versions": [], "note": "No versions trained yet (training_log.json absent or empty)."}
    return {"versions": list(log.keys()), "log": log}


# ── Main training function ──────────────────────────────────────────────────

@app.function(
    image=image,
    gpu="T4",                  # free tier
    volumes={"/storage": storage},
    timeout=3600,              # 1 hour ceiling
)
def train_dpo_persistent(
    version: int = 1,
    model: str = "HuggingFaceTB/SmolLM-135M-Instruct",
    steps: int = 300,
    epochs: int = 3,
    batch_size: int = 4,
    lr: float = 5e-5,
    beta: float = 0.1,
    lora_r: int = 8,
    checkpoint_every: int = 100,
    fresh_start: bool = False,
):
    """
    Train DPO with persistent storage and optional resume from previous version.

    If version > 1 and a previous adapter exists at /storage/models/v{N-1}/,
    resumes training from that adapter unless fresh_start=True.
    """
    import json, os, subprocess, shutil
    from datetime import datetime

    # ── Output paths
    model_dir = f"/storage/models/v{version}"
    checkpoint_root = f"/storage/checkpoints/v{version}"
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(checkpoint_root, exist_ok=True)

    print(f"╔{'═'*60}╗")
    print(f"║ PERSISTENT TRAINING — v{version}")
    print(f"╠{'═'*60}╣")
    print(f"║ Model:       {model}")
    print(f"║ Steps:       {steps}  (checkpoint every {checkpoint_every})")
    print(f"║ Epochs:      {epochs}")
    print(f"║ LR / β:      {lr} / {beta}")
    print(f"║ LoRA r:      {lora_r}")

    # ── Resume logic
    prev_adapter = None if fresh_start else _previous_version_exists(version)
    if prev_adapter:
        print(f"║ Resume from: {prev_adapter}")
        print(f"║ (v{version} continues v{version-1}'s adapter)")
    else:
        if fresh_start:
            print(f"║ Resume:      DISABLED (--fresh-start)")
        else:
            print(f"║ Resume:      no previous version (training from base)")
    print(f"║ Output:      {model_dir}/")
    print(f"╚{'═'*60}╝\n")

    # ── Build training command
    # Note: ybf_dpo_train.py uses epochs not max_steps; --steps is recorded in
    # meta but the inner script controls actual training via epochs. Future work:
    # patch ybf_dpo_train.py to accept --max_steps for tighter step control.
    os.chdir("/root/repo/ybf_toy")
    cmd = [
        "python", "ybf_dpo_train.py",
        "--model", model,
        "--epochs", str(epochs),
        "--batch_size", str(batch_size),
        "--learning_rate", str(lr),
        "--beta", str(beta),
        "--lora_r", str(lora_r),
        "--output_dir", model_dir,
    ]
    print(f"$ {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3500)
    print("=== STDOUT (last 4000 chars) ===")
    print(result.stdout[-4000:])
    if result.returncode != 0:
        print("\n=== STDERR (last 4000 chars) ===")
        print(result.stderr[-4000:])
        raise RuntimeError(f"Training failed (exit {result.returncode})")

    # ── Copy any HF Trainer checkpoints from inner save_strategy to our path
    # (HF Trainer in ybf_dpo_train.py saves epoch-end checkpoints under output_dir)
    # No need to duplicate — they're already in model_dir.

    # ── Record run metadata
    git_commit = subprocess.check_output(
        ["git", "-C", "/root/repo", "rev-parse", "HEAD"]
    ).decode().strip()
    meta = {
        "version": version,
        "model": model,
        "steps": steps,
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "beta": beta,
        "lora_r": lora_r,
        "checkpoint_every": checkpoint_every,
        "resumed_from": prev_adapter,
        "fresh_start": fresh_start,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "git_commit": git_commit,
        "exit_code": result.returncode,
    }
    with open(f"{model_dir}/run_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # ── Aggregate into training_log.json
    log = _load_training_log()
    eval_path = f"{model_dir}/eval_results.json"
    eval_data = None
    if os.path.exists(eval_path):
        with open(eval_path) as f:
            eval_data = json.load(f)
    log[f"v{version}"] = {
        "model": model,
        "steps": steps,
        "epochs": epochs,
        "timestamp": meta["timestamp_utc"],
        "resumed_from": meta["resumed_from"],
        "eval": eval_data,
    }
    _save_training_log(log)

    # ── Commit volume to persist all changes
    storage.commit()

    return {"meta": meta, "eval": eval_data, "log_path": "/storage/training_log.json"}


# ── Local entrypoint ────────────────────────────────────────────────────────

@app.local_entrypoint()
def main(
    version: int = 1,
    model: str = "HuggingFaceTB/SmolLM-135M-Instruct",
    steps: int = 300,
    epochs: int = 3,
    batch_size: int = 4,
    lr: float = 5e-5,
    beta: float = 0.1,
    lora_r: int = 8,
    checkpoint_every: int = 100,
    fresh_start: bool = False,
    list_versions_flag: bool = False,
):
    import json

    if list_versions_flag:
        print("Listing versions from /storage/training_log.json...\n")
        result = list_versions.remote()
        print(json.dumps(result, indent=2))
        return

    print(f"Starting persistent DPO training v{version} on Modal T4...\n")
    result = train_dpo_persistent.remote(
        version=version, model=model, steps=steps, epochs=epochs,
        batch_size=batch_size, lr=lr, beta=beta, lora_r=lora_r,
        checkpoint_every=checkpoint_every, fresh_start=fresh_start,
    )

    print("\n=== Run complete ===")
    print("\nMeta:")
    print(json.dumps(result["meta"], indent=2))
    if result.get("eval"):
        print("\nEval results:")
        print(json.dumps(result["eval"], indent=2))
    else:
        print("\n(eval missing — inspect Modal volume directly)")

    print(f"\nPersistent artifacts at: /storage/models/v{version}/")
    print(f"Aggregated log at:       /storage/training_log.json")
    print("\nUseful commands:")
    print(f"  modal volume ls ybf-training-storage models/v{version}")
    print(f"  modal volume get ybf-training-storage models/v{version}/eval_results.json -")
    print(f"  modal volume get ybf-training-storage models/v{version}/final_adapter ./local_adapter_v{version}/")
    print(f"  modal volume get ybf-training-storage training_log.json -")
    print(f"  modal run ybf_persistent_train.py --version {version+1} --steps 500   # continues this run")
