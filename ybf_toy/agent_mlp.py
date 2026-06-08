"""
2-layer MLP Q-network agent for YBF-TOY experiment.
Drop-in replacement for YBFAgent (linear).

Architecture: input_dim → 128 (ReLU) → 2
Loss: MSE TD(0) per action, hand-rolled backprop (no torch).

Same interface as YBFAgent: predict, choose_action, update, save, load.
Different weights file format so we don't overwrite the linear baseline.
"""

import numpy as np
import os

ACTION_LIST = ["A", "B"]
ACTION_TO_IDX = {"A": 0, "B": 1}


class YBFAgentMLP:
    """
    Q(s, a) = relu(s @ W1 + b1) @ W2[:, a] + b2[a]
    """

    def __init__(self, embedding_dim: int = 384, hidden_dim: int = 128, seed: int = 42):
        rng = np.random.default_rng(seed)
        # He init for ReLU layer
        self.W1 = rng.normal(0, np.sqrt(2.0 / embedding_dim),
                             (embedding_dim, hidden_dim)).astype(np.float32)
        self.b1 = np.zeros(hidden_dim, dtype=np.float32)
        # Small init for output head
        self.W2 = rng.normal(0, 0.01, (hidden_dim, 2)).astype(np.float32)
        self.b2 = np.zeros(2, dtype=np.float32)

    def _forward(self, state_emb: np.ndarray):
        z1 = state_emb @ self.W1 + self.b1            # (128,)
        h1 = np.maximum(z1, 0.0)                       # ReLU
        q  = h1 @ self.W2 + self.b2                    # (2,)
        return q, h1, z1

    def predict(self, state_emb: np.ndarray) -> np.ndarray:
        q, _, _ = self._forward(state_emb)
        return q

    def choose_action(self, state_emb: np.ndarray, epsilon: float = 0.0) -> str:
        if np.random.random() < epsilon:
            return np.random.choice(ACTION_LIST)
        q = self.predict(state_emb)
        idx = int(np.argmax(q)) if q[0] != q[1] else 0
        return ACTION_LIST[idx]

    def update(self, state_emb: np.ndarray, action: str,
               reward: float, lr: float):
        """
        TD(0) on MSE loss = (reward - Q[s,a])^2.
        Compute all gradients first (using pre-update W2[:, a] for the hidden
        gradient), then apply.
        """
        a = ACTION_TO_IDX[action]
        q, h1, z1 = self._forward(state_emb)
        error = reward - q[a]                          # scalar

        # Save pre-update W2 column for hidden-layer gradient
        w2_a = self.W2[:, a].copy()

        # Gradients (positive 'error' means we want Q[a] to go UP)
        # dQ[a]/dW2[:, a] = h1
        # dQ[a]/db2[a]    = 1
        grad_W2_a = error * h1                         # (128,)
        grad_b2_a = error                              # scalar

        # dQ[a]/dh1 = w2_a; dh1/dz1 = relu_mask
        relu_mask = (z1 > 0).astype(np.float32)
        dz1 = error * w2_a * relu_mask                 # (128,)

        # dz1/dW1 = state_emb (outer product); dz1/db1 = 1
        grad_W1 = np.outer(state_emb, dz1)             # (embedding_dim, 128)
        grad_b1 = dz1                                  # (128,)

        # Apply
        self.W2[:, a] += lr * grad_W2_a
        self.b2[a]    += lr * grad_b2_a
        self.W1       += lr * grad_W1
        self.b1       += lr * grad_b1

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        np.save(path, {"W1": self.W1, "b1": self.b1,
                       "W2": self.W2, "b2": self.b2})
        print(f"  MLP agent saved → {path}")

    def load(self, path: str):
        data = np.load(path, allow_pickle=True).item()
        self.W1 = data["W1"].astype(np.float32)
        self.b1 = data["b1"].astype(np.float32)
        self.W2 = data["W2"].astype(np.float32)
        self.b2 = data["b2"].astype(np.float32)
        print(f"  MLP agent loaded ← {path}")
