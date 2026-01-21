"""
Shared utilities for Claude Code hooks.

This package provides common functionality used across hook implementations:
- log_writer: JSONL append operations for session logs
- security_guards: Dangerous command and file access detection
- model_extractor: Model name extraction from transcripts with caching
"""

__all__ = ["log_writer", "security_guards", "model_extractor"]
