---
description: L2-Perf - Performance Tuning & Bottleneck Analysis.
---

# /profile

## 🎯 Goal
Identify and eliminate performance bottlenecks in the Jadzia-Core execution pipeline (Worker Loop, SQLite, LLM Latency).

## 🛠️ Analysis Vectors

### 1. Database Profiling (SQLite)
- Identify "Slow Queries": Use `EXPLAIN QUERY PLAN`.
- Check for Lock Contention: Analyze how long `FileLock` is held during `_sync_to_sqlite`.
- Index Audit: Check if frequently queried columns in `jadzia.db` are indexed.

### 2. Execution Pipeline Latency
- **LLM Turnaround**: Measure time from `process_message` start to LLM response.
- **Worker Overhead**: Measure the time spent in the 15s/2s polling loop.
- **I/O Bound**: Identify slow file reads/writes in `agent/state.py`.

### 3. Resource Consumption
- Memory leak check in the background worker.
- CPU spikes during large diff generation.

## 📈 Optimization Loop
1. **Measure**: Baseline current performance (e.g., "Avg task completion: 45s").
2. **Hypothesize**: "Adding an index to `task_id` will reduce lookup time by 200ms".
3. **Implement**: Surgical change.
4. **Verify**: Measure again. If no improvement $\to$ Rollback.

## 📤 Output Format

```text
BOTTLENECK_FOUND: [Module/Function]
METRIC: [Current Value] -> [Target Value]
PROPOSED_OPTIMIZATION: [Change]
EXPECTED_GAIN: [% or ms]

---
CURRENT_STAGE: L2-Profile
RECOMMENDED_NEXT: /implement
---
```
