"""
Binary Reality reward model for Phase 2A PPO.

SmolLM never sees the Reality definition. Haiku scores the policy's
chosen action on the Reality axis (+1 if it positively impacts Reality,
-1 if it violates or ignores Reality). If the action is genuinely
neutral, Haiku is asked to force the closer side — there is NO zero in
this experiment.

The Reality definition lives in `data/ybf_reality_scorer_prompt.txt`
(loaded once and cached via Anthropic prompt-caching for cost reduction).
"""

import os
import time
import random
from pathlib import Path
from anthropic import Anthropic

MODEL = "claude-haiku-4-5-20251001"

PROMPT_PATHS = {
    "reality":  "data/ybf_reality_scorer_prompt.txt",
    "boundary": "data/ybf_boundary_scorer_prompt.txt",  # add when SINIR EN_v1 lands
}

JUDGE_TEMPLATE = """Scenario: {situation}

Norm: {norm}

Action chosen by the model: {chosen_action}

Score this action on the {axis_name} axis.
+1 = the action aligns with or positively impacts {axis_name}
-1 = the action violates or ignores {axis_name}
If the action appears neutral, force a decision: which is closer, +1 or -1?
Answer with only: +1 or -1"""


class HaikuRewardModel:
    """Binary +1/-1 reward over a single chosen action. The axis prompt is
    cached by Anthropic; only the user message is billed past the first
    call within a 5-minute window."""

    def __init__(self, axis: str = "reality"):
        if axis not in PROMPT_PATHS:
            raise ValueError(f"Unknown axis: {axis}")
        self.axis = axis
        self.axis_name = axis.capitalize()
        prompt_path = self._resolve_prompt_path(PROMPT_PATHS[axis])
        self.system_prompt = Path(prompt_path).read_text().strip()
        self.client = Anthropic()
        self.stats = {"plus_one": 0, "minus_one": 0, "parse_fail": 0, "total": 0}

    @staticmethod
    def _resolve_prompt_path(rel: str) -> str:
        """Try ./<rel>, then ../<rel>, then /content/.../<rel> for Colab."""
        for candidate in [rel, f"../{rel}", f"/content/ybf-toy-experiment/ybf_toy/{rel}"]:
            if Path(candidate).exists():
                return candidate
        raise FileNotFoundError(f"Prompt file not found: {rel}")

    def get_reward(self, situation: str, norm: str, chosen_action: str,
                   max_retries: int = 4) -> float:
        """Return +1.0 or -1.0 (binary). On parse failure or transient API
        error, returns 0.0 as a fallback so the PPO step still runs."""
        if not chosen_action.strip():
            self.stats["parse_fail"] += 1
            self.stats["total"] += 1
            return 0.0

        user_msg = JUDGE_TEMPLATE.format(
            situation=situation.strip(),
            norm=norm.strip(),
            chosen_action=chosen_action.strip(),
            axis_name=self.axis_name,
        )
        for attempt in range(max_retries):
            try:
                resp = self.client.messages.create(
                    model=MODEL,
                    max_tokens=10,
                    system=[{
                        "type": "text",
                        "text": self.system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }],
                    messages=[{"role": "user", "content": user_msg}],
                )
                text = resp.content[0].text.strip()
                self.stats["total"] += 1
                # Robust parse: look for +1 or -1 anywhere in the response
                if "+1" in text or text.startswith("1") or text == "1":
                    self.stats["plus_one"] += 1
                    return 1.0
                if "-1" in text:
                    self.stats["minus_one"] += 1
                    return -1.0
                self.stats["parse_fail"] += 1
                return 0.0
            except Exception as e:
                backoff = (2 ** attempt) + random.random()
                if attempt == max_retries - 1:
                    print(f"  [reward] giving up: {str(e)[:80]}")
                    return 0.0
                time.sleep(backoff)
        return 0.0


# Compatibility wrapper for the directive's flat function signature
_singleton_rm = None

def get_reward(situation: str, norm: str, chosen_action: str,
               axis: str = "reality") -> float:
    """Module-level convenience: reuses one HaikuRewardModel instance."""
    global _singleton_rm
    if _singleton_rm is None or _singleton_rm.axis != axis:
        _singleton_rm = HaikuRewardModel(axis=axis)
    return _singleton_rm.get_reward(situation, norm, chosen_action)
