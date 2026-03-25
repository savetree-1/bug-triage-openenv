# TASKS.md — Bug Triage Environment Tasks

> 3 graded tasks, easy → medium → hard. Scores in [0.0, 1.0].

---

## Task 1 (Easy): Bug Type Classification

**Goal:** Given a bug report, classify its type.

**Output labels:** `crash` | `ui` | `performance` | `security` | `data_loss` | `compatibility`

**Grader:** Exact match → 1.0, wrong → 0.0

### Input Example
```
Title: "App crashes on iOS 17 when uploading files > 50MB"
Description: "Consistently crashes immediately on upload tap."
Logs: "FATAL: EXC_BAD_ACCESS KERN_INVALID_ADDRESS at 0x0"
```

### Expected Output
```json
{"task_id": "task_1", "bug_type": "crash"}
```

### Success Criteria
| Agent Output | Score |
|-------------|-------|
| `bug_type: "crash"` | 1.0 ✓ |
| `bug_type: "performance"` | 0.0 ✗ |
| Missing field | 0.0 ✗ |

---

## Task 2 (Medium): Priority Assignment

**Goal:** Given a bug report, assign the correct priority level.

**Output labels:** `low` | `medium` | `high` | `critical`

**Grader:** Distance-based partial credit.

### Input Example
```
Title: "SQL injection possible in search endpoint"
Description: "The /api/v1/search endpoint does not sanitize user input.
  Passing ' OR 1=1 -- returns all records."
Metadata: {"severity": "CVSS_9.8", "disclosure_deadline": "2025-03-27"}
```

### Expected Output
```json
{"task_id": "task_2", "priority": "critical"}
```

### Success Criteria (Partial Credit)
| Agent Output | Distance | Score |
|-------------|----------|-------|
| `priority: "critical"` | 0 | 1.00 ✓ |
| `priority: "high"` | 1 | 0.67 |
| `priority: "medium"` | 2 | 0.33 |
| `priority: "low"` | 3 | 0.00 ✗ |

---

## Task 3 (Hard): Full Bug Triage

**Goal:** Complete triage — classify + prioritize + assign developer + suggest action.

**Weights:** bug_type (30%) + priority (30%) + developer (20%) + action (20%)

### Input Example
```
Title: "Export to CSV corrupts data with special characters"
Description: "Characters like é, ü, 中文 replaced with question marks."
Logs: "UnicodeEncodeError: 'latin-1' codec can't encode character"
Metadata: {"affected_users": 3200, "regression": true}
```

### Expected Output
```json
{
  "task_id": "task_3",
  "bug_type": "data_loss",
  "priority": "high",
  "assigned_developer": "David",
  "suggested_action": "fix_immediately"
}
```

### Success Criteria (Composite)
| Dimension | Weight | Scoring |
|-----------|--------|---------|
| bug_type | 30% | exact match → 1.0, else 0.0 |
| priority | 30% | distance: 0→1.0, 1→0.67, 2→0.33, 3→0.0 |
| developer | 20% | exact→1.0, right specialization→0.5, else→0.0 |
| action | 20% | exact→1.0, adjacent→0.5, else→0.0 |

### Example Scoring
```
Agent output:  bug_type=data_loss ✓  priority=high ✓  dev=Alice (wrong, but knows data_loss) →0.5  action=fix_immediately ✓
Score = 0.30×1.0 + 0.30×1.0 + 0.20×0.5 + 0.20×1.0 = 0.30+0.30+0.10+0.20 = 0.90
```

---

## Bug Dataset (15 reports)

| Bug ID | Type | Priority | Developer | Action |
|--------|------|----------|-----------|--------|
| BUG-001 | crash | critical | Alice | fix_immediately |
| BUG-002 | ui | low | Carol | schedule_sprint |
| BUG-003 | performance | high | Alice | fix_immediately |
| BUG-004 | security | critical | Bob | fix_immediately |
| BUG-005 | data_loss | high | David | fix_immediately |
| BUG-006 | compatibility | high | Eve | fix_immediately |
| BUG-007 | ui | medium | Carol | schedule_sprint |
| BUG-008 | performance | critical | Alice | fix_immediately |
| BUG-009 | ui | medium | Carol | fix_immediately |
| BUG-010 | data_loss | critical | David | fix_immediately |
| BUG-011 | ui | low | Carol | schedule_sprint |
| BUG-012 | security | critical | Bob | fix_immediately |
| BUG-013 | compatibility | medium | Eve | schedule_sprint |
| BUG-014 | performance | high | Eve | fix_immediately |
| BUG-015 | ui | low | Carol | needs_more_info |
