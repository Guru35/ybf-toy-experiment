"""
Modal wrapper for YBF Phase 2A PPO pure-reward learning.

Mirrors ybf_persistent_train.py structure but:
- Pinned to TRL 0.11.4 (legacy PPOTrainer with manual step API; TRL 1.x
  removed it).
- Mounts anthropic-api-key Secret for Haiku reward calls from container.
- Persistent storage layout: /storage/models/ppo_v{N}/

First-time Modal setup:
    modal volume create ybf-training-storage   # already done for DPO
    modal secret create anthropic-api-key \\
        ANTHROPIC_API_KEY=$(security find-generic-password \\
                                 -s ANTHROPIC_API_KEY -w)

Smoke test (50 scenarios, 1 round):
    modal run ybf_persistent_ppo.py \\
        --version ppo_v1_smoke --axis reality \\
        --rounds 1 --max-scenarios-per-round 50

Full run:
    modal run ybf_persistent_ppo.py \\
        --version ppo_v1 --axis reality --rounds 5
"""

import modal
from pathlib import Path

app = modal.App("ybf-toy-ppo-persistent")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        # Pin TRL to 0.11.4 — last stable version with classical PPOTrainer
        # manual step API. TRL 1.x changed the PPOTrainer significantly.
        "torch==2.4.1",
        "transformers==4.46.3",
        "datasets==3.0.2",
        "peft==0.13.2",
        "trl==0.11.4",
        "accelerate==1.0.1",
        "bitsandbytes==0.44.1",
        "numpy<2",
        "anthropic",
        "rich",          # TRL 0.11.4 transitive — not auto-installed
        "tyro",          # TRL 0.11.4 CLI helper — also transitive
    )
    .run_commands(
        "git clone https://github.com/Guru35/ybf-toy-experiment.git /root/repo",
    )
)

storage = modal.Volume.from_name("ybf-training-storage", create_if_missing=True)


def _load_training_log():
    import json, os
    path = "/storage/training_log_ppo.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _save_training_log(log):
    import json, os
    os.makedirs("/storage", exist_ok=True)
    with open("/storage/training_log_ppo.json", "w") as f:
        json.dump(log, f, indent=2)


@app.function(
    image=image,
    gpu="T4",
    volumes={"/storage": storage},
    timeout=14400,   # 4-hour ceiling for full 5-round run
    secrets=[modal.Secret.from_name("anthropic-api-key")],
)
def train_ppo_persistent(
    version: str = "ppo_v1",
    axis: str = "reality",
    rounds: int = 5,
    batch_size: int = 4,
    lr: float = 1.4e-5,
    lora_r: int = 8,
    max_scenarios_per_round: int = None,
    eval_n: int = 100,
    train_data: str = "data/scenarios.json",
    ood_data: str = "data/ybf_sinir_dpo_ood.jsonl",
):
    """Pure-reward PPO training. The axis definition is loaded inside the
    reward model and never shown to the policy."""
    import json, os, subprocess
    from datetime import datetime

    model_dir = f"/storage/models/{version}"
    os.makedirs(model_dir, exist_ok=True)

    print(f"╔{'═'*60}╗")
    print(f"║ PPO PURE-REWARD TRAINING — {version}")
    print(f"╠{'═'*60}╣")
    print(f"║ Axis:        {axis}")
    print(f"║ Rounds:      {rounds}")
    print(f"║ Batch size:  {batch_size}")
    print(f"║ LR:          {lr}")
    print(f"║ LoRA r:      {lora_r}")
    print(f"║ Train:       {train_data}")
    print(f"║ OOD:         {ood_data}")
    print(f"║ Output:      {model_dir}")
    if max_scenarios_per_round:
        print(f"║ Truncate:    {max_scenarios_per_round} scenarios/round (smoke)")
    print(f"╚{'═'*60}╝\n")

    # ── Pull latest code (Modal caches the initial clone)
    pull = subprocess.run(
        ["git", "-C", "/root/repo", "pull", "--ff-only", "origin", "main"],
        capture_output=True, text=True,
    )
    print(f"[git pull] {pull.stdout.strip()}")

    # Convert scenarios.json (5-axis cache shape) to the flat form the PPO
    # script expects.  We do this on the fly if train_data points to a raw
    # scenarios.json.
    os.chdir("/root/repo/ybf_toy")
    if Path(train_data).name == "scenarios.json":
        raw = json.loads(Path(train_data).read_text())
        flat_path = "/tmp/ppo_scenarios.jsonl"
        with open(flat_path, "w") as f:
            for s in raw:
                f.write(json.dumps({
                    "scenario_id":    s["id"],
                    "situation":      s["situation"],
                    "intention":      s["intention"],
                    "norm":           s.get("norm", ""),
                    "moral_action":   s["options"]["A"],
                    "immoral_action": s["options"]["B"],
                }) + "\n")
        train_data_path = flat_path
    else:
        train_data_path = train_data

    cmd = [
        "python", "ybf_ppo_train.py",
        "--axis", axis,
        "--train_file", train_data_path,
        "--ood_file", ood_data,
        "--output_dir", model_dir,
        "--rounds", str(rounds),
        "--batch_size", str(batch_size),
        "--ppo_lr", str(lr),
        "--lora_r", str(lora_r),
        "--eval_n", str(eval_n),
    ]
    if max_scenarios_per_round:
        cmd += ["--max_scenarios_per_round", str(max_scenarios_per_round)]
    print(f"$ {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=13800)
    print("=== STDOUT (last 6000 chars) ===")
    print(result.stdout[-6000:])
    if result.returncode != 0:
        print("\n=== STDERR (last 4000 chars) ===")
        print(result.stderr[-4000:])
        raise RuntimeError(f"PPO training failed (exit {result.returncode})")

    # Record metadata
    git_commit = subprocess.check_output(
        ["git", "-C", "/root/repo", "rev-parse", "HEAD"]
    ).decode().strip()
    meta = {
        "version":         version,
        "axis":            axis,
        "rounds":          rounds,
        "batch_size":      batch_size,
        "lr":              lr,
        "lora_r":          lora_r,
        "train_data":      train_data,
        "ood_data":        ood_data,
        "max_scenarios":   max_scenarios_per_round,
        "timestamp_utc":   datetime.utcnow().isoformat() + "Z",
        "git_commit":      git_commit,
        "exit_code":       result.returncode,
    }
    with open(f"{model_dir}/run_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    log = _load_training_log()
    eval_path = f"{model_dir}/eval_results.json"
    eval_data = json.loads(Path(eval_path).read_text()) if Path(eval_path).exists() else None
    log[version] = {
        "axis": axis,
        "rounds": rounds,
        "timestamp": meta["timestamp_utc"],
        "eval": eval_data,
    }
    _save_training_log(log)
    storage.commit()
    return {"meta": meta, "eval": eval_data, "log_path": "/storage/training_log_ppo.json"}


@app.local_entrypoint()
def main(
    version: str = "ppo_v1",
    axis: str = "reality",
    rounds: int = 5,
    batch_size: int = 4,
    lr: float = 1.4e-5,
    lora_r: int = 8,
    max_scenarios_per_round: int = 0,
    eval_n: int = 100,
    train_data: str = "data/scenarios.json",
    ood_data: str = "data/ybf_sinir_dpo_ood.jsonl",
):
    import json
    max_s = None if max_scenarios_per_round in (0, None) else max_scenarios_per_round

    print(f"Starting PPO pure-reward training {version} on Modal T4...")
    print(f"  axis={axis} rounds={rounds} batch={batch_size}\n")
    result = train_ppo_persistent.remote(
        version=version, axis=axis, rounds=rounds, batch_size=batch_size,
        lr=lr, lora_r=lora_r, max_scenarios_per_round=max_s,
        eval_n=eval_n, train_data=train_data, ood_data=ood_data,
    )

    print("\n=== Run complete ===")
    print("\nMeta:")
    print(json.dumps(result["meta"], indent=2))
    if result.get("eval"):
        print("\nEval summary (per round):")
        for k in sorted(result["eval"]["rounds_data"].keys()):
            r = result["eval"]["rounds_data"][k]
            id_acc = r["id"]["accuracy_pct"] if r.get("id") else None
            ood_acc = r["ood"]["accuracy_pct"] if r.get("ood") else None
            print(f"  {k}:  ID={id_acc:.1f}%  OOD={ood_acc:.1f}%" if id_acc is not None and ood_acc is not None
                  else f"  {k}:  ID={id_acc}  OOD={ood_acc}")

    print(f"\nPersistent at: /storage/models/{version}/")
    print(f"Useful commands:")
    print(f"  modal volume ls ybf-training-storage models/{version}")
    print(f"  modal volume get ybf-training-storage models/{version}/eval_results.json -")
