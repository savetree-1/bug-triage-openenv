# REWARD_DESIGN.md — Bug Triage Reward & Grader Design

---

## Two Systems: Reward vs Grader

| | Step Reward | Grader Score |
|-|------------|-------------|
| Purpose | GRPO training signal | Hackathon evaluation |
| When | Every `step()` | Only at `done=True` |
| Range | [-0.5, 1.0] (shaped) | [0.0, 1.0] (strict) |
| Endpoint | Via observation `reward` | `/grader` endpoint |

**Mapping:** `reward = (grader_score × 1.5) − 0.5`
- Perfect score (1.0) → reward = +1.0
- Zero score (0.0) → reward = -0.5
- This shaping gives gradient signal even for bad predictions.

---

## Task 1 Reward: Bug Type Classification

| Agent Output | Score |
|-------------|-------|
| Correct type | **+1.0** |
| Wrong type | **0.0** |

Simple exact match. 6 possible types, so random baseline ≈ 0.167.

---

## Task 2 Reward: Priority Assignment

| Distance from Correct | Score |
|-----------------------|-------|
| Exact match | **1.00** |
| Off by 1 level | **0.67** |
| Off by 2 levels | **0.33** |
| Off by 3 levels | **0.00** |

**Why partial credit?** Priority has ordinal structure — predicting "high" when answer is "critical" is better than predicting "low".

---

## Task 3 Reward: Full Triage (Composite)

| Component | Weight | Scoring |
|-----------|--------|---------|
| Bug type correct | **0.30** | 1.0 exact, 0.0 else |
| Priority correct | **0.30** | Distance: 0→1.0, 1→0.67, 2→0.33, 3→0.0 |
| Developer correct | **0.20** | Exact→1.0, right specialty→0.5, else→0.0 |
| Action correct | **0.20** | Exact→1.0, adjacent→0.5, else→0.0 |

### Partial Credit Details

**Developer assignment:**
- Exact match to ground truth → 1.0
- Wrong person but has the right specialization for the bug type → 0.5
- No match → 0.0

**Action suggestion (adjacency map):**
```
fix_immediately  schedule_sprint     (0.5)
schedule_sprint  needs_more_info     (0.5)
wontfix  duplicate                   (0.5)
```

### Example Scoring
```
Ground truth: type=crash, priority=critical, dev=Alice, action=fix_immediately
Agent output: type=crash, priority=high,     dev=Bob,   action=fix_immediately

type:     crash == crash       → 1.0 × 0.30 = 0.30
priority: high vs critical     → 0.67 × 0.30 = 0.20
dev:      Bob vs Alice         → Bob knows crash → 0.5 × 0.20 = 0.10
action:   fix_immediately      → 1.0 × 0.20 = 0.20

Total: 0.80
```

---

## Why This Reward Design Is Meaningful

1. **Non-trivial** — random agent scores ~0.20 on Task 3; a good model should score 0.7+
2. **Decomposed** — each dimension provides independent learning signal
3. **Partial credit** — prevents plateau; agent improves incrementally
4. **Varies per bug** — different bugs have different answers, so grader scores vary (no fixed output)
5. **Production-relevant** — mirrors how humans evaluate triage quality

---

## Grader Code Locations

| Task | Grader File | Method |
|------|-------------|--------|
| task_1 | `graders/task1_grader.py` | `grade(episode_log, ground_truth) → float` |
| task_2 | `graders/task2_grader.py` | `grade(episode_log, ground_truth) → float` |
| task_3 | `graders/task3_grader.py` | `grade(episode_log, ground_truth) → float` |
