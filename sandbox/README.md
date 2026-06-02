# JARVIS OMEGA Sandbox

This sandbox is a structured, auditable runtime environment for safe command execution.

## Structure
- `runs/`: persistent run metadata
- `artifacts/`: generated runtime artifacts
- `logs/`: sandbox-level logs
- `session.py`: isolated session lifecycle
- `policy.py`: command and path policy gate
- `executor.py`: supervised command execution with timeout and audit
- `process_guard.py`: process snapshot and process-tree termination
- `filesystem.py`: path-safe file IO helpers
- `audit.py`: JSONL audit logging utilities

## Safety Guarantees
- command policy blocking for destructive patterns
- workspace boundary enforcement
- process-tree termination on timeout
- structured execution logs
- audit trail for blocked/executed commands
