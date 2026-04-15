/**
 * Video Pipeline Types — Zod schemas aligned with schema/video_pipeline.graphql
 *
 * Shared type definitions for the social distribution layer.
 * These mirror the Python Pydantic models in models/video.py.
 */

import { z } from "zod";

// ── Enums ────────────────────────────────────────────────────────

export const VideoStatus = z.enum([
  "pending",
  "generating",
  "ready",
  "uploading",
  "published",
  "failed",
]);
export type VideoStatus = z.infer<typeof VideoStatus>;

export const Platform = z.enum([
  "tiktok",
  "youtube_shorts",
  "instagram_reels",
]);
export type Platform = z.infer<typeof Platform>;

export const VideoResolution = z.enum(["480p", "720p", "1080p", "4k"]);
export type VideoResolution = z.infer<typeof VideoResolution>;

export const GenerationModel = z.enum([
  "veo-3.1-fast-generate-001",
  "veo-3.1-generate-001",
]);
export type GenerationModel = z.infer<typeof GenerationModel>;

export const PromptStyle = z.enum([
  "cinematic",
  "documentary",
  "commercial",
  "music_video",
  "vlog",
]);
export type PromptStyle = z.infer<typeof PromptStyle>;

// ── Object Types ─────────────────────────────────────────────────

export const VideoMetadata = z.object({
  title: z.string().min(1).max(200),
  description: z.string().nullable().optional(),
  resolution: VideoResolution,
  durationSeconds: z.number().positive().max(60),
  hasAudio: z.boolean(),
  tags: z.array(z.string()).max(30).default([]),
});
export type VideoMetadata = z.infer<typeof VideoMetadata>;

export const VideoAsset = z.object({
  id: z.string(),
  url: z.string().nullable().optional(),
  status: VideoStatus,
  platforms: z.array(Platform),
  metadata: VideoMetadata,
  generationTaskId: z.string().nullable().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});
export type VideoAsset = z.infer<typeof VideoAsset>;

export const GenerationTask = z.object({
  id: z.string(),
  prompt: z.string().min(1),
  model: GenerationModel,
  resolution: VideoResolution,
  durationSeconds: z.number().positive(),
  status: VideoStatus,
  videoAsset: VideoAsset.nullable().optional(),
  error: z.string().nullable().optional(),
  createdAt: z.string().datetime(),
});
export type GenerationTask = z.infer<typeof GenerationTask>;

export const DistributionResult = z.object({
  platform: Platform,
  success: z.boolean(),
  platformVideoId: z.string().nullable().optional(),
  platformUrl: z.string().nullable().optional(),
  error: z.string().nullable().optional(),
});
export type DistributionResult = z.infer<typeof DistributionResult>;

export const DistributionTask = z.object({
  id: z.string(),
  videoAssetId: z.string(),
  platforms: z.array(Platform).min(1),
  results: z.array(DistributionResult).default([]),
  createdAt: z.string().datetime(),
});
export type DistributionTask = z.infer<typeof DistributionTask>;

// ── Input Types ──────────────────────────────────────────────────

export const GenerateVideoInput = z.object({
  prompt: z.string().min(1),
  title: z.string().min(1).max(200),
  platforms: z.array(Platform).min(1),
  negativePrompt: z.string().nullable().optional(),
  model: GenerationModel.default("veo-3.1-fast-generate-001"),
  resolution: VideoResolution.default("4k"),
  durationSeconds: z.number().positive().default(10),
  style: PromptStyle.default("cinematic"),
  description: z.string().nullable().optional(),
  tags: z.array(z.string()).max(30).default([]),
});
export type GenerateVideoInput = z.infer<typeof GenerateVideoInput>;

export const DistributeVideoInput = z.object({
  videoAssetId: z.string(),
  platforms: z.array(Platform).min(1),
});
export type DistributeVideoInput = z.infer<typeof DistributeVideoInput>;

export const CinematicPromptInput = z.object({
  topic: z.string().min(1).max(500),
  style: PromptStyle.default("cinematic"),
  durationSeconds: z.number().positive().default(10),
  includeAudioDirection: z.boolean().default(true),
});
export type CinematicPromptInput = z.infer<typeof CinematicPromptInput>;

// ── Platform-specific configs ────────────────────────────────────

export const TikTokUploadConfig = z.object({
  privacyLevel: z
    .enum([
      "PUBLIC_TO_EVERYONE",
      "MUTUAL_FOLLOW_FRIENDS",
      "FOLLOWER_OF_CREATOR",
      "SELF_ONLY",
    ])
    .default("PUBLIC_TO_EVERYONE"),
  disableDuet: z.boolean().default(false),
  disableStitch: z.boolean().default(false),
  disableComment: z.boolean().default(false),
  brandContentToggle: z.boolean().default(false),
  brandOrganicToggle: z.boolean().default(false),
});
export type TikTokUploadConfig = z.infer<typeof TikTokUploadConfig>;

export const YouTubeUploadConfig = z.object({
  categoryId: z.string().default("22"),
  privacyStatus: z.enum(["public", "unlisted", "private"]).default("public"),
  madeForKids: z.boolean().default(false),
  shorts: z.boolean().default(true),
});
export type YouTubeUploadConfig = z.infer<typeof YouTubeUploadConfig>;

export const InstagramReelsConfig = z.object({
  shareToFeed: z.boolean().default(true),
  captionMaxLength: z.number().nonnegative().default(2200),
  locationId: z.string().nullable().optional(),
  collaborators: z.array(z.string()).default([]),
});
export type InstagramReelsConfig = z.infer<typeof InstagramReelsConfig>;

// ── Platform Credentials ─────────────────────────────────────────

export const PlatformCredentials = z.object({
  platform: Platform,
  accessToken: z.string().min(1),
  refreshToken: z.string().nullable().optional(),
  expiresAt: z.string().datetime().nullable().optional(),
});
export type PlatformCredentials = z.infer<typeof PlatformCredentials>;
