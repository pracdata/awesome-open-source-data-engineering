"""Video pipeline data models — generation, distribution, and social platform types.

Aligned with schema/video_pipeline.graphql. Covers Claude Opus 4.6 prompt
generation, Veo 3.1 video generation, and multi-platform social distribution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from agentwarehouses.models.base import BaseModel

# ── Enums ────────────────────────────────────────────────────────


class VideoStatus(str, Enum):
    """Lifecycle status of a video asset or generation task."""

    PENDING = "pending"
    GENERATING = "generating"
    READY = "ready"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    FAILED = "failed"


class Platform(str, Enum):
    """Social media platforms for video distribution."""

    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"
    INSTAGRAM_REELS = "instagram_reels"


class VideoResolution(str, Enum):
    """Supported video output resolutions."""

    SD_480P = "480p"
    HD_720P = "720p"
    HD_1080P = "1080p"
    UHD_4K = "4k"


class GenerationModel(str, Enum):
    """Veo 3.1 model variants for video generation."""

    VEO_3_1_FAST = "veo-3.1-fast-generate-001"
    VEO_3_1_QUALITY = "veo-3.1-generate-001"


class PromptStyle(str, Enum):
    """Cinematic prompt styles for Claude-generated video descriptions."""

    CINEMATIC = "cinematic"
    DOCUMENTARY = "documentary"
    COMMERCIAL = "commercial"
    MUSIC_VIDEO = "music_video"
    VLOG = "vlog"


# ── Video Metadata & Assets ──────────────────────────────────────


class VideoMetadata(BaseModel):
    """Metadata attached to a generated video asset."""

    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    resolution: VideoResolution = VideoResolution.UHD_4K
    duration_seconds: float = Field(gt=0, le=60.0)
    has_audio: bool = True
    tags: list[str] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def limit_tags(cls, v: list[str]) -> list[str]:
        if len(v) > 30:
            msg = "Maximum 30 tags allowed"
            raise ValueError(msg)
        return v


class VideoAsset(BaseModel):
    """A generated video asset ready for distribution."""

    id: str
    url: str | None = None
    status: VideoStatus = VideoStatus.PENDING
    platforms: list[Platform] = Field(default_factory=list)
    metadata: VideoMetadata
    generation_task_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Generation ───────────────────────────────────────────────────


class GenerationConfig(BaseModel):
    """Configuration for a Veo 3.1 video generation request."""

    model: GenerationModel = GenerationModel.VEO_3_1_FAST
    resolution: VideoResolution = VideoResolution.UHD_4K
    duration_seconds: float = Field(default=10.0, gt=0, le=60.0)
    negative_prompt: str | None = None
    seed: int | None = None
    person_generation: str = "allow_adult"
    aspect_ratio: str = "9:16"


class GenerationTask(BaseModel):
    """A video generation task submitted to Veo 3.1."""

    id: str
    prompt: str = Field(min_length=1)
    config: GenerationConfig = Field(default_factory=GenerationConfig)
    status: VideoStatus = VideoStatus.PENDING
    video_asset: VideoAsset | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CinematicPromptRequest(BaseModel):
    """Input for Claude Opus 4.6 cinematic prompt generation."""

    topic: str = Field(min_length=1, max_length=500)
    style: PromptStyle = PromptStyle.CINEMATIC
    duration_seconds: float = Field(default=10.0, gt=0, le=60.0)
    include_audio_direction: bool = True


class CinematicPromptResponse(BaseModel):
    """Output from Claude Opus 4.6 cinematic prompt generation."""

    prompt: str
    negative_prompt: str | None = None
    style: PromptStyle
    model_used: str = "claude-opus-4-6"
    usage: dict[str, Any] = Field(default_factory=dict)


# ── Distribution ─────────────────────────────────────────────────


class PlatformCredentials(BaseModel):
    """OAuth credentials for a social media platform."""

    platform: Platform
    access_token: str = Field(min_length=1)
    refresh_token: str | None = None
    expires_at: datetime | None = None


class DistributionResult(BaseModel):
    """Result of publishing a video to a single platform."""

    platform: Platform
    success: bool
    platform_video_id: str | None = None
    platform_url: str | None = None
    error: str | None = None


class DistributionTask(BaseModel):
    """A multi-platform video distribution task."""

    id: str
    video_asset_id: str
    platforms: list[Platform] = Field(min_length=1)
    results: list[DistributionResult] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ── Social Platform Configs ──────────────────────────────────────


class TikTokUploadConfig(BaseModel):
    """TikTok Video Upload API configuration."""

    privacy_level: str = "PUBLIC_TO_EVERYONE"
    disable_duet: bool = False
    disable_stitch: bool = False
    disable_comment: bool = False
    brand_content_toggle: bool = False
    brand_organic_toggle: bool = False


class YouTubeUploadConfig(BaseModel):
    """YouTube Data API v3 upload configuration for Shorts."""

    category_id: str = "22"
    privacy_status: str = "public"
    made_for_kids: bool = False
    shorts: bool = True


class InstagramReelsConfig(BaseModel):
    """Meta Graph API Reels endpoint configuration."""

    share_to_feed: bool = True
    caption_max_length: int = Field(default=2200, ge=0)
    location_id: str | None = None
    collaborators: list[str] = Field(default_factory=list)
