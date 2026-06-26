---
description: L-CRITICAL - Emergency Response Protocol.
---

# /panic

## 🎯 Goal
Restore system availability in the shortest possible time. Bypasses standard L0-L3 pipelines. Priority: **Availability > Consistency > Purity**.

## 🚨 Activation Criteria
- Production service is DOWN.
- Data corruption detected in `jadzia.db`.
- Critical security breach in progress.

## 🛠️ Emergency Procedure

### 1. Triage (3 Minutes)
- **Isolate**: Stop the service (`sudo systemctl stop jadzia.service`).
- **Snapshot**: Immediate backup of current (broken) state for later RCA.
- **Identify**: Is it Code, Config, or Data?

### 2. Fast-Path Restoration
Choose the fastest path to "Green":
- **Option A (Rollback)**: Revert to the last known stable git commit and DB backup.
- **Option B (Hot-Patch)**: Surgical fix of the crashing line (bypass `/blast`).
- **Option C (Safe-Mode)**: Disable the failing feature and restart the core.

### 3. Verification (Smoke Only)
- Restart service $\to$ `curl localhost:8000/health`.
- Verify core worker loop is not crashing.

### 4. Post-Mortem (MANDATORY)
Once the system is UP, you MUST immediately route to `/debug` to perform a full Root-Cause Analysis and then to `/handoff` to document the incident.

## 📤 Output Format

```text
PANIC_STATUS: [RESTORED | STILL_DOWN]
ACTION_TAKEN: [Rollback | Hot-patch | Safe-mode]
DOWNTIME: [Duration]
IMMEDIATE_NEXT: /debug (Post-Mortem)
---
```
