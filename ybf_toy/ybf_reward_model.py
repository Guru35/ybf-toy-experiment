"""
Haiku-based reward model for YBF Phase 2A (PPO pure-reward learning).

The Reality definition is loaded here and NEVER passed to the policy model
(SmolLM). The policy only ever sees the raw scenario and is asked to pick
an action. This module judges the policy's pick against the Reality axis
using Haiku, and returns +1 for "correct" or -1 for "incorrect".

Usage:
    from ybf_reward_model import HaikuRewardModel
    rm = HaikuRewardModel(axis="reality")
    reward = rm.score(situation, intention, norm, moral_action, immoral_action,
                      chosen_letter="A")
    # reward ∈ {-1.0, +1.0, 0.0 on parse failure}

Modal setup: container must have ANTHROPIC_API_KEY env var. Add via:
    modal secret create anthropic-api-key ANTHROPIC_API_KEY=<key>
and attach with `secrets=[modal.Secret.from_name("anthropic-api-key")]`.
"""

import os
import time
import random
from pathlib import Path
from anthropic import Anthropic

_PROMPT_PATHS = {
    "reality":  "Raw/YBF_Reality_Definition_EN_v1.txt",
    "boundary": "Raw/YBF_Reality_Definition_EN_v1.txt",  # placeholder until SINIR EN_v1 is written
}

MODEL = "claude-haiku-4-5-20251001"

JUDGE_TEMPLATE = """Situation: {situation}

Intention: {intention}

Norm: {norm}

Action A: {moral_action}

Action B: {immoral_action}

The model chose Action {chosen_letter}.

Did the model pick the action that scores higher on the {axis_name} axis?
Reply with exactly one word: CORRECT or INCORRECT."""


class HaikuRewardModel:
    """Reward model that uses Claude Haiku 4.5 as the oracle judge.

    The axis definition prompt is loaded once at construction and cached via
    the Anthropic prompt-caching API (5-minute TTL) so subsequent calls only
    pay for the user message + completion.
    """

    def __init__(self, axis: str = "reality"):
        if axis not in _PROMPT_PATHS:
            raise ValueError(f"Unknown axis: {axis}. Choices: {list(_PROMPT_PATHS)}")
        self.axis = axis
        self.axis_name = axis.capitalize()
        prompt_path = Path(__file__).parent / _PROMPT_PATHS[axis]
        if not prompt_path.exists():
            # Try absolute path if running from container with /root/repo layout
            alt = Path("/root/repo/ybf_toy") / _PROMPT_PATHS[axis]
            if alt.exists():
                prompt_path = alt
            else:
                raise FileNotFoundError(f"Axis prompt not found: {prompt_path}")
        self.system_prompt = prompt_path.read_text().strip()
        self.client = Anthropic()
        self._call_count = 0
        self._correct_count = 0
        self._incorrect_count = 0
        self._parse_fail = 0

    def score(self, situation: str, intention: str, norm: str,
              moral_action: str, immoral_action: str,
              chosen_letter: str, max_retries: int = 4) -> float:
        """Return +1.0 if chosen_letter scores higher on the axis, -1.0 otherwise.
        Returns 0.0 on parse/network failure (treated as no-signal episode)."""
        if chosen_letter not in ("A", "B"):
            return 0.0
        user_msg = JUDGE_TEMPLATE.format(
            situation=situation.strip(),
            intention=intention.strip(),
            norm=norm.strip(),
            moral_action=moral_action.strip(),
            immoral_action=immoral_action.strip(),
            chosen_letter=chosen_letter,
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
                text = resp.content[0].text.strip().upper()
                self._call_count += 1
                if "CORRECT" in text and "INCORRECT" not in text:
                    self._correct_count += 1
                    return 1.0
                if "INCORRECT" in text:
                    self._incorrect_count += 1
                    return -1.0
                self._parse_fail += 1
                return 0.0
            except Exception as e:
                backoff = (2 ** attempt) + random.random()
                if attempt == max_retries - 1:
                    print(f"  [reward] giving up: {str(e)[:80]}")
                    return 0.0
                time.sleep(backoff)
        return 0.0

    def stats(self) -> dict:
        return {
            "calls":        self._call_count,
            "correct":      self._correct_count,
            "incorrect":    self._incorrect_count,
            "parse_fail":   self._parse_fail,
        }
