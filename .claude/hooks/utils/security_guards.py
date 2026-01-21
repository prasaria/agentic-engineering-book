#!/usr/bin/env python3
"""
Security guards for dangerous command and file access detection.

Provides pattern matching to detect potentially destructive operations:
- Dangerous rm commands (rm -rf, recursive deletion)
- Access to sensitive files (.env, credentials)

Used by PreToolUse hooks to warn or block risky operations.
"""

import re
from typing import Optional


# Patterns for dangerous rm commands
DANGEROUS_PATTERNS = [
    r"\brm\s+.*-[a-z]*r[a-z]*f",      # rm -rf variants (rm -rf, rm -fr, etc)
    r"\brm\s+--recursive\s+--force",  # rm --recursive --force
    r"\brm\s+.*\s+/\s*$",             # rm targeting root directory
    r"\brm\s+.*~",                    # rm targeting home directory (~)
    r"\brm\s+.*\$HOME",               # rm targeting $HOME
]

# Sensitive file patterns
SENSITIVE_FILE_PATTERNS = [
    r"\.env",
    r"\.env\.",
    r"credentials",
    r"secret",
    r"\.aws/credentials",
    r"\.ssh/id_",
]


def is_dangerous_rm_command(command: str) -> bool:
    """
    Detect potentially destructive rm commands.

    Args:
        command: Shell command string to analyze

    Returns:
        True if command matches dangerous patterns

    Examples:
        >>> is_dangerous_rm_command("rm -rf /")
        True
        >>> is_dangerous_rm_command("rm myfile.txt")
        False
        >>> is_dangerous_rm_command("rm -rf node_modules")
        True
    """
    if not command:
        return False

    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True

    return False


def is_env_file_access(tool_name: str, tool_input: dict) -> bool:
    """
    Detect access to sensitive environment files.

    Args:
        tool_name: Name of the tool being invoked
        tool_input: Parameters passed to the tool

    Returns:
        True if operation accesses sensitive files

    Examples:
        >>> is_env_file_access("Read", {"file_path": "/project/.env"})
        True
        >>> is_env_file_access("Write", {"file_path": "/project/config.yaml"})
        False
    """
    if not tool_input:
        return False

    # Check file_path parameter (Read, Write, Edit tools)
    file_path = tool_input.get("file_path", "")
    if file_path:
        for pattern in SENSITIVE_FILE_PATTERNS:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True

    # Check content parameter for Write tool
    content = tool_input.get("content", "")
    if content and tool_name == "Write":
        # Check if writing credentials/secrets
        for pattern in ["password", "api_key", "token", "secret"]:
            if re.search(pattern, content, re.IGNORECASE):
                return True

    return False


def get_blocked_reason(tool_name: str, tool_input: dict) -> Optional[str]:
    """
    Check if a tool invocation should be blocked and return reason.

    Args:
        tool_name: Name of the tool being invoked
        tool_input: Parameters passed to the tool

    Returns:
        Blocking reason string, or None if operation is safe

    Examples:
        >>> get_blocked_reason("Bash", {"command": "rm -rf /"})
        'Dangerous rm command detected: potential data loss'
        >>> get_blocked_reason("Read", {"file_path": ".env"})
        'Access to sensitive file: .env'
        >>> get_blocked_reason("Read", {"file_path": "config.yaml"})
        None
    """
    # Check for dangerous bash commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if is_dangerous_rm_command(command):
            return "Dangerous rm command detected: potential data loss"

    # Check for sensitive file access
    if tool_name in ["Read", "Write", "Edit"]:
        if is_env_file_access(tool_name, tool_input):
            file_path = tool_input.get("file_path", "")
            return f"Access to sensitive file: {file_path}"

    return None
