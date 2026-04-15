---
url: "https://github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent"
title: "research-agent - Multi-Agent Research System Demo"
fetched_at: "2026-04-15T18:52:25.300997+00:00"
session_id: "safety001"
---

# research-agent - Multi-Agent Research System Demo

Source: https://github.com/anthropics/claude-agent-sdk-demos/tree/main/research-agent

Lead agent spawns researcher, data analyst, report writer subagents. Uses pre/post_tool_use hooks for tracking. parent_tool_use_id links tool calls. Generates structured logs + transcripts. Output: markdown notes, charts, PDF reports.
