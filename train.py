"""Training loop for YBF-TOY experiment."""

import random
import numpy as np
from scorer import _cache_key


def better_action(scores_cache: dict, scenario: dict) -> str:
    """Returns which action (A or B) has higher reward. Tie → A."""
    r_a = scores_cache[_cache_key(scenario["id"], "A")]["reward"]
    r_b = scores_cache[_cache_key(scenario["id"], "B")]["reward"]
    return "A" if r_a >= r_b else "B"


def train(agent, train_scenarios: list, embeddings: np.ndarray,
          scores_cache: dict, episodes: int, lr: float,
          epsilon_start: float, epsilon_end: float, epsilon_decay: float):
    """
    Training loop — NO API calls, runs entirely from cache.
    Returns: list of per-episode log dicts.
    """
    epsilon = epsilon_start
    training_log = []

    for ep in range(episodes):
        ep_rewards = []
        correct = 0
        indices = list(range(len(train_scenarios)))
        random.shuffle(indices)

        for idx in indices:
            s = train_scenarios[idx]
            # C4: use embed_idx, not id
            state_emb = embeddings[s["embed_idx"]]

            action = agent.choose_action(state_emb, epsilon)
            reward = scores_cache[_cache_key(s["id"], action)]["reward"]

            agent.update(state_emb, action, reward, lr)
            ep_rewards.append(reward)

            if action == better_action(scores_cache, s):
                correct += 1

        epsilon = max(epsilon_end, epsilon * epsilon_decay)
        avg_r = float(np.mean(ep_rewards))
        acc   = correct / len(train_scenarios) * 100

        log = {
            "episode":       ep + 1,
            "avg_reward":    round(avg_r, 4),
            "correct_pct":   round(acc,  2),
            "epsilon":       round(epsilon, 4),
        }
        training_log.append(log)
        print(f"  Ep {ep+1}/{episodes} | "
              f"avg reward: {avg_r:+6.3f} | "
              f"correct: {acc:5.1f}% | ε={epsilon:.3f}")

    return training_log
