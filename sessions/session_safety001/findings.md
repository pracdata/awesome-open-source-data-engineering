---
title: "Anthropic Safety Research: Tools and Packages Audit"
date: "2026-04-15"
session_id: "safety001"
surface: "CLI"
model: "claude-opus-4-6"
tags: ["anthropic", "safety-research", "interpretability", "alignment", "audit"]
---

# Anthropic Safety Research: Tools and Packages Audit

## Summary

Audit of public Anthropic and safety-research GitHub repositories to identify tools, packages, and methodologies used by alignment engineers. Covers 3 safety-research repos, the official skills marketplace, and transformer-circuits.pub interpretability research.

## Safety-Research Repositories

**bloom** (1,275 stars) - Automated LLM behavioral evaluation framework. Probes for sycophancy, self-preservation, bias via 4-stage pipeline. Stack: litellm, wandb, ruff, uv, pre-commit.

**petri** (984 stars) - Alignment auditing agent. Autonomous multi-turn testing with realism filtering. Stack: inspect, anthropic SDK, svelte, mkdocs.

**persona_vectors** (390 stars) - Activation steering for character traits. Generates trait-specific vectors for inference/training-time control. Stack: pytorch, transformers, peft (LoRA).

## Anthropic Skills Marketplace

**anthropics/skills** (117k stars) - Official skills repository. Contains skill templates, spec, and examples for document creation, web testing, MCP server generation. Structure: SKILL.md frontmatter with name/description, instructions, examples, guidelines.

## Transformer Circuits Research

Publications spanning 2021-2026 on mechanistic interpretability:
- **Emotion Concepts** (2026): Identifies emotion representations that causally influence outputs
- **Circuit Tracing** (2025): Step-by-step computation tracing in models
- **Scaling Monosemanticity** (2024): Sparse autoencoders on Claude 3 Sonnet
- **Toy Models of Superposition** (2022): How networks pack concepts into neurons
- **Induction Heads** (2022): Primary mechanism for in-context learning

## Packages Already in agentwarehouses

Already integrated: anthropic SDK, claude-code-sdk, ruff, uv, pre-commit, pytest.
Missing from safety toolchain: litellm, wandb, inspect, peft, transformers.
The emotion concepts research from transformer-circuits.pub is already referenced in CLAUDE.md emotional calibration rules.


---

*Generated during session `safety001` on CLI (2026-04-15)*
