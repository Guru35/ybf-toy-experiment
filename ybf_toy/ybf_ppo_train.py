"""
Phase 2A PPO training loop (Colab-native).

Pure-reward learning: SmolLM never sees the Reality definition. Haiku
scores each chosen action with binary +1/-1 and PPO updates the policy
from that scalar.

Public entry-point: run_ppo_experiment(scoring_mode='binary', version='ppo_v1')

Key differences from the Modal version:
  - Binary +1/-1 reward (no zero except on parse fail)
  - 20 rounds default with early stopping (3 consecutive rounds < 1pp OOD swing)
  - Best-OOD checkpoint saved to /content/drive/MyDrive/ybf_models/{version}/best_checkpoint
  - Final checkpoint always at .../{version}/final
  - Per-round JSON log at results/{version}_log.json
  - Grokking detection (OOD dip then recovery above baseline)
"""

import argparse, json, os, re, time, random
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from peft import LoraConfig

from ybf_reward_model import HaikuRewardModel


MODEL_NAME = "HuggingFaceTB/SmolLM-135M-Instruct"
LORA_R = 8
LORA_ALPHA = 16
TOTAL_ROUNDS = 20
BATCH_SIZE = 4
MAX_NEW_TOKENS = 25   # SmolLM tends to answer 'The answer is B.' — need ~8-15
                       # tokens to reach the letter; 25 gives headroom


POLICY_PROMPT_TEMPLATE = """You are making a moral decision. Read the situation carefully and choose the better action.

Situation: {situation}
Norm: {norm}

Option A: {action_a}
Option B: {action_b}

Which action is better? Reply with just one letter: A or B.

Answer:"""

_LETTER_RE = re.compile(r"\b([AB])\b")
_SIT_RE = re.compile(r"Situation:\s*(.*?)(?:\n\n|\Z)", re.DOTALL)
_INT_RE = re.compile(r"Intention:\s*(.*?)(?:\n\n|\Z)", re.DOTALL)


def parse_choice(response_text: str) -> str:
    if not response_text:
        return ""
    m = _LETTER_RE.search(response_text.strip().upper())
    return m.group(1) if m else ""


def format_policy_prompt(scenario: dict, tokenizer) -> str:
    msg = POLICY_PROMPT_TEMPLATE.format(
        situation=scenario["situation"].strip(),
        norm=scenario.get("norm", "").strip(),
        action_a=scenario["moral_action"].strip(),
        action_b=scenario["immoral_action"].strip(),
    )
    if hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(
                [{"role": "user", "content": msg}],
                tokenize=False, add_generation_prompt=True,
            )
        except Exception:
            pass
    return msg


def load_scenarios(path: str) -> list:
    """Two formats supported:
       (a) {scenario_id, situation, intention, norm, moral_action, immoral_action}
       (b) DPO {prompt, chosen, rejected} — fields recovered from prompt text"""
    out = []
    with open(path) as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            obj = json.loads(line)
            if "moral_action" in obj:
                out.append({
                    "id":              obj.get("scenario_id", obj.get("id", i)),
                    "situation":       obj.get("situation", ""),
                    "intention":       obj.get("intention", ""),
                    "norm":            obj.get("norm", ""),
                    "moral_action":    obj["moral_action"],
                    "immoral_action":  obj["immoral_action"],
                })
                continue
            if "prompt" in obj:
                s = _SIT_RE.search(obj["prompt"])
                n = _INT_RE.search(obj["prompt"])
                out.append({
                    "id":              obj.get("scenario_id", i),
                    "situation":       s.group(1).strip() if s else obj["prompt"][:200],
                    "intention":       n.group(1).strip() if n else "",
                    "norm":            "",
                    "moral_action":    obj["chosen"].strip(),
                    "immoral_action":  obj["rejected"].strip(),
                })
                continue
    return out


def evaluate(model, tokenizer, scenarios, reward_model, device,
             max_n: int = None, label: str = "eval") -> dict:
    """Greedy decode each scenario, score the picked action with the
    reward model, return aggregate accuracy/reward."""
    if max_n is not None:
        scenarios = scenarios[:max_n]
    parsed = 0
    plus_one_count = 0
    rewards = []
    for sc in scenarios:
        prompt = format_policy_prompt(sc, tokenizer)
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(
                **inputs, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        text = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:],
                                 skip_special_tokens=True)
        letter = parse_choice(text)
        if not letter:
            continue
        parsed += 1
        chosen = sc["moral_action"] if letter == "A" else sc["immoral_action"]
        r = reward_model.get_reward(sc["situation"], sc.get("norm", ""), chosen)
        rewards.append(r)
        if r > 0:
            plus_one_count += 1
    n = len(scenarios)
    return {
        "label":        label,
        "n":            n,
        "parsed":       parsed,
        "plus_one":     plus_one_count,
        "accuracy_pct": 100 * plus_one_count / n if n else 0.0,
        "mean_reward":  sum(rewards) / len(rewards) if rewards else 0.0,
    }


def train_one_round(model, ppo_trainer, tokenizer, scenarios, reward_model,
                     device, batch_size: int, log_every: int = 25):
    """One full pass through `scenarios`, doing PPO updates batch-by-batch."""
    n_full = (len(scenarios) // batch_size) * batch_size
    scenarios = scenarios[:n_full]
    t0 = time.time()
    for i in range(0, n_full, batch_size):
        batch = scenarios[i:i + batch_size]
        queries = [format_policy_prompt(sc, tokenizer) for sc in batch]
        q_tensors = [tokenizer(q, return_tensors="pt").input_ids[0].to(device)
                     for q in queries]
        r_tensors = ppo_trainer.generate(
            q_tensors, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
        response_texts = [
            tokenizer.decode(r[len(q):], skip_special_tokens=True)
            for q, r in zip(q_tensors, r_tensors)
        ]
        rewards = []
        for sc, rt in zip(batch, response_texts):
            letter = parse_choice(rt)
            if not letter:
                # Neutral signal on parse failure — penalizing -1 pushes the
                # model away from ANY output, creating a collapse spiral.
                rewards.append(torch.tensor(0.0).to(device))
                continue
            chosen = sc["moral_action"] if letter == "A" else sc["immoral_action"]
            r = reward_model.get_reward(sc["situation"], sc.get("norm", ""), chosen)
            rewards.append(torch.tensor(r).to(device))
        stats = ppo_trainer.step(q_tensors, r_tensors, rewards)
        if (i // batch_size) % log_every == 0:
            mean_r = sum(r.item() for r in rewards) / len(rewards)
            print(f"    batch {i//batch_size:4d}  mean_reward={mean_r:+.3f}  "
                  f"ppo_loss={stats.get('ppo/loss/total', 0):.4f}")
    return time.time() - t0


def detect_grokking(results: list, baseline_ood: float) -> bool:
    """Grokking: at some point OOD dipped below baseline and later
    climbed back to STRICTLY ABOVE baseline."""
    if len(results) < 4:
        return False
    oods = [r["ood_acc"] for r in results]
    saw_dip = False
    for i, v in enumerate(oods[1:], 1):
        if v < baseline_ood:
            saw_dip = True
        elif saw_dip and v > baseline_ood:
            return True
    return False


def run_ppo_experiment(
    scoring_mode: str = "binary",
    version: str = "ppo_v1",
    axis: str = "reality",
    train_file: str = "data/scenarios.json",
    test_file: str = None,    # None ⇒ use last 100 of train as held-out
    ood_file: str = "data/ybf_sinir_dpo_ood.jsonl",
    rounds: int = TOTAL_ROUNDS,
    batch_size: int = BATCH_SIZE,
    lr: float = 1.4e-5,
    lora_r: int = LORA_R,
    eval_n: int = 100,
    max_train_per_round: int = None,
    checkpoint_dir: str = "/content/drive/MyDrive/ybf_models",
    seed: int = 42,
):
    """Top-level entry point — what the notebook calls."""
    os.makedirs(f"{checkpoint_dir}/{version}", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    random.seed(seed)
    torch.manual_seed(seed)

    print("=" * 65)
    print(f"YBF PPO — version={version}  axis={axis}  scoring={scoring_mode}")
    print("=" * 65)

    # ── Load scenarios
    if train_file.endswith(".json") and not train_file.endswith(".jsonl"):
        # Raw scenarios.json shape (5-axis cache)
        raw = json.loads(Path(train_file).read_text())
        scenarios = [{
            "id":              s["id"],
            "situation":       s["situation"],
            "intention":       s["intention"],
            "norm":            s.get("norm", ""),
            "moral_action":    s["options"]["A"],
            "immoral_action":  s["options"]["B"],
        } for s in raw]
    else:
        scenarios = load_scenarios(train_file)

    if test_file:
        test_scenarios = load_scenarios(test_file)
    else:
        rng = random.Random(seed)
        rng.shuffle(scenarios)
        test_scenarios = scenarios[-eval_n:]
        scenarios = scenarios[:-eval_n]
    ood_scenarios = load_scenarios(ood_file) if Path(ood_file).exists() else []
    print(f"  Train pool:  {len(scenarios)}")
    print(f"  ID test:     {len(test_scenarios)}")
    print(f"  OOD:         {len(ood_scenarios)}")

    # ── Tokenizer + model + LoRA
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    lora_cfg = LoraConfig(
        r=lora_r, lora_alpha=LORA_ALPHA, lora_dropout=0.05,
        bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"],
    )
    model = AutoModelForCausalLMWithValueHead.from_pretrained(
        MODEL_NAME, peft_config=lora_cfg, torch_dtype=torch.bfloat16,
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # ── PPO config
    ppo_cfg = PPOConfig(
        model_name=MODEL_NAME, learning_rate=lr,
        batch_size=batch_size, mini_batch_size=batch_size,
        log_with=None, seed=seed,
    )
    ppo_trainer = PPOTrainer(
        config=ppo_cfg, model=model, ref_model=None, tokenizer=tokenizer,
    )

    rm = HaikuRewardModel(axis=axis)
    print(f"  Reward model: Haiku 4.5 + {axis} prompt ({len(rm.system_prompt)} chars)")

    # ── Round 0 baseline
    print(f"\n[Round 0 — baseline, no training]")
    base_id = evaluate(model, tokenizer, test_scenarios, rm, device, label="round_0_id")
    base_ood = evaluate(model, tokenizer, ood_scenarios, rm, device, label="round_0_ood") if ood_scenarios else None
    print(f"  ID  {base_id['plus_one']}/{base_id['parsed']} parsed (n={base_id['n']}) "
          f"acc={base_id['accuracy_pct']:.1f}%  mean_reward={base_id['mean_reward']:+.3f}")
    if base_ood:
        print(f"  OOD {base_ood['plus_one']}/{base_ood['parsed']} parsed (n={base_ood['n']}) "
              f"acc={base_ood['accuracy_pct']:.1f}%  mean_reward={base_ood['mean_reward']:+.3f}")

    results = [{
        "round":         0,
        "id_acc":        base_id["accuracy_pct"],
        "ood_acc":       base_ood["accuracy_pct"] if base_ood else None,
        "id_reward":     base_id["mean_reward"],
        "ood_reward":    base_ood["mean_reward"] if base_ood else None,
    }]
    baseline_ood = base_ood["accuracy_pct"] if base_ood else 0.0
    best_ood = baseline_ood
    best_round = 0

    # ── Training rounds
    for round_num in range(1, rounds + 1):
        print(f"\n[Round {round_num}]")
        rng = random.Random(seed + round_num)
        rnd = list(scenarios)
        rng.shuffle(rnd)
        if max_train_per_round:
            rnd = rnd[:max_train_per_round]
        train_t = train_one_round(model, ppo_trainer, tokenizer, rnd, rm, device, batch_size)
        print(f"  Round {round_num} training done in {train_t/60:.1f}m")

        rnd_id = evaluate(model, tokenizer, test_scenarios, rm, device, label=f"round_{round_num}_id")
        rnd_ood = evaluate(model, tokenizer, ood_scenarios, rm, device, label=f"round_{round_num}_ood") if ood_scenarios else None
        prev_ood = results[-1]["ood_acc"] or 0.0
        delta_ood = (rnd_ood["accuracy_pct"] - prev_ood) if rnd_ood else 0.0
        print(f"  ID  acc={rnd_id['accuracy_pct']:.1f}%  mean_reward={rnd_id['mean_reward']:+.3f}")
        if rnd_ood:
            print(f"  OOD acc={rnd_ood['accuracy_pct']:.1f}%  mean_reward={rnd_ood['mean_reward']:+.3f}  "
                  f"Δ={delta_ood:+.1f}pp")

        results.append({
            "round":         round_num,
            "id_acc":        rnd_id["accuracy_pct"],
            "ood_acc":       rnd_ood["accuracy_pct"] if rnd_ood else None,
            "id_reward":     rnd_id["mean_reward"],
            "ood_reward":    rnd_ood["mean_reward"] if rnd_ood else None,
        })

        if rnd_ood and rnd_ood["accuracy_pct"] > best_ood:
            best_ood = rnd_ood["accuracy_pct"]
            best_round = round_num
            ppo_trainer.save_pretrained(f"{checkpoint_dir}/{version}/best_checkpoint")
            print(f"  *** New best OOD: {best_ood:.1f}% at round {round_num} ***")

        # Early stopping: 3 consecutive rounds with <1pp OOD swing
        if round_num >= 4:
            last3 = [r["ood_acc"] for r in results[-3:] if r["ood_acc"] is not None]
            if len(last3) == 3 and (max(last3) - min(last3)) < 1.0:
                print(f"[Early stop] OOD stabilized at round {round_num}")
                break

    # ── Final adapter + log
    ppo_trainer.save_pretrained(f"{checkpoint_dir}/{version}/final")
    grok = detect_grokking(results, baseline_ood) if base_ood else False
    summary = {
        "version":          version,
        "axis":             axis,
        "scoring_mode":     scoring_mode,
        "model":            MODEL_NAME,
        "lora_r":           lora_r,
        "rounds_planned":   rounds,
        "rounds_actual":    len(results) - 1,
        "baseline_ood":     baseline_ood,
        "best_ood":         best_ood,
        "best_ood_round":   best_round,
        "final_ood":        results[-1]["ood_acc"],
        "grokking":         grok,
        "reward_stats":     rm.stats,
        "results":          results,
    }
    log_path = f"results/{version}_log.json"
    with open(log_path, "w") as f:
        json.dump(summary, f, indent=2)

    # ── Print summary table
    print(f"\n{'='*60}")
    print(f"Round  |  ID Acc  |  OOD Acc  |  Δ OOD")
    print(f"{'-'*60}")
    for i, r in enumerate(results):
        prev_ood = results[i-1]["ood_acc"] if i > 0 else None
        delta = (r["ood_acc"] - prev_ood) if prev_ood is not None and r["ood_acc"] is not None else None
        delta_str = f"{delta:+.1f}" if delta is not None else "—"
        print(f"  {r['round']:>3d}  |  {r['id_acc']:>5.1f}%  |  {r['ood_acc'] or 0:>5.1f}%   |  {delta_str:>5s}")
    print(f"{'='*60}")
    print(f"Best OOD:    {best_ood:.1f}% at round {best_round}")
    print(f"Final OOD:   {results[-1]['ood_acc']:.1f}%" if results[-1]['ood_acc'] is not None else "Final OOD: n/a")
    print(f"Grokking:    {'var' if grok else 'yok'}")
    print(f"Log saved → {log_path}")
    print(f"Best ckpt   → {checkpoint_dir}/{version}/best_checkpoint")
    print(f"Final ckpt  → {checkpoint_dir}/{version}/final")

    return summary


# CLI fallback (rarely used; notebook calls run_ppo_experiment directly)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version",        default="ppo_v1")
    parser.add_argument("--axis",           default="reality")
    parser.add_argument("--rounds",         type=int, default=TOTAL_ROUNDS)
    parser.add_argument("--max_train_per_round", type=int, default=None)
    args = parser.parse_args()
    run_ppo_experiment(
        version=args.version, axis=args.axis,
        rounds=args.rounds, max_train_per_round=args.max_train_per_round,
    )
