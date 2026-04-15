# Scratchpad — anthropic-safety-research-audit

Session: `safety001`
Created: 2026-04-15T17:51:42.032458+00:00

---

### [2026-04-15 17:51:42 UTC] Initial repo scan

Identified 3 key safety-research repos: bloom (LLM eval framework), petri (alignment auditing agent), persona_vectors (activation steering). Also found anthropics/skills (117k stars, official skills marketplace).

### [2026-04-15 17:51:42 UTC] Dependency analysis

Key packages used by safety engineers:
- bloom: litellm, wandb, ruff, uv, pre-commit, ty (type checker)
- petri: inspect (eval framework), anthropic SDK, mkdocs, pytest, svelte
- persona_vectors: pytorch, transformers, openai, peft (LoRA)
- anthropics/skills: python scripts, shell, document tools (docx/pdf/xlsx)

### [2026-04-15 17:51:42 UTC] transformer-circuits.pub catalog

transformer-circuits.pub publishes interpretability research:
- 2026: Emotion Concepts paper (basis for our CLAUDE.md calibration rules)
- 2025: Introspective Awareness, Biology of LLM, Circuit Tracing
- 2024: Scaling Monosemanticity (sparse autoencoders on Claude 3 Sonnet)
- 2023: Towards Monosemanticity, Superposition + Double Descent
- 2022: Toy Models of Superposition, Induction Heads
- 2021: Mathematical Framework for Transformer Circuits

### [2026-04-15 18:52:25 UTC] ConventionalSessions Research

Researched: conventional commits spec, parser, circuit-tracer, research-agent demo, Agent SDK Python + TS v2 preview. Evaluating conventionalsessions / conventionaltraces concept.

### [2026-04-15 19:03:26 UTC] Context Compacted

Session context was compacted. Prior work is summarized above.
