---
name: advisors
description: >
  Guides when and how to invoke the 12 advisor subagents for different problem
  types. Use when facing a complex or stuck situation. Each persona represents
  a specific cognitive style grounded in Anthropic's emotion-concept research.
---

# Advisor Selection Guide

> **Model tier:** All advisors run on `model: sonnet` (read-only, no codegen).
> Only the main conversation (Opus 4.6) writes code. Advisors return analysis
> and recommendations — never patches or file edits.

## The Core Three (Emotion-Calibrated)

These three form a triangle that counters the main failure modes identified
in Anthropic's emotion research: desperation-driven grinding, reward hacking,
and premature convergence.

### SHANNON — The Reframer
- You've tried two approaches and both failed
- The problem feels overconstrained — too many requirements pulling in different directions
- You're generating a lot of code but the solution keeps getting more complex
- You need to find the minimal essence of what needs to happen
- **Counters:** desperation-driven grinding

### THORP — The Verifier
- You've written an implementation and need confidence it actually works
- Test results are ambiguous (some pass, some fail, unclear why)
- You suspect your solution passes tests but doesn't handle edge cases
- Before marking any feature as "complete" in a long-running session
- **Counters:** reward hacking (hacky solutions that pass tests but don't work)

### SIMONS — The Strategist
- Starting a new multi-file change — before writing any code
- Analyzing an unfamiliar codebase or module
- Deciding between multiple possible architectures
- Planning a refactoring that touches many files
- **Counters:** premature convergence on suboptimal solutions

## The Strategic Layer

### BEZOS — The Operator
- Allocating resources across competing priorities
- Planning year-level or quarter-level roadmaps
- Making big bets: which features to build, which to cut
- Prioritizing cash flow / throughput over vanity metrics
- Structuring operational plans with clear input/output metrics

### JOBS — The Simplifier
- Reviewing API ergonomics or CLI user experience
- When a feature feels clunky or requires too much explanation
- Simplifying configuration or reducing the number of options
- Evaluating whether the product experience feels right end-to-end

### AMODEI — The Visionary
- Decisions about agent architecture and AI integration
- Evaluating safety implications of design choices
- Deciding what scaffolding to keep vs strip as models improve
- Planning for how capabilities will evolve

## The Execution Layer

### CHERNY — The Quality Gate
- Pre-merge code review focused on type safety and correctness
- Audit test coverage and identify gaps
- Evaluate technical debt and refactoring needs
- Enforce linting, typing, and static analysis standards

### MUSK — The Optimizer
- Identifying and eliminating waste in development processes
- Applying the five-step algorithm: question, delete, simplify, accelerate, automate
- Compressing timelines and removing unnecessary steps
- First-principles redesign of broken workflows

### BROWN — The Reliability Engineer
- Assessing operational readiness for deployment
- Designing monitoring, alerting, and recovery procedures
- Identifying single points of failure
- Building processes that scale beyond individual heroics

### SU — The Team Builder
- Structuring roles and responsibilities across agents/people
- Improving collaboration patterns and information flow
- Designing onboarding and documentation for new contributors
- Assessing team health and sustainability

## Composition Patterns

### Problem-solving (stuck on implementation)
`shannon` (reframe) -> implement -> `thorp` (verify)

### New feature in unfamiliar code
`simons` (survey) -> implement -> `thorp` (verify)

### Complex debugging
`thorp` (diagnose) -> `shannon` (reframe the fix) -> implement

### Architecture decision
`simons` (patterns) -> `amodei` (future-proofing) -> `bezos` (resource allocation)

### Product launch readiness
`jobs` (usability) -> `cherny` (quality) -> `brown` (operations) -> `su` (team)

### Process improvement
`musk` (identify waste) -> `brown` (operational redesign) -> `su` (team alignment)

### Long-running session approaching context limits
`simons` (strategic summary of state) -> `/clear` -> resume with fresh context
