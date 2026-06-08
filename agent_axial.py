"""
Axial Q-network — per-axis input feeding.

Architecture difference vs YBFAgent (linear, 384-in, 2-out):
  - Input is per-action: emb (384) + axis_vec_of_that_action (5) = 389-dim
  - Output is scalar Q (one number per forward call)
  - choose_action computes Q twice (once for each action's input), argmax.

This means at decision time the agent SEES the YBF axis values for both
choices and can in principle reason about which is better axis-by-axis,
including detecting veto patterns. Whether it actually does so is what
Test 5 measures.
"""

import numpy as np
import os

ACTION_LIST = ["A", "B"]
ACTION_TO_IDX = {"A": 0, "B": 1}


class YBFAgentAxial:
    """
    Q(input) = input @ W + b, where input = [embedding | axis_vector]
    Single scalar output. Called twice per scenario (once per action).
    """

    def __init__(self, input_dim: int = 389, seed: int = 42):
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 0.01, (input_dim, 1)).astype(np.float32)
        self.b = np.zeros(1, dtype=np.float32)

    def predict(self, input_vec: np.ndarray) -> float:
        """Scalar Q for a single (state, action) input."""
        return float((input_vec @ self.W + self.b).item())

    def choose_action(self, input_a: np.ndarray, input_b: np.ndarray,
                      epsilon: float = 0.0) -> str:
        """Epsilon-greedy. Tie → 'A'."""
        if np.random.random() < epsilon:
            return np.random.choice(ACTION_LIST)
        q_a = self.predict(input_a)
        q_b = self.predict(input_b)
        return "A" if q_a >= q_b else "B"

    def update(self, input_vec: np.ndarray, reward: float, lr: float):
        """
        TD(0) on MSE: loss = (reward - Q(input))^2
        dL/dW = -2 * (reward - Q) * input → fold 2 into lr
        """
        q = self.predict(input_vec)
        error = reward - q
        self.W[:, 0] += lr * error * input_vec
        self.b[0]    += lr * error

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        np.save(path, {"W": self.W, "b": self.b})
        print(f"  Axial agent saved → {path}")

    def load(self, path: str):
        data = np.load(path, allow_pickle=True).item()
        self.W = data["W"].astype(np.float32)
        self.b = data["b"].astype(np.float32)
        print(f"  Axial agent loaded ← {path}")
