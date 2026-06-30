"""Operational runtime backbone.

A continuously-operating engine that starts, accepts work, schedules
execution across workers, emits a heartbeat, tracks operational state,
shuts down gracefully, and recovers from restart using persisted state.

This package is the executable spine the capability and intelligence layers
attach to. It reuses the canonical pipeline primitives (validation,
serialization, hashing, append-only persistence, truth ledger) rather than
duplicating them.
"""
