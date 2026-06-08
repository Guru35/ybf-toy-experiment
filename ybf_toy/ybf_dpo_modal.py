"""
Modal alternative for DPO training — used if Colab MCP setup fails.

Modal lets us run the existing ybf_dpo_train.py on a remote GPU without
browser interaction. Pay-per-second, ~$0.50 for the full SmolLM-135M run.

Prerequisites:
    pip install modal
    modal token new                              # first-time auth
    modal volume create ybf-toy                  # storage for outputs

Run:
    modal run ybf_dpo_modal.py                   # full training
    modal run ybf_dpo_modal.py --quick           # 50-step sanity check

Output:
    Downloaded to ./modal_outputs/ybf_dpo_results.json
    Adapter weights to ./modal_outputs/final_adapter/
"""

import modal
from pathlib import Path

# Modal app + image
app = modal.App("ybf-toy-dpo")

# Image: base + ML stack + clone our repo
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

# Persistent volume for outputs
volume = modal.Volume.from_name("ybf-toy", create_if_missing=True)

@app.function(
    image=image,
    gpu="T4",                # free-tier-equivalent GPU class
    volumes={"/outputs": volume},
    timeout=3600,            # 1 hour ceiling
)
def train_dpo(quick: bool = False):
    import subprocess
    import shutil
    import os

    os.chdir("/root/repo/ybf_toy")
    cmd = ["python", "ybf_dpo_train.py", "--output_dir", "/outputs/ybf_dpo_model"]
    if quick:
        cmd.extend(["--epochs", "1", "--batch_size", "2"])
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3500)
    print("STDOUT:", result.stdout[-3000:])
    if result.returncode != 0:
        print("STDERR:", result.stderr[-3000:])
        raise RuntimeError(f"Training failed (exit {result.returncode})")

    # Read eval results back
    eval_path = "/outputs/ybf_dpo_model/eval_results.json"
    if os.path.exists(eval_path):
        with open(eval_path) as f:
            return f.read()
    return "(no eval_results.json produced)"


@app.local_entrypoint()
def main(quick: bool = False):
    print(f"Starting DPO training on Modal T4 (quick={quick})...")
    result = train_dpo.remote(quick=quick)
    print("\n=== Eval results ===")
    print(result)
    # Save locally
    out_dir = Path("modal_outputs")
    out_dir.mkdir(exist_ok=True)
    (out_dir / "ybf_dpo_results.json").write_text(result)
    print(f"\n✓ Saved → {out_dir / 'ybf_dpo_results.json'}")
