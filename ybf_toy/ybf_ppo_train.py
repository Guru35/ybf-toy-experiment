"""
YBF Phase 2A — PPO training: pure-reward learning, no axis definition shown
to the policy model.

Loop:
  for round in N_ROUNDS:
    for batch of scenarios:
      query  = format prompt (situation + intention + Action A + Action B)
      response = policy.generate(query)  # 1-2 tokens, "A" or "B"
      chosen_letter = parse(response)
      reward = HaikuRewardModel.score(scenario, chosen_letter)  # ±1
      ppo_trainer.step(query, response, reward)
    eval_round(train and ood)
    save checkpoint

Designed to run inside Modal container; sees inputs via mounted args.
"""

import argparse, json, os, re, time, random
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from peft import LoraConfig, get_peft_model
from datasets import load_dataset

from ybf_reward_model import HaikuRewardModel


# Prompt shown to the POLICY model. CRITICAL: contains NO Reality definition.
POLICY_PROMPT = """Read the scenario and pick the better action.

Situation: {situation}

Intention: {intention}

Norm: {norm}

Action A: {moral_action}

Action B: {immoral_action}

Which action is better? Answer with just one letter: A or B.

Answer:"""


# Match first standalone A or B (word boundary) — handles "A.", "(A)", "A)",
# "The answer is A" etc. but not random "A" inside other words.
_LETTER_RE = re.compile(r"\b([AB])\b")


def parse_choice(response_text: str) -> str:
    """Extract first standalone A or B from response. Returns '' if neither."""
    if not response_text:
        return ""
    m = _LETTER_RE.search(response_text.strip().upper())
    return m.group(1) if m else ""


def format_prompt(scenario: dict, tokenizer=None) -> str:
    """Format scenario as chat-template prompt for instruct models.
    SmolLM-135M-Instruct ignores instructions without the chat template;
    fall back to raw prompt only if tokenizer not supplied."""
    msg = POLICY_PROMPT.format(
        situation=scenario["situation"].strip(),
        intention=scenario["intention"].strip(),
        norm=scenario.get("norm", "").strip(),
        moral_action=scenario["moral_action"].strip(),
        immoral_action=scenario["immoral_action"].strip(),
    )
    if tokenizer is not None and hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(
                [{"role": "user", "content": msg}],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            pass
    return msg


def evaluate(model, tokenizer, scenarios, reward_model, device,
             max_n: int = None, label: str = "eval") -> dict:
    """Sample greedy responses, score with reward model, return accuracy."""
    if max_n is not None:
        scenarios = scenarios[:max_n]
    correct = 0
    parsed = 0
    rewards_sum = 0.0
    for sc in scenarios:
        prompt = format_prompt(sc, tokenizer)
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=15,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        text = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:],
                                 skip_special_tokens=True)
        letter = parse_choice(text)
        if not letter:
            continue
        parsed += 1
        r = reward_model.score(
            sc["situation"], sc["intention"], sc.get("norm", ""),
            sc["moral_action"], sc["immoral_action"], letter,
        )
        rewards_sum += r
        if r > 0:
            correct += 1
    n = len(scenarios)
    return {
        "label":         label,
        "n":             n,
        "parsed":        parsed,
        "correct":       correct,
        "accuracy_pct":  100 * correct / n if n else 0.0,
        "mean_reward":   rewards_sum / n if n else 0.0,
    }


_SITUATION_RE = re.compile(r"Situation:\s*(.*?)(?:\n\n|\Z)", re.DOTALL)
_INTENTION_RE = re.compile(r"Intention:\s*(.*?)(?:\n\n|\Z)", re.DOTALL)


def load_scenarios(path: str) -> list:
    """Load scenarios from either of two formats:
       (a) Flat JSONL with moral_action/immoral_action fields (e.g. our
           /tmp/ppo_scenarios.jsonl converted from scenarios.json).
       (b) DPO TRL format {prompt, chosen, rejected} — situation and
           intention are recovered by regex from the prompt text; chosen
           becomes moral_action, rejected becomes immoral_action.
    """
    scenarios = []
    with open(path) as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            obj = json.loads(line)
            if "moral_action" in obj:
                scenarios.append({
                    "id":              obj.get("scenario_id", obj.get("id", i)),
                    "situation":       obj.get("situation", ""),
                    "intention":       obj.get("intention", ""),
                    "norm":            obj.get("norm", ""),
                    "moral_action":    obj["moral_action"],
                    "immoral_action":  obj["immoral_action"],
                })
                continue
            # DPO format fallback
            if "prompt" in obj and "chosen" in obj and "rejected" in obj:
                prompt = obj["prompt"]
                s = _SITUATION_RE.search(prompt)
                n = _INTENTION_RE.search(prompt)
                scenarios.append({
                    "id":              obj.get("scenario_id", i),
                    "situation":       (s.group(1).strip() if s else prompt[:200]),
                    "intention":       (n.group(1).strip() if n else ""),
                    "norm":            "",
                    "moral_action":    obj["chosen"].strip(),
                    "immoral_action":  obj["rejected"].strip(),
                })
                continue
            raise ValueError(
                f"Unrecognized scenario shape at {path}:{i+1}; expected "
                f"either moral_action/immoral_action or prompt/chosen/rejected"
            )
    return scenarios


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",       default="HuggingFaceTB/SmolLM-135M-Instruct")
    parser.add_argument("--axis",        default="reality", choices=["reality", "boundary"])
    parser.add_argument("--train_file",  required=True)
    parser.add_argument("--ood_file",    default=None)
    parser.add_argument("--output_dir",  required=True)
    parser.add_argument("--rounds",      type=int, default=5)
    parser.add_argument("--batch_size",  type=int, default=4)
    parser.add_argument("--ppo_lr",      type=float, default=1.4e-5)
    parser.add_argument("--lora_r",      type=int,   default=8)
    parser.add_argument("--lora_alpha",  type=int,   default=16)
    parser.add_argument("--max_scenarios_per_round", type=int, default=None,
                        help="Truncate scenarios per round (smoke test).")
    parser.add_argument("--eval_n",      type=int, default=100,
                        help="Number of held-out samples for per-round eval.")
    parser.add_argument("--seed",        type=int, default=42)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    print("=" * 65)
    print(f"YBF PPO — axis={args.axis}, base={args.model}")
    print("=" * 65)

    # ---- Load scenarios
    print(f"\n[1/5] Loading scenarios...")
    scenarios = load_scenarios(args.train_file)
    print(f"  Train: {len(scenarios)}")
    ood_scenarios = []
    if args.ood_file and os.path.exists(args.ood_file):
        ood_scenarios = load_scenarios(args.ood_file)
        print(f"  OOD:   {len(ood_scenarios)}")

    # ---- Load model with value head + LoRA
    print(f"\n[2/5] Loading model + LoRA...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    lora_cfg = LoraConfig(
        r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=0.05,
        bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj"],
    )
    model = AutoModelForCausalLMWithValueHead.from_pretrained(
        args.model, peft_config=lora_cfg, torch_dtype=torch.bfloat16,
    )
    # Ref model = base (no LoRA) — TRL handles this internally with LoRA setup
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Device: {device}")

    # ---- PPO config
    ppo_cfg = PPOConfig(
        model_name=args.model,
        learning_rate=args.ppo_lr,
        batch_size=args.batch_size,
        mini_batch_size=args.batch_size,
        log_with=None,
        seed=args.seed,
    )
    trainer = PPOTrainer(
        config=ppo_cfg, model=model, ref_model=None, tokenizer=tokenizer,
    )

    # ---- Reward model
    print(f"\n[3/5] Initializing reward model (Haiku, axis={args.axis})...")
    rm = HaikuRewardModel(axis=args.axis)
    print(f"  System prompt loaded: {len(rm.system_prompt)} chars")

    # ---- Held-out eval set (drawn from end of training, never trained on)
    rng = random.Random(args.seed)
    rng.shuffle(scenarios)
    eval_n = min(args.eval_n, len(scenarios) // 5)
    held_out = scenarios[-eval_n:]
    train_pool = scenarios[:-eval_n]
    print(f"\n[4/5] Held-out for per-round eval: {len(held_out)} | "
          f"Train pool: {len(train_pool)}")

    # ---- Round 0 baseline
    print("\n[Round 0 — baseline, no training]")
    base_id = evaluate(trainer.model, tokenizer, held_out, rm, device,
                       label="round_0_id")
    print(f"  ID  {base_id['correct']}/{base_id['parsed']} = {base_id['accuracy_pct']:.1f}%   "
          f"mean_reward={base_id['mean_reward']:+.3f}")
    if ood_scenarios:
        base_ood = evaluate(trainer.model, tokenizer, ood_scenarios, rm, device,
                            label="round_0_ood")
        print(f"  OOD {base_ood['correct']}/{base_ood['parsed']} = {base_ood['accuracy_pct']:.1f}%   "
              f"mean_reward={base_ood['mean_reward']:+.3f}")

    all_results = {"round_0": {"id": base_id, "ood": base_ood if ood_scenarios else None}}

    # ---- Training rounds
    print(f"\n[5/5] PPO training, {args.rounds} rounds × "
          f"{len(train_pool) if not args.max_scenarios_per_round else args.max_scenarios_per_round} scenarios")
    for round_idx in range(1, args.rounds + 1):
        print(f"\n[Round {round_idx}]")
        rnd_scenarios = list(train_pool)
        rng.shuffle(rnd_scenarios)
        if args.max_scenarios_per_round:
            rnd_scenarios = rnd_scenarios[:args.max_scenarios_per_round]
        # Truncate to a multiple of batch_size — TRL 0.11.4 PPOTrainer.step
        # rejects partial batches (the last 2 of 50 with batch_size=4).
        n_full = (len(rnd_scenarios) // args.batch_size) * args.batch_size
        rnd_scenarios = rnd_scenarios[:n_full]
        t0 = time.time()
        for i in range(0, len(rnd_scenarios), args.batch_size):
            batch = rnd_scenarios[i:i + args.batch_size]
            queries = [format_prompt(sc, tokenizer) for sc in batch]
            q_tensors = [tokenizer(q, return_tensors="pt").input_ids[0].to(device)
                         for q in queries]
            r_tensors = trainer.generate(
                q_tensors, max_new_tokens=15, do_sample=False,
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
                    rewards.append(torch.tensor(-0.1).to(device))
                    continue
                r = rm.score(sc["situation"], sc["intention"], sc.get("norm", ""),
                             sc["moral_action"], sc["immoral_action"], letter)
                rewards.append(torch.tensor(r).to(device))
            stats = trainer.step(q_tensors, r_tensors, rewards)
            if (i // args.batch_size) % 25 == 0:
                mean_r = sum(r.item() for r in rewards) / len(rewards)
                print(f"  [r{round_idx} b{i//args.batch_size:4d}] "
                      f"mean_reward={mean_r:+.3f} ppo_loss={stats.get('ppo/loss/total', 0):.4f}")

        round_t = time.time() - t0
        print(f"  Round {round_idx} training done in {round_t/60:.1f}m")

        # eval
        print(f"  [Round {round_idx} eval]")
        rnd_id = evaluate(trainer.model, tokenizer, held_out, rm, device,
                          label=f"round_{round_idx}_id")
        print(f"    ID  {rnd_id['correct']}/{rnd_id['parsed']} = {rnd_id['accuracy_pct']:.1f}%   "
              f"mean_reward={rnd_id['mean_reward']:+.3f}")
        rnd_ood = None
        if ood_scenarios:
            rnd_ood = evaluate(trainer.model, tokenizer, ood_scenarios, rm, device,
                                label=f"round_{round_idx}_ood")
            print(f"    OOD {rnd_ood['correct']}/{rnd_ood['parsed']} = {rnd_ood['accuracy_pct']:.1f}%   "
                  f"mean_reward={rnd_ood['mean_reward']:+.3f}")
        all_results[f"round_{round_idx}"] = {"id": rnd_id, "ood": rnd_ood}

        # checkpoint
        ckpt_path = os.path.join(args.output_dir, f"round_{round_idx}")
        trainer.save_pretrained(ckpt_path)
        print(f"    saved → {ckpt_path}")

    # ---- Save final adapter + eval results
    final_path = os.path.join(args.output_dir, "final_adapter")
    trainer.save_pretrained(final_path)
    eval_path = os.path.join(args.output_dir, "eval_results.json")
    summary = {
        "axis":            args.axis,
        "model":           args.model,
        "rounds":          args.rounds,
        "lora_r":          args.lora_r,
        "rewards_stats":   rm.stats(),
        "rounds_data":     all_results,
    }
    with open(eval_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n✓ Done. eval_results → {eval_path}")
    print(f"  Final adapter → {final_path}")


if __name__ == "__main__":
    main()
