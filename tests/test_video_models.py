"""Tests for video pipeline Pydantic models — enums, validation, serialization."""

import pytest
from pydantic import ValidationError

from agentwarehouses.models import (
    CinematicPromptRequest,
    CinematicPromptResponse,
    DistributionResult,
    DistributionTask,
    GenerationConfig,
    GenerationModel,
    GenerationTask,
    InstagramReelsConfig,
    Platform,
    PlatformCredentials,
    PromptStyle,
    TikTokUploadConfig,
    VideoAsset,
    VideoMetadata,
    VideoResolution,
    VideoStatus,
    YouTubeUploadConfig,
)


class TestVideoEnums:
    def test_video_status_values(self):
        assert VideoStatus.PENDING.value == "pending"
        assert VideoStatus.GENERATING.value == "generating"
        assert VideoStatus.READY.value == "ready"
        assert VideoStatus.PUBLISHED.value == "published"
        assert VideoStatus.FAILED.value == "failed"
        assert len(VideoStatus) == 6

    def test_platform_values(self):
        assert Platform.TIKTOK.value == "tiktok"
        assert Platform.YOUTUBE_SHORTS.value == "youtube_shorts"
        assert Platform.INSTAGRAM_REELS.value == "instagram_reels"
        assert len(Platform) == 3

    def test_resolution_values(self):
        assert VideoResolution.UHD_4K.value == "4k"
        assert VideoResolution.HD_1080P.value == "1080p"
        assert len(VideoResolution) == 4

    def test_generation_model_values(self):
        assert GenerationModel.VEO_3_1_FAST.value == "veo-3.1-fast-generate-001"
        assert GenerationModel.VEO_3_1_QUALITY.value == "veo-3.1-generate-001"

    def test_prompt_style_values(self):
        assert PromptStyle.CINEMATIC.value == "cinematic"
        assert PromptStyle.DOCUMENTARY.value == "documentary"
        assert len(PromptStyle) == 5


class TestVideoMetadata:
    def test_create_minimal(self):
        vm = VideoMetadata(title="Test Video", duration_seconds=10.0)
        assert vm.title == "Test Video"
        assert vm.resolution == VideoResolution.UHD_4K
        assert vm.has_audio is True
        assert vm.tags == []

    def test_create_full(self):
        vm = VideoMetadata(
            title="Cinematic Sunset",
            description="A beautiful sunset over the ocean",
            resolution=VideoResolution.HD_1080P,
            duration_seconds=30.0,
            has_audio=True,
            tags=["sunset", "ocean", "cinematic"],
        )
        assert vm.description == "A beautiful sunset over the ocean"
        assert len(vm.tags) == 3

    def test_rejects_empty_title(self):
        with pytest.raises(ValidationError):
            VideoMetadata(title="", duration_seconds=10.0)

    def test_rejects_zero_duration(self):
        with pytest.raises(ValidationError):
            VideoMetadata(title="Test", duration_seconds=0)

    def test_rejects_over_60s_duration(self):
        with pytest.raises(ValidationError):
            VideoMetadata(title="Test", duration_seconds=61.0)

    def test_rejects_too_many_tags(self):
        with pytest.raises(ValidationError):
            VideoMetadata(title="Test", duration_seconds=10.0, tags=["tag"] * 31)

    def test_serialization(self):
        vm = VideoMetadata(title="Test", duration_seconds=10.0)
        data = vm.model_dump()
        assert data["title"] == "Test"
        assert data["resolution"] == "4k"


class TestVideoAsset:
    def test_create_minimal(self):
        va = VideoAsset(
            id="asset-1",
            metadata=VideoMetadata(title="Test", duration_seconds=10.0),
        )
        assert va.id == "asset-1"
        assert va.status == VideoStatus.PENDING
        assert va.platforms == []
        assert va.url is None

    def test_create_with_platforms(self):
        va = VideoAsset(
            id="asset-2",
            url="https://storage.example.com/video.mp4",
            status=VideoStatus.READY,
            platforms=[Platform.TIKTOK, Platform.YOUTUBE_SHORTS],
            metadata=VideoMetadata(title="Multi-platform", duration_seconds=15.0),
        )
        assert len(va.platforms) == 2
        assert va.url == "https://storage.example.com/video.mp4"


class TestGenerationConfig:
    def test_defaults(self):
        gc = GenerationConfig()
        assert gc.model == GenerationModel.VEO_3_1_FAST
        assert gc.resolution == VideoResolution.UHD_4K
        assert gc.duration_seconds == 10.0
        assert gc.aspect_ratio == "9:16"
        assert gc.person_generation == "allow_adult"

    def test_custom(self):
        gc = GenerationConfig(
            model=GenerationModel.VEO_3_1_QUALITY,
            resolution=VideoResolution.HD_1080P,
            duration_seconds=30.0,
            negative_prompt="blurry, low quality",
        )
        assert gc.model == GenerationModel.VEO_3_1_QUALITY
        assert gc.negative_prompt == "blurry, low quality"


class TestGenerationTask:
    def test_create(self):
        gt = GenerationTask(id="task-1", prompt="A cinematic sunrise over mountains")
        assert gt.id == "task-1"
        assert gt.status == VideoStatus.PENDING
        assert gt.video_asset is None
        assert gt.error is None

    def test_rejects_empty_prompt(self):
        with pytest.raises(ValidationError):
            GenerationTask(id="task-1", prompt="")


class TestCinematicPrompt:
    def test_request_defaults(self):
        cr = CinematicPromptRequest(topic="A cat playing piano")
        assert cr.style == PromptStyle.CINEMATIC
        assert cr.duration_seconds == 10.0
        assert cr.include_audio_direction is True

    def test_request_custom(self):
        cr = CinematicPromptRequest(
            topic="Product launch for tech gadget",
            style=PromptStyle.COMMERCIAL,
            duration_seconds=30.0,
            include_audio_direction=False,
        )
        assert cr.style == PromptStyle.COMMERCIAL

    def test_response(self):
        resp = CinematicPromptResponse(
            prompt="A slow dolly shot reveals a grand piano...",
            style=PromptStyle.CINEMATIC,
            model_used="claude-opus-4-6",
            usage={"input_tokens": 150, "output_tokens": 300},
        )
        assert resp.model_used == "claude-opus-4-6"
        assert resp.usage["output_tokens"] == 300

    def test_response_with_negative(self):
        resp = CinematicPromptResponse(
            prompt="A macro shot of a dewdrop on a leaf...",
            negative_prompt="blurry, artifacts, text overlays",
            style=PromptStyle.DOCUMENTARY,
        )
        assert resp.negative_prompt is not None


class TestDistribution:
    def test_result_success(self):
        dr = DistributionResult(
            platform=Platform.TIKTOK,
            success=True,
            platform_video_id="7123456789",
            platform_url="https://www.tiktok.com/@user/video/7123456789",
        )
        assert dr.success is True
        assert dr.error is None

    def test_result_failure(self):
        dr = DistributionResult(
            platform=Platform.YOUTUBE_SHORTS,
            success=False,
            error="Upload quota exceeded",
        )
        assert dr.success is False
        assert dr.platform_video_id is None

    def test_task(self):
        dt = DistributionTask(
            id="dist-1",
            video_asset_id="asset-1",
            platforms=[Platform.TIKTOK, Platform.INSTAGRAM_REELS],
        )
        assert len(dt.platforms) == 2
        assert dt.results == []

    def test_task_rejects_no_platforms(self):
        with pytest.raises(ValidationError):
            DistributionTask(id="dist-1", video_asset_id="asset-1", platforms=[])


class TestPlatformCredentials:
    def test_create(self):
        pc = PlatformCredentials(
            platform=Platform.TIKTOK,
            access_token="tk_abc123",
        )
        assert pc.platform == Platform.TIKTOK
        assert pc.refresh_token is None

    def test_rejects_empty_token(self):
        with pytest.raises(ValidationError):
            PlatformCredentials(platform=Platform.TIKTOK, access_token="")


class TestPlatformConfigs:
    def test_tiktok_defaults(self):
        tc = TikTokUploadConfig()
        assert tc.privacy_level == "PUBLIC_TO_EVERYONE"
        assert tc.disable_duet is False

    def test_youtube_defaults(self):
        yc = YouTubeUploadConfig()
        assert yc.category_id == "22"
        assert yc.shorts is True
        assert yc.privacy_status == "public"

    def test_instagram_defaults(self):
        ic = InstagramReelsConfig()
        assert ic.share_to_feed is True
        assert ic.caption_max_length == 2200
        assert ic.collaborators == []

    def test_tiktok_serialization(self):
        tc = TikTokUploadConfig()
        data = tc.model_dump()
        assert data["privacy_level"] == "PUBLIC_TO_EVERYONE"

    def test_youtube_serialization(self):
        yc = YouTubeUploadConfig(privacy_status="unlisted")
        data = yc.model_dump()
        assert data["privacy_status"] == "unlisted"
