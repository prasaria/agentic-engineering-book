#!/usr/bin/env python3
"""
Prompt classification for data analysis and logging.

Classifies user prompts into types and subtypes for understanding
workflow patterns and command usage. Extracts slash commands and
detects mentioned topics/chapters.

Non-blocking: all errors are suppressed to avoid breaking hook execution.
"""

import re
from typing import Any, List, Optional


def classify_prompt(prompt: str) -> dict[str, Any]:
    """
    Classify prompt into type and subtype.

    Args:
        prompt: User prompt text to classify

    Returns:
        Dictionary with classification fields:
        {
            "type": "command|question|instruction|orchestrator",
            "subtype": "slash_command|natural|continuation",
            "command_name": "/orchestrators:knowledge" or None,
            "detected_topics": ["chapter-6", "patterns"]
        }

    Classification rules:
        - Starts with /orchestrators: → type="orchestrator", subtype="slash_command"
        - Starts with / → type="command", subtype="slash_command"
        - Contains ? → type="question"
        - Short (<20 chars) → type="instruction", subtype="continuation"
        - Default → type="instruction", subtype="natural"

    Example:
        >>> classify_prompt("/orchestrators:knowledge Add section on patterns")
        {
            "type": "orchestrator",
            "subtype": "slash_command",
            "command_name": "/orchestrators:knowledge",
            "detected_topics": ["patterns"]
        }

        >>> classify_prompt("What are the twelve leverage points?")
        {
            "type": "question",
            "subtype": "natural",
            "command_name": None,
            "detected_topics": ["leverage-points"]
        }

    Notes:
        - Non-blocking: returns minimal classification on error
        - Topics detected via heuristics (chapter names, keywords)
        - Subtype "continuation" for short follow-up prompts
    """
    try:
        if not prompt or not isinstance(prompt, str):
            return _empty_classification()

        prompt_stripped = prompt.strip()

        # Detect prompt type
        prompt_type = detect_prompt_type(prompt_stripped)

        # Detect subtype
        subtype = _detect_subtype(prompt_stripped, prompt_type)

        # Extract command name if present
        command_name = extract_command_name(prompt_stripped)

        # Detect topics
        topics = detect_topics(prompt_stripped)

        return {
            "type": prompt_type,
            "subtype": subtype,
            "command_name": command_name,
            "detected_topics": topics,
        }

    except Exception:
        return _empty_classification()


def extract_command_name(prompt: str) -> Optional[str]:
    """
    Extract slash command name if present.

    Args:
        prompt: User prompt text

    Returns:
        Command name (e.g., "/orchestrators:knowledge"), or None

    Example:
        >>> extract_command_name("/orchestrators:knowledge Add patterns")
        "/orchestrators:knowledge"

        >>> extract_command_name("/book:toc")
        "/book:toc"

        >>> extract_command_name("Update the chapter")
        None

    Notes:
        - Extracts first word starting with /
        - Includes everything up to first space
        - Returns None if no slash command found
    """
    try:
        if not prompt or not prompt.strip().startswith("/"):
            return None

        # Extract first word (up to space or end of string)
        match = re.match(r"^(/[^\s]+)", prompt.strip())
        if match:
            return match.group(1)

        return None

    except Exception:
        return None


def detect_prompt_type(prompt: str) -> str:
    """
    Detect primary type: command, question, instruction, orchestrator.

    Args:
        prompt: User prompt text

    Returns:
        Type string: "orchestrator", "command", "question", or "instruction"

    Classification rules:
        1. Starts with /orchestrators: → "orchestrator"
        2. Starts with / → "command"
        3. Contains ? → "question"
        4. Default → "instruction"

    Example:
        >>> detect_prompt_type("/orchestrators:knowledge Add section")
        "orchestrator"

        >>> detect_prompt_type("/book:toc")
        "command"

        >>> detect_prompt_type("What is the prompt maturity model?")
        "question"

        >>> detect_prompt_type("Add a section on patterns")
        "instruction"

    Notes:
        - Simple heuristics, not perfect classification
        - Prioritizes orchestrator detection
        - Question mark anywhere triggers "question" type
    """
    try:
        if not prompt:
            return "instruction"

        prompt_stripped = prompt.strip()

        # Check for orchestrator command
        if prompt_stripped.startswith("/orchestrators:"):
            return "orchestrator"

        # Check for slash command
        if prompt_stripped.startswith("/"):
            return "command"

        # Check for question
        if "?" in prompt_stripped:
            return "question"

        # Default to instruction
        return "instruction"

    except Exception:
        return "instruction"


def detect_topics(prompt: str) -> List[str]:
    """
    Detect mentioned topics/chapters from prompt.

    Args:
        prompt: User prompt text

    Returns:
        List of detected topic strings

    Topics detected:
        - Chapter references (e.g., "chapter 6", "chapter-6")
        - Part references (e.g., "part 2")
        - Known concepts (e.g., "patterns", "orchestrator", "prompt")
        - File paths (e.g., "chapters/6-patterns")

    Example:
        >>> detect_topics("Update chapter 6 on patterns")
        ["chapter-6", "patterns"]

        >>> detect_topics("Add orchestrator pattern to part 2")
        ["part-2", "orchestrator", "patterns"]

        >>> detect_topics("Fix the prompt maturity model")
        ["prompt"]

    Notes:
        - Returns unique topics (no duplicates)
        - Case-insensitive matching
        - Heuristic-based, not comprehensive
    """
    try:
        if not prompt:
            return []

        topics = []
        prompt_lower = prompt.lower()

        # Detect chapter references
        chapter_matches = re.findall(r"chapter[\s-]*(\d+)", prompt_lower)
        for num in chapter_matches:
            topics.append(f"chapter-{num}")

        # Detect part references
        part_matches = re.findall(r"part[\s-]*(\d+)", prompt_lower)
        for num in part_matches:
            topics.append(f"part-{num}")

        # Detect known concepts
        concepts = [
            "patterns",
            "orchestrator",
            "prompt",
            "model",
            "context",
            "tool-use",
            "practices",
            "mental-models",
            "foundations",
            "leverage-points",
            "evaluation",
            "debugging",
            "cost",
            "latency",
            "production",
            "workflow",
            "knowledge",
        ]

        for concept in concepts:
            # Match whole word or with hyphens
            pattern = r"\b" + concept.replace("-", r"[\s-]?") + r"\b"
            if re.search(pattern, prompt_lower):
                topics.append(concept)

        # Detect file paths (chapters/N-name format)
        path_matches = re.findall(r"chapters/(\d+)-([a-z-]+)", prompt_lower)
        for num, name in path_matches:
            topics.append(f"chapter-{num}")
            topics.append(name)

        # Return unique topics
        return list(set(topics))

    except Exception:
        return []


def _detect_subtype(prompt: str, prompt_type: str) -> str:
    """
    Detect subtype: slash_command, natural, or continuation.

    Args:
        prompt: User prompt text
        prompt_type: Already-detected prompt type

    Returns:
        Subtype string

    Rules:
        - If type is "command" or "orchestrator" → "slash_command"
        - If prompt < 20 chars → "continuation"
        - Default → "natural"

    Notes:
        - Internal helper for classify_prompt
        - Continuation implies short follow-up message
    """
    try:
        # Commands and orchestrators are always slash_command
        if prompt_type in ["command", "orchestrator"]:
            return "slash_command"

        # Short prompts are likely continuations
        if len(prompt) < 20:
            return "continuation"

        # Default to natural language
        return "natural"

    except Exception:
        return "natural"


def _empty_classification() -> dict[str, Any]:
    """
    Return empty/default classification.

    Returns:
        Default classification dictionary

    Notes:
        - Used as fallback on errors
        - Provides safe defaults for all fields
    """
    return {
        "type": "instruction",
        "subtype": "natural",
        "command_name": None,
        "detected_topics": [],
    }
