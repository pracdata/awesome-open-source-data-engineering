"""Strawberry GraphQL server exposing the video generation pipeline.

Run with: strawberry server agentwarehouses.generation.graphql_server:schema
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import strawberry

from agentwarehouses.models.video import (
    CinematicPromptRequest,
    VideoStatus,
)
from agentwarehouses.models.video import (
    DistributionTask as PydanticDistTask,
)
from agentwarehouses.models.video import (
    GenerationModel as GenModelEnum,
)
from agentwarehouses.models.video import (
    GenerationTask as PydanticGenTask,
)
from agentwarehouses.models.video import (
    Platform as PlatformEnum,
)
from agentwarehouses.models.video import (
    PromptStyle as PromptStyleEnum,
)
from agentwarehouses.models.video import (
    VideoAsset as PydanticVideoAsset,
)
from agentwarehouses.models.video import (
    VideoResolution as ResolutionEnum,
)

# ── Strawberry Object Types ──────────────────────────────────────


@strawberry.type
class VideoMetadata:
    title: str
    description: str | None
    resolution: str
    duration_seconds: float
    has_audio: bool
    tags: list[str]


@strawberry.type
class VideoAssetType:
    id: strawberry.ID
    url: str | None
    status: str
    platforms: list[str]
    metadata: VideoMetadata
    generation_task_id: str | None
    created_at: str
    updated_at: str


@strawberry.type
class GenerationTaskType:
    id: strawberry.ID
    prompt: str
    model: str
    resolution: str
    duration_seconds: float
    status: str
    video_asset: VideoAssetType | None
    error: str | None
    created_at: str


@strawberry.type
class DistributionResultType:
    platform: str
    success: bool
    platform_video_id: str | None
    platform_url: str | None
    error: str | None


@strawberry.type
class DistributionTaskType:
    id: strawberry.ID
    video_asset_id: strawberry.ID
    platforms: list[str]
    results: list[DistributionResultType]
    created_at: str


# ── Input Types ──────────────────────────────────────────────────


@strawberry.input
class GenerateVideoInput:
    prompt: str
    title: str
    platforms: list[str]
    negative_prompt: str | None = None
    model: str = "veo-3.1-fast-generate-001"
    resolution: str = "4k"
    duration_seconds: float = 10.0
    style: str = "cinematic"
    description: str | None = None
    tags: list[str] = strawberry.field(default_factory=list)


@strawberry.input
class DistributeVideoInput:
    video_asset_id: strawberry.ID
    platforms: list[str]


@strawberry.input
class CinematicPromptInput:
    topic: str
    style: str = "cinematic"
    duration_seconds: float = 10.0
    include_audio_direction: bool = True


# ── In-memory store (replace with DB in production) ──────────────

_generation_tasks: dict[str, PydanticGenTask] = {}
_video_assets: dict[str, PydanticVideoAsset] = {}
_distribution_tasks: dict[str, PydanticDistTask] = {}


def _pydantic_to_gql_video_asset(asset: PydanticVideoAsset) -> VideoAssetType:
    return VideoAssetType(
        id=strawberry.ID(asset.id),
        url=asset.url,
        status=asset.status.value,
        platforms=[p.value for p in asset.platforms],
        metadata=VideoMetadata(
            title=asset.metadata.title,
            description=asset.metadata.description,
            resolution=asset.metadata.resolution.value,
            duration_seconds=asset.metadata.duration_seconds,
            has_audio=asset.metadata.has_audio,
            tags=asset.metadata.tags,
        ),
        generation_task_id=asset.generation_task_id,
        created_at=asset.created_at.isoformat(),
        updated_at=asset.updated_at.isoformat(),
    )


def _pydantic_to_gql_gen_task(task: PydanticGenTask) -> GenerationTaskType:
    return GenerationTaskType(
        id=strawberry.ID(task.id),
        prompt=task.prompt,
        model=task.config.model.value,
        resolution=task.config.resolution.value,
        duration_seconds=task.config.duration_seconds,
        status=task.status.value,
        video_asset=_pydantic_to_gql_video_asset(task.video_asset) if task.video_asset else None,
        error=task.error,
        created_at=task.created_at.isoformat(),
    )


# ── Query ────────────────────────────────────────────────────────


@strawberry.type
class Query:
    @strawberry.field
    def generation_task(self, id: strawberry.ID) -> GenerationTaskType | None:
        task = _generation_tasks.get(str(id))
        return _pydantic_to_gql_gen_task(task) if task else None

    @strawberry.field
    def list_generation_tasks(self, status: str | None = None, limit: int = 20) -> list[GenerationTaskType]:
        tasks = list(_generation_tasks.values())
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        return [_pydantic_to_gql_gen_task(t) for t in tasks[:limit]]

    @strawberry.field
    def video_asset(self, id: strawberry.ID) -> VideoAssetType | None:
        asset = _video_assets.get(str(id))
        return _pydantic_to_gql_video_asset(asset) if asset else None

    @strawberry.field
    def list_video_assets(self, platform: str | None = None, limit: int = 20) -> list[VideoAssetType]:
        assets = list(_video_assets.values())
        if platform:
            assets = [a for a in assets if any(p.value == platform for p in a.platforms)]
        return [_pydantic_to_gql_video_asset(a) for a in assets[:limit]]

    @strawberry.field
    def distribution_task(self, id: strawberry.ID) -> DistributionTaskType | None:
        task = _distribution_tasks.get(str(id))
        if not task:
            return None
        return DistributionTaskType(
            id=strawberry.ID(task.id),
            video_asset_id=strawberry.ID(task.video_asset_id),
            platforms=[p.value for p in task.platforms],
            results=[
                DistributionResultType(
                    platform=r.platform.value,
                    success=r.success,
                    platform_video_id=r.platform_video_id,
                    platform_url=r.platform_url,
                    error=r.error,
                )
                for r in task.results
            ],
            created_at=task.created_at.isoformat(),
        )


# ── Mutation ─────────────────────────────────────────────────────


@strawberry.type
class Mutation:
    @strawberry.mutation
    def generate_video(self, input: GenerateVideoInput) -> GenerationTaskType:
        """Submit a video generation task. Enqueues Veo 3.1 generation."""
        from agentwarehouses.generation.veo_client import VeoClient
        from agentwarehouses.models.video import GenerationConfig

        config = GenerationConfig(
            model=GenModelEnum(input.model),
            resolution=ResolutionEnum(input.resolution),
            duration_seconds=input.duration_seconds,
            negative_prompt=input.negative_prompt,
        )

        try:
            client = VeoClient()
            _operation, task = client.submit_generation(
                prompt=input.prompt,
                config=config,
                title=input.title,
                tags=input.tags,
            )
        except Exception as exc:
            raise ValueError(f"Video generation failed: {exc}") from exc

        if task.video_asset:
            task.video_asset.platforms = [PlatformEnum(p) for p in input.platforms]
            _video_assets[task.video_asset.id] = task.video_asset

        _generation_tasks[task.id] = task
        return _pydantic_to_gql_gen_task(task)

    @strawberry.mutation
    def generate_cinematic_prompt(self, input: CinematicPromptInput) -> str:
        """Generate a cinematic prompt using Claude Opus 4.6."""
        from agentwarehouses.generation.claude_prompts import CinematicPromptGenerator

        try:
            generator = CinematicPromptGenerator()
            request = CinematicPromptRequest(
                topic=input.topic,
                style=PromptStyleEnum(input.style),
                duration_seconds=input.duration_seconds,
                include_audio_direction=input.include_audio_direction,
            )
            response = generator.generate(request)
        except Exception as exc:
            raise ValueError(f"Prompt generation failed: {exc}") from exc
        return response.prompt

    @strawberry.mutation
    def distribute_video(self, input: DistributeVideoInput) -> DistributionTaskType:
        """Enqueue video distribution to specified platforms."""
        asset = _video_assets.get(str(input.video_asset_id))
        if not asset:
            raise ValueError(f"Video asset {input.video_asset_id} not found")

        platforms = [PlatformEnum(p) for p in input.platforms]
        task = PydanticDistTask(
            id=str(uuid.uuid4()),
            video_asset_id=str(input.video_asset_id),
            platforms=platforms,
        )

        _distribution_tasks[task.id] = task
        return DistributionTaskType(
            id=strawberry.ID(task.id),
            video_asset_id=strawberry.ID(task.video_asset_id),
            platforms=input.platforms,
            results=[],
            created_at=task.created_at.isoformat(),
        )

    @strawberry.mutation
    def retry_generation(self, task_id: strawberry.ID) -> GenerationTaskType:
        """Retry a failed generation task."""
        task = _generation_tasks.get(str(task_id))
        if not task:
            raise ValueError(f"Generation task {task_id} not found")
        if task.status != VideoStatus.FAILED:
            raise ValueError(f"Task {task_id} is not in FAILED status")

        task.status = VideoStatus.PENDING
        task.error = None
        task.created_at = datetime.now(timezone.utc)
        return _pydantic_to_gql_gen_task(task)

    @strawberry.mutation
    def cancel_generation(self, task_id: strawberry.ID) -> GenerationTaskType:
        """Cancel a pending or generating task."""
        task = _generation_tasks.get(str(task_id))
        if not task:
            raise ValueError(f"Generation task {task_id} not found")

        task.status = VideoStatus.FAILED
        task.error = "Cancelled by user"
        return _pydantic_to_gql_gen_task(task)


# ── Schema ───────────────────────────────────────────────────────

schema = strawberry.Schema(query=Query, mutation=Mutation)
