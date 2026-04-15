/**
 * UDA + Kimball Dimensional Model — Zod Schemas
 * Claude Code User Surface: Dimensions
 *
 * These schemas are designed for use with the Claude Agent SDK's
 * structured output feature (output_format). Each schema carries
 * UDA-style semantic metadata via .describe() annotations that
 * map to the RDF ontology URIs in domain_model.ttl.
 *
 * Ralph Kimball patterns applied:
 *   - Conformed dimensions shared across fact tables
 *   - Type 2 SCD on DimUser (effective_from/to, is_current)
 *   - Surrogate keys (UUID v7) on every dimension
 *   - Enumerations as controlled vocabularies
 */

import { z } from "zod";

// =============================================================================
// UDA URI metadata helper
// =============================================================================

const UDA_NS = "https://rdf.agentwarehouses.dev/onto/claude-code-surface#";

/** Tag a schema with its UDA ontology URI for traceability */
function udaUri<T extends z.ZodTypeAny>(schema: T, concept: string): T {
  return schema.describe(`@udaUri: ${UDA_NS}${concept}`) as T;
}

// =============================================================================
// ENUMERATIONS (Controlled Vocabularies)
// =============================================================================

export const PlanTier = z.enum([
  "Free", "Pro", "Team", "Enterprise", "API",
]).describe(`@udaUri: ${UDA_NS}PlanTier`);
export type PlanTier = z.infer<typeof PlanTier>;

export const AuthMethod = z.enum([
  "OAuth", "APIKey", "OAuthToken",
]).describe(`@udaUri: ${UDA_NS}AuthMethod`);
export type AuthMethod = z.infer<typeof AuthMethod>;

export const PermissionMode = z.enum([
  "default", "acceptEdits", "plan", "dontAsk", "auto", "bypassPermissions",
]).describe(`@udaUri: ${UDA_NS}PermissionMode`);
export type PermissionMode = z.infer<typeof PermissionMode>;

export const OSName = z.enum([
  "Linux", "macOS", "Windows",
]).describe(`@udaUri: ${UDA_NS}OSName`);
export type OSName = z.infer<typeof OSName>;

export const SurfaceType = z.enum([
  "CLI", "VSCode", "JetBrains", "Desktop", "Web",
  "Mobile", "Slack", "GitHubAction", "GitLabCI", "SDK",
]).describe(`@udaUri: ${UDA_NS}SurfaceType`);
export type SurfaceType = z.infer<typeof SurfaceType>;

export const ModelTier = z.enum([
  "Opus", "Sonnet", "Haiku",
]).describe(`@udaUri: ${UDA_NS}ModelTier`);
export type ModelTier = z.infer<typeof ModelTier>;

export const ToolCategory = z.enum([
  "file_operations", "code_execution", "code_search", "file_search",
  "web_operations", "subagent_spawning", "task_management",
  "mcp_integration", "git_operations", "user_interaction", "workflow",
]).describe(`@udaUri: ${UDA_NS}ToolCategory`);
export type ToolCategory = z.infer<typeof ToolCategory>;

// =============================================================================
// DIMENSION: User (Type 2 SCD)
// =============================================================================

export const DimUser = z.object({
  user_key:        udaUri(z.string().uuid(), "user_key"),
  user_id:         udaUri(z.string().min(1), "user_id"),
  org_id:          udaUri(z.string().nullable(), "org_id"),
  plan_tier:       udaUri(PlanTier, "plan_tier"),
  auth_method:     udaUri(AuthMethod, "auth_method"),
  permission_mode: udaUri(PermissionMode, "permission_mode"),
  zdr_enabled:     udaUri(z.boolean(), "zdr_enabled"),
  effective_from:  udaUri(z.string().datetime(), "effective_from"),
  effective_to:    udaUri(z.string().datetime().nullable(), "effective_to"),
  is_current:      udaUri(z.boolean(), "is_current"),
}).describe(`@udaUri: ${UDA_NS}DimUser — Kimball Type 2 SCD`);
export type DimUser = z.infer<typeof DimUser>;

// =============================================================================
// DIMENSION: Device
// =============================================================================

export const DimDevice = z.object({
  device_key:          udaUri(z.string().uuid(), "device_key"),
  device_fingerprint:  udaUri(z.string().min(1), "device_fingerprint"),
  os_name:             udaUri(OSName, "os_name"),
  os_version:          udaUri(z.string().nullable(), "os_version"),
  arch:                udaUri(z.string().min(1), "arch"),
  shell:               udaUri(z.string().nullable(), "shell"),
  terminal:            udaUri(z.string().nullable(), "terminal"),
  node_version:        udaUri(z.string().nullable(), "node_version"),
  claude_code_version: udaUri(z.string().regex(/^\d+\.\d+\.\d+/), "claude_code_version"),
}).describe(`@udaUri: ${UDA_NS}DimDevice`);
export type DimDevice = z.infer<typeof DimDevice>;

// =============================================================================
// DIMENSION: User Surface
// =============================================================================

export const DimUserSurface = z.object({
  surface_key:     udaUri(z.string().uuid(), "surface_key"),
  surface_type:    udaUri(SurfaceType, "surface_type"),
  surface_version: udaUri(z.string().nullable(), "surface_version"),
  ide_name:        udaUri(z.string().nullable(), "ide_name"),
  ide_version:     udaUri(z.string().nullable(), "ide_version"),
  is_remote:       udaUri(z.boolean(), "is_remote"),
  is_headless:     udaUri(z.boolean(), "is_headless"),
}).describe(`@udaUri: ${UDA_NS}DimUserSurface`);
export type DimUserSurface = z.infer<typeof DimUserSurface>;

// =============================================================================
// DIMENSION: Model
// =============================================================================

export const DimModel = z.object({
  model_key:          udaUri(z.string().uuid(), "model_key"),
  model_id:           udaUri(z.string().min(1), "model_id"),
  model_family:       udaUri(z.string().min(1), "model_family"),
  model_tier:         udaUri(ModelTier, "model_tier"),
  context_window:     udaUri(z.number().int().positive(), "context_window"),
  max_output_tokens:  udaUri(z.number().int().positive(), "max_output_tokens"),
  supports_thinking:  udaUri(z.boolean(), "supports_thinking"),
  supports_vision:    udaUri(z.boolean(), "supports_vision"),
}).describe(`@udaUri: ${UDA_NS}DimModel`);
export type DimModel = z.infer<typeof DimModel>;

// =============================================================================
// DIMENSION: Time (Conformed Date/Time at hourly grain)
// =============================================================================

export const DimTime = z.object({
  time_key:    udaUri(z.string(), "time_key"),
  iso_date:    udaUri(z.string().date(), "iso_date"),
  hour:        udaUri(z.number().int().min(0).max(23), "hour"),
  day_of_week: udaUri(z.number().int().min(1).max(7), "day_of_week"),
  month:       udaUri(z.number().int().min(1).max(12), "month"),
  quarter:     udaUri(z.number().int().min(1).max(4), "quarter"),
  year:        udaUri(z.number().int().min(2024), "year"),
  is_weekend:  udaUri(z.boolean(), "is_weekend"),
}).describe(`@udaUri: ${UDA_NS}DimTime`);
export type DimTime = z.infer<typeof DimTime>;

// =============================================================================
// DIMENSION: Tool
// =============================================================================

export const DimTool = z.object({
  tool_key:            udaUri(z.string().uuid(), "tool_key"),
  tool_name:           udaUri(z.string().min(1), "tool_name"),
  tool_category:       udaUri(ToolCategory, "tool_category"),
  requires_permission: udaUri(z.boolean(), "requires_permission"),
  is_mcp_tool:         udaUri(z.boolean(), "is_mcp_tool"),
  mcp_server_name:     udaUri(z.string().nullable(), "mcp_server_name"),
}).describe(`@udaUri: ${UDA_NS}DimTool`);
export type DimTool = z.infer<typeof DimTool>;
