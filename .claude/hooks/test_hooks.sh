#!/bin/bash
# Test script for hook implementations
# Verifies hooks can be executed and handle input correctly

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOOKS_DIR="$PROJECT_DIR/.claude/hooks"

echo "Testing Claude Code hooks..."
echo "Project: $PROJECT_DIR"
echo

# Test 1: user_prompt_submit.py
echo "Test 1: user_prompt_submit.py"
echo '{"session_id": "test-123", "prompt": "This is a test prompt"}' | \
  uv run "$HOOKS_DIR/user_prompt_submit.py"
echo "✓ user_prompt_submit.py executed successfully"
echo

# Test 2: pre_tool_use_logger.py - safe command
echo "Test 2: pre_tool_use_logger.py (safe command)"
echo '{"session_id": "test-123", "tool_name": "Read", "tool_input": {"file_path": "/tmp/test.txt"}}' | \
  uv run "$HOOKS_DIR/pre_tool_use_logger.py"
echo "✓ pre_tool_use_logger.py executed successfully (safe)"
echo

# Test 3: pre_tool_use_logger.py - dangerous command (should block)
echo "Test 3: pre_tool_use_logger.py (dangerous command - should block)"
if echo '{"session_id": "test-123", "tool_name": "Bash", "tool_input": {"command": "rm -rf /"}}' | \
  uv run "$HOOKS_DIR/pre_tool_use_logger.py" 2>&1; then
  echo "✗ FAILED: Dangerous command was not blocked"
  exit 1
else
  exit_code=$?
  if [ $exit_code -eq 2 ]; then
    echo "✓ pre_tool_use_logger.py correctly blocked dangerous command (exit code 2)"
  else
    echo "✗ FAILED: Wrong exit code $exit_code (expected 2)"
    exit 1
  fi
fi
echo

# Test 4: subagent_stop_logger.py
echo "Test 4: subagent_stop_logger.py"
echo '{"session_id": "test-123", "stop_hook_active": true, "transcript_path": "/tmp/transcript.jsonl"}' | \
  uv run "$HOOKS_DIR/subagent_stop_logger.py"
echo "✓ subagent_stop_logger.py executed successfully"
echo

# Test 5: pre_compact_handler.py
echo "Test 5: pre_compact_handler.py"
# Create a dummy transcript file
mkdir -p /tmp/test-transcripts
echo '{"role": "user", "content": "test"}' > /tmp/test-transcripts/test-transcript.jsonl
echo '{"session_id": "test-123", "transcript_path": "/tmp/test-transcripts/test-transcript.jsonl", "trigger": "manual"}' | \
  CLAUDE_PROJECT_DIR="$PROJECT_DIR" uv run "$HOOKS_DIR/pre_compact_handler.py"
echo "✓ pre_compact_handler.py executed successfully"
echo

# Test 6: orchestrator_context.py
echo "Test 6: orchestrator_context.py"
echo '{"session_id": "test-123", "prompt": "/orchestrators:knowledge some requirement"}' | \
  uv run "$HOOKS_DIR/orchestrator_context.py"
echo "✓ orchestrator_context.py executed successfully"
echo

# Test 7: orchestrator_guard.py - blocked tool in orchestrator context
echo "Test 7: orchestrator_guard.py (blocked tool in orchestrator mode)"
# First set orchestrator context
echo 'export CLAUDE_ORCHESTRATOR_CONTEXT="knowledge"' > "$HOOKS_DIR/.orchestrator_context"
if echo '{"session_id": "test-123", "tool_name": "Write", "tool_input": {}}' | \
  CLAUDE_ENV_FILE="$HOOKS_DIR/.orchestrator_context" uv run "$HOOKS_DIR/orchestrator_guard.py" 2>&1; then
  echo "✗ FAILED: Write was not blocked in orchestrator mode"
  exit 1
else
  exit_code=$?
  if [ $exit_code -eq 2 ]; then
    echo "✓ orchestrator_guard.py correctly blocked Write in orchestrator mode (exit code 2)"
  else
    echo "✗ FAILED: Wrong exit code $exit_code (expected 2)"
    exit 1
  fi
fi
# Clear orchestrator context
rm -f "$HOOKS_DIR/.orchestrator_context"
echo

echo "=========================================="
echo "All tests passed! ✓"
echo "=========================================="
echo
echo "Hooks are ready for use in Claude Code sessions."
echo "They will automatically log to .claude/logs/ when configured in settings.json"
