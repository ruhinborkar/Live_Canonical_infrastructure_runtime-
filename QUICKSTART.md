# QUICKSTART

## Purpose

This repository implements a deterministic runtime infrastructure capable of:

- Append-only persistence
- Runtime reconstruction
- Replay execution
- Interrupted execution recovery
- Deterministic serialization validation
- Hostile runtime validation
- Runtime observability

## Runtime Entry Point

run_system.py

## Available Execution Modes

### Live Runtime

python run_system.py --mode live

### Replay Execution

python run_system.py --mode replay

### Recovery Execution

python run_system.py --mode recover

### Runtime Verification

python run_system.py --mode verify

## Expected Outputs

### Replay

REPLAY_VERIFIED

or

REPLAY_MISMATCH

### Recovery

RECOVERY_REQUIRED

or

RECOVERY_NOT_REQUIRED

### Verification

Structured failure detection output for:

- Duplicate packets
- Sequence corruption
- Trace mutation
- Invalid schema
- Partial replay corruption

## Validation Sequence

1. Execute live runtime
2. Execute replay validation
3. Execute recovery validation
4. Execute verification validation
5. Review generated outputs and logs

All execution paths are routed through run_system.py.
