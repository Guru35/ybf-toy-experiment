"""YBF-TOY Experiment Configuration"""

ANTHROPIC_MODEL   = "claude-haiku-4-5-20251001"
EMBED_MODEL       = "sentence-transformers/all-MiniLM-L6-v2"

# Dataset
DATASET_NAME      = "demelin/moral_stories"
DATASET_SPLIT     = "full"
TOTAL_SCENARIOS   = 1200
TRAIN_RATIO       = 0.80
RANDOM_SEED       = 42

# Training
EPISODES          = 5
LEARNING_RATE     = 0.01
EPSILON_START     = 0.50
EPSILON_END       = 0.05
EPSILON_DECAY     = 0.85

# API
API_DELAY_SEC     = 0.4
MAX_RETRIES       = 3

# Reward (C8: veto rule)
VETO_REWARD       = -5.0   # any -1 axis → minimum of natural range
MAX_REWARD        = 5.0    # all 5 axes = +1

# Sanity gate (C6/C8)
MIN_A_BEATS_B_PCT = 70.0

# Paths
DATA_DIR          = "data"
RESULTS_DIR       = "results"
SCORES_CACHE_PATH = "data/scores_cache.json"
SCENARIOS_PATH    = "data/scenarios.json"
EMBEDDINGS_PATH   = "data/embeddings.npy"
MODEL_PATH        = "data/agent_weights.npy"

MIN_REWARD        = -5.0   # all 5 axes = -1
