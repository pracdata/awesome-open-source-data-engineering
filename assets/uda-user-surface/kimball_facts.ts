/**
 * UDA + Kimball Dimensional Model — Zod Schemas
 * Claude Code User Surface: Fact Tables
 *
 * Fact tables at three grains:
 *   1. FactSession  — one Claude Code session (coarsest)
 *   2. FactToolUse  — one tool invocation within a session
 *   3. FactMessage  — one message in the conversation (finest)
 *
 * Each fact references dimension keys via string FK fields.
 * For Claude Agent SDK structured output, use the combined
 * StarSchema at the bottom which bundles dimensions inline.
 */

import { z } from "zod";

const UDA_NS = "https://rdf.agentwarehouses.dev/onto/claude-code-surface#";

function udaUri<T extends z.ZodTypeAny>(schema: T, concept: string): T {
  return schema.describe(`@udaUri: ${UDA_NS}${concept}`) as T;
}

// =============================================================================
// FACT: Session (grain = one Claude Code session)
// =============================================================================

export const FactSession = z.object({
  session_key: udaUri(z.string().uuid(), "session_key"),

  // Dimension foreign keys (surrogate UUIDs)
  fk_user:       udaUri(z.string().uuid(), "fk_user"),
  fk_device:     udaUri(z.string().uuid(), "fk_device"),
  fk_surface:    udaUri(z.string().uuid(), "fk_surface"),
  fk_model:      udaUri(z.string().uuid(), "fk_model"),
  fk_time_start: udaUri(z.string(), "fk_time_start"),
  fk_time_end:   udaUri(z.string().nullable(), "fk_time_end"),

  // Degenerate dimensions (low-cardinality attributes stored on the fact)
  session_id:    udaUri(z.string().min(1), "session_id"),
  git_branch:    udaUri(z.string().nullable(), "git_branch"),
  cwd:           udaUri(z.string().nullable(), "cwd"),
  thinking_mode: udaUri(z.enum(["adaptive", "enabled", "disabled"]).nullable(), "thinking_mode"),
  effort_level:  udaUri(z.enum(["low", "medium", "high", "max"]).nullable(), "effort_level"),

  // Measures — additive facts that can be summed across dimensions
  duration_ms:        udaUri(z.number().int().nonnegative(), "duration_ms"),
  num_turns:          udaUri(z.number().int().nonnegative(), "num_turns"),
  input_tokens:       udaUri(z.number().int().nonnegative(), "input_tokens"),
  output_tokens:      udaUri(z.number().int().nonnegative(), "output_tokens"),
  thinking_tokens:    udaUri(z.number().int().nonnegative().nullable(), "thinking_tokens"),
  cache_read_tokens:  udaUri(z.number().int().nonnegative().nullable(), "cache_read_tokens"),
  cache_write_tokens: udaUri(z.number().int().nonnegative().nullable(), "cache_write_tokens"),
  total_cost_usd:     udaUri(z.number().nonnegative(), "total_cost_usd"),
  num_tool_uses:      udaUri(z.number().int().nonnegative(), "num_tool_uses"),
  num_errors:         udaUri(z.number().int().nonnegative(), "num_errors"),
  num_checkpoints:    udaUri(z.number().int().nonnegative().nullable(), "num_checkpoints"),
  files_edited:       udaUri(z.number().int().nonnegative().nullable(), "files_edited"),
  files_created:      udaUri(z.number().int().nonnegative().nullable(), "files_created"),
  stop_reason:        udaUri(z.string().nullable(), "stop_reason"),
}).describe(`@udaUri: ${UDA_NS}FactSession — grain: one session`);
export type FactSession = z.infer<typeof FactSession>;

// =============================================================================
// FACT: Tool Use (grain = one tool invocation)
// =============================================================================

export const FactToolUse = z.object({
  tool_use_key: udaUri(z.string().uuid(), "tool_use_key"),

  // FK references
  fk_session:      udaUri(z.string().uuid(), "fk_session"),
  fk_tool:         udaUri(z.string().uuid(), "fk_tool"),
  fk_time_invoked: udaUri(z.string(), "fk_time_invoked"),

  // Degenerate dimensions
  tool_use_id:        udaUri(z.string().min(1), "tool_use_id"),
  parent_tool_use_id: udaUri(z.string().nullable(), "parent_tool_use_id"),
  turn_number:        udaUri(z.number().int().nonnegative(), "turn_number"),

  // Measures
  tool_duration_ms:    udaUri(z.number().int().nonnegative(), "tool_duration_ms"),
  is_error:            udaUri(z.boolean(), "is_error"),
  input_size_bytes:    udaUri(z.number().int().nonnegative().nullable(), "input_size_bytes"),
  output_size_bytes:   udaUri(z.number().int().nonnegative().nullable(), "output_size_bytes"),
  permission_decision: udaUri(z.enum(["allow", "deny", "ask", "defer"]).nullable(), "permission_decision"),
}).describe(`@udaUri: ${UDA_NS}FactToolUse — grain: one tool invocation`);
export type FactToolUse = z.infer<typeof FactToolUse>;

// =============================================================================
// FACT: Message (grain = one conversation message)
// =============================================================================

export const FactMessage = z.object({
  message_key: udaUri(z.string().uuid(), "message_key"),

  // FK references
  fk_session_msg: udaUri(z.string().uuid(), "fk_session_msg"),
  fk_time_sent:   udaUri(z.string(), "fk_time_sent"),

  // Degenerate dimensions
  message_uuid: udaUri(z.string().uuid(), "message_uuid"),
  message_role: udaUri(z.enum(["user", "assistant", "system", "result"]), "message_role"),

  // Measures
  content_blocks: udaUri(z.number().int().nonnegative(), "content_blocks"),
  text_length:    udaUri(z.number().int().nonnegative().nullable(), "text_length"),
  has_thinking:   udaUri(z.boolean(), "has_thinking"),
  has_tool_use:   udaUri(z.boolean(), "has_tool_use"),
}).describe(`@udaUri: ${UDA_NS}FactMessage — grain: one message`);
export type FactMessage = z.infer<typeof FactMessage>;

// =============================================================================
// KNOWLEDGE GRAPH: Entity & Relation schemas
// (Anthropic cookbook pattern for graph extraction via structured output)
// =============================================================================

export const EntityType = z.enum([
  "USER", "DEVICE", "SURFACE", "SESSION", "MODEL", "TOOL", "MCP_SERVER",
  "ORGANIZATION", "REPOSITORY", "BRANCH",
]);

export const Entity = z.object({
  name:        z.string().min(1),
  type:        EntityType,
  description: z.string(),
});

export const Relation = z.object({
  source:    z.string().min(1),
  predicate: z.string().min(1),
  target:    z.string().min(1),
});

export const ExtractedGraph = z.object({
  entities:  z.array(Entity),
  relations: z.array(Relation),
}).describe("Knowledge graph extracted from session telemetry");

// =============================================================================
// STAR SCHEMA: Denormalized session snapshot for SDK structured output
// =============================================================================
// Use this with Claude Agent SDK's output_format to extract a complete
// dimensional snapshot from a session, suitable for warehouse loading.

import {
  DimUser, DimDevice, DimUserSurface, DimModel, DimTime,
} from "./kimball_dimensions.js";

export const SessionStarSchema = z.object({
  // Inline dimensions (denormalized for single-call extraction)
  user:    DimUser,
  device:  DimDevice,
  surface: DimUserSurface,
  model:   DimModel,
  time:    DimTime,

  // The session fact
  session: FactSession,

  // Child facts
  tool_uses: z.array(FactToolUse),
  messages:  z.array(FactMessage),

  // Optional knowledge graph overlay
  graph: ExtractedGraph.optional(),
}).describe(
  "Complete Kimball star schema snapshot of a Claude Code session. " +
  "Dimensions are denormalized inline for single-pass extraction."
);
export type SessionStarSchema = z.infer<typeof SessionStarSchema>;
