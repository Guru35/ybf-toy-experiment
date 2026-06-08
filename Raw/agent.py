"""Linear Q-Network agent for YBF-TOY experiment."""

import numpy as np
import os

ACTION_LIST = ["A", "B"]
ACTION_TO_IDX = {"A": 0, "B": 1}


class YBFAgent:
    """
    Linear Q-network: Q(s, a) = s @ W[:, a] + b[a]
    Input:  384-dim L2-normalized embedding
    Output: 2 Q-values [Q_A, Q_B]
    """

    def __init__(self, embedding_dim: int = 384):
        rng = np.random.default_rng(42)
        self.W = rng.normal(0, 0.01, (embedding_dim, 2)).astype(np.float32)
        self.b = np.zeros(2, dtype=np.float32)

    def predict(self, state_emb: np.ndarray) -> np.ndarray:
        """Returns [Q_A, Q_B]."""
        return state_emb @ self.W + self.b

    def choose_action(self, state_emb: np.ndarray, epsilon: float = 0.0) -> str:
        """Epsilon-greedy selection. Returns 'A' or 'B'."""
        if np.random.random() < epsilon:
            return np.random.choice(ACTION_LIST)
        q = self.predict(state_emb)
        # Tie-break: A wins (convention for equal scores)
        idx = int(np.argmax(q)) if q[0] != q[1] else 0
        return ACTION_LIST[idx]

    def update(self, state_emb: np.ndarray, action: str,
               reward: float, lr: float):
        """
        TD(0) update on MSE loss.
        dL/dW[:, a] = -2 * (reward - Q(s,a)) * s
        dL/db[a]    = -2 * (reward - Q(s,a))
        """
        a_idx = ACTION_TO_IDX[action]
        q_vals = self.predict(state_emb)
        error = reward - q_vals[a_idx]          # scalar
        self.W[:, a_idx] += lr * error * state_emb
        self.b[a_idx]    += lr * error

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        np.save(path, {"W": self.W, "b": self.b})
        print(f"  Agent saved → {path}")

    def load(self, path: str):
        data = np.load(path, allow_pickle=True).item()
        self.W = data["W"].astype(np.float32)
        self.b = data["b"].astype(np.float32)
        print(f"  Agent loaded ← {path}")
