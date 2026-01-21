#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///
"""
Session Logging Finalization - Stop Hook

Processes session logs and writes summary statistics.
Runs when the main agent stops (not subagents).
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import tempfile

# Import utilities
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from log_writer import get_session_log_path


def atomic_write(file_path: Path, data: dict):
    """Atomically write JSON data to file using temp file and rename."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file in same directory
    fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=f".{file_path.name}.",
        suffix=".tmp"
    )
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)

        # Atomic rename
        os.rename(temp_path, file_path)
    except Exception:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except Exception:
            pass
        raise


def update_agent_metrics(aggregated_dir: Path, session_metrics: dict):
    """Update agent_metrics.json with running totals."""
    agent_metrics_path = aggregated_dir / "agent_metrics.json"

    # Load existing or create new
    if agent_metrics_path.exists():
        with open(agent_metrics_path, "r") as f:
            data = json.load(f)
    else:
        data = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_sessions_analyzed": 0,
            "agents": {}
        }

    # Update totals
    data["total_sessions_analyzed"] += 1
    data["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Update per-agent metrics
    duration = session_metrics.get("duration_seconds", 0)
    for agent_type, count in session_metrics.get("agents_spawned", {}).items():
        if agent_type not in data["agents"]:
            data["agents"][agent_type] = {
                "total_invocations": 0,
                "total_duration_seconds": 0,
                "total_tool_calls": 0
            }

        agent = data["agents"][agent_type]
        agent["total_invocations"] += count

        # Estimate duration per agent (divide session duration by number of agents)
        # This is an approximation since we don't have per-agent timing yet
        num_agents = sum(session_metrics.get("agents_spawned", {}).values())
        if num_agents > 0 and duration:
            agent["total_duration_seconds"] += duration // num_agents

        # Tool calls are harder to attribute; skip for now or use heuristic
        # Could be enhanced by tracking tool calls per agent depth in future

    # Write atomically
    atomic_write(agent_metrics_path, data)


def update_tool_metrics(aggregated_dir: Path, session_metrics: dict, agent_depth: int):
    """Update tool_metrics.json with running totals."""
    tool_metrics_path = aggregated_dir / "tool_metrics.json"

    # Load existing or create new
    if tool_metrics_path.exists():
        with open(tool_metrics_path, "r") as f:
            data = json.load(f)
    else:
        data = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_sessions_analyzed": 0,
            "tools": {}
        }

    # Update totals
    data["total_sessions_analyzed"] += 1
    data["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Update per-tool metrics
    for tool_name, count in session_metrics.get("tool_breakdown", {}).items():
        if tool_name not in data["tools"]:
            data["tools"][tool_name] = {
                "total_calls": 0,
                "by_agent_depth": {}
            }

        tool = data["tools"][tool_name]
        tool["total_calls"] += count

        # Track by agent depth
        depth_key = str(agent_depth)
        tool["by_agent_depth"][depth_key] = tool["by_agent_depth"].get(depth_key, 0) + count

        # Special handling for Task tool
        if tool_name == "Task":
            if "spawned_agents" not in tool:
                tool["spawned_agents"] = {}

            for agent_type, agent_count in session_metrics.get("agents_spawned", {}).items():
                tool["spawned_agents"][agent_type] = \
                    tool["spawned_agents"].get(agent_type, 0) + agent_count

    # Write atomically
    atomic_write(tool_metrics_path, data)


def merge_aggregated_metrics(aggregated_path: Path, new_metrics: dict):
    """Merge new session metrics into daily aggregated file."""
    if aggregated_path.exists():
        # Load existing metrics
        with open(aggregated_path, "r") as f:
            existing = json.load(f)

        # Merge basic counts
        existing["sessions"] += 1
        existing["total_duration_seconds"] = existing.get("total_duration_seconds", 0) + new_metrics.get("duration_seconds", 0)
        existing["total_tool_calls"] += new_metrics["total_tool_calls"]
        existing["total_prompts"] += new_metrics["total_prompts"]

        # Merge tool breakdown
        for tool, count in new_metrics["tool_breakdown"].items():
            existing["tool_breakdown"][tool] = existing["tool_breakdown"].get(tool, 0) + count

        # Merge agent metrics
        if "agent_metrics" not in existing:
            existing["agent_metrics"] = {
                "total_spawned": 0,
                "total_completed": 0,
                "by_type": {}
            }

        existing["agent_metrics"]["total_spawned"] += new_metrics.get("agents_spawned_count", 0)
        existing["agent_metrics"]["total_completed"] += new_metrics.get("agents_completed_count", 0)

        for agent_type, count in new_metrics.get("agents_spawned", {}).items():
            existing["agent_metrics"]["by_type"][agent_type] = \
                existing["agent_metrics"]["by_type"].get(agent_type, 0) + count

        # Merge prompt metrics
        if "prompt_metrics" not in existing:
            existing["prompt_metrics"] = {
                "by_type": {},
                "orchestrator_commands": 0
            }

        for prompt_type, count in new_metrics.get("prompt_types", {}).items():
            existing["prompt_metrics"]["by_type"][prompt_type] = \
                existing["prompt_metrics"]["by_type"].get(prompt_type, 0) + count

        if new_metrics.get("orchestrator_contexts"):
            existing["prompt_metrics"]["orchestrator_commands"] += len(new_metrics["orchestrator_contexts"])

        # Merge cost metrics
        if "cost" not in existing:
            existing["cost"] = {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "estimated_total_usd": 0.0
            }

        cost = new_metrics.get("cost", {})
        existing["cost"]["total_input_tokens"] += cost.get("input_tokens", 0)
        existing["cost"]["total_output_tokens"] += cost.get("output_tokens", 0)
        existing["cost"]["estimated_total_usd"] += cost.get("estimated_cost_usd", 0.0)

        return existing
    else:
        # Create new metrics file
        return {
            "date": new_metrics["date"],
            "sessions": 1,
            "total_duration_seconds": new_metrics.get("duration_seconds", 0),
            "total_tool_calls": new_metrics["total_tool_calls"],
            "total_prompts": new_metrics["total_prompts"],
            "tool_breakdown": new_metrics["tool_breakdown"],
            "agent_metrics": {
                "total_spawned": new_metrics.get("agents_spawned_count", 0),
                "total_completed": new_metrics.get("agents_completed_count", 0),
                "by_type": new_metrics.get("agents_spawned", {})
            },
            "prompt_metrics": {
                "by_type": new_metrics.get("prompt_types", {}),
                "orchestrator_commands": len(new_metrics.get("orchestrator_contexts", []))
            },
            "cost": new_metrics.get("cost", {
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "estimated_total_usd": 0.0
            })
        }


def finalize_logging():
    """Finalize session logging and compute statistics."""
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "unknown")

        # Get session log path (checks env, state file, or discovers)
        session_log_path = get_session_log_path()
        if not session_log_path or not Path(session_log_path).exists():
            sys.exit(0)

        # Read session log and compute stats
        tool_counts = defaultdict(int)
        agent_spawned = defaultdict(int)
        agent_stopped = defaultdict(int)
        prompt_types = defaultdict(int)
        orchestrator_contexts = []
        total_tools = 0
        total_prompts = 0
        start_time = None
        orchestrator_context = None
        parent_session_id = None
        agent_depth = 0

        with open(session_log_path, "r") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    event_type = event.get("event")

                    if event_type == "session_start":
                        start_time = event.get("timestamp")
                        orchestrator_context = event.get("orchestrator_context")
                        parent_session_id = event.get("parent_session_id")
                        agent_depth = event.get("agent_depth", 0)
                    elif event_type == "user_prompt":
                        total_prompts += 1
                        # Extract prompt classification if available
                        prompt_class = event.get("prompt_classification", "unknown")
                        prompt_types[prompt_class] += 1
                    elif event_type == "tool_use":
                        total_tools += 1
                        tool_name = event.get("tool_name", "unknown")
                        tool_counts[tool_name] += 1

                        # Track agent invocations from Task tool
                        metadata = event.get("metadata", {})
                        if metadata and "subagent_type" in metadata:
                            agent_type = metadata["subagent_type"]
                            if agent_type:
                                agent_spawned[agent_type] += 1
                    elif event_type == "subagent_stop":
                        # Track agent completions (we can infer type from session relationships)
                        agent_stopped["unknown"] = agent_stopped.get("unknown", 0) + 1

                except json.JSONDecodeError:
                    continue

        # Track orchestrator usage if present
        if orchestrator_context:
            orchestrator_contexts.append(orchestrator_context)

        # Calculate session duration
        end_time = datetime.now(timezone.utc)
        duration_seconds = None
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                duration_seconds = int((end_time - start_dt).total_seconds())
            except Exception:
                pass

        # Calculate agent counts
        agents_spawned_count = sum(agent_spawned.values())
        agents_completed_count = sum(agent_stopped.values())

        # Write enhanced session end event with summary
        end_event = {
            "timestamp": end_time.isoformat(),
            "event": "session_end",
            "session_id": session_id,
            "parent_session_id": parent_session_id,
            "agent_depth": agent_depth,
            "summary": {
                "duration_seconds": duration_seconds,
                "total_tool_calls": total_tools,
                "total_prompts": total_prompts,
                "tool_breakdown": dict(tool_counts),
                "agents_spawned": dict(agent_spawned),
                "agents_completed": agents_completed_count,
                "prompt_types": dict(prompt_types),
                "orchestrator_contexts": orchestrator_contexts
            },
            "cost": {
                "input_tokens": 0,  # Not available from hooks currently
                "output_tokens": 0,
                "estimated_cost_usd": 0.0
            },
            "outcome": "completed"
        }

        # Append end event
        with open(session_log_path, "a") as f:
            f.write(json.dumps(end_event) + "\n")

        # Update daily aggregated metrics
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
        aggregated_dir = Path(project_dir) / ".claude" / "logs" / "aggregated"
        aggregated_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        aggregated_path = aggregated_dir / f"{today}.json"

        new_metrics = {
            "date": today,
            "duration_seconds": duration_seconds or 0,
            "total_tool_calls": total_tools,
            "total_prompts": total_prompts,
            "tool_breakdown": dict(tool_counts),
            "agents_spawned": dict(agent_spawned),
            "agents_spawned_count": agents_spawned_count,
            "agents_completed_count": agents_completed_count,
            "prompt_types": dict(prompt_types),
            "orchestrator_contexts": orchestrator_contexts,
            "cost": {
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost_usd": 0.0
            }
        }

        merged_metrics = merge_aggregated_metrics(aggregated_path, new_metrics)
        atomic_write(aggregated_path, merged_metrics)

        # Update agent metrics aggregation
        update_agent_metrics(aggregated_dir, new_metrics)

        # Update tool metrics aggregation
        update_tool_metrics(aggregated_dir, new_metrics, agent_depth)

        # Print summary to stderr (visible in verbose mode)
        print(f"Session complete: {total_tools} tool calls, {total_prompts} prompts", file=sys.stderr)
        if duration_seconds:
            print(f"Duration: {duration_seconds}s", file=sys.stderr)
        if agent_spawned:
            agents_str = ", ".join(f"{k}:{v}" for k, v in agent_spawned.items())
            print(f"Agents spawned: {agents_str}", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        print(f"Logging finalize warning: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    finalize_logging()
