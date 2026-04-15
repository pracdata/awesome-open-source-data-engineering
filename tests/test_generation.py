"""Tests for the generation pipeline — Claude prompts, Veo client, GraphQL server.

Uses unittest.mock to avoid real API calls to Anthropic and Google.
Skipped when generation extras are not installed (CI installs dev+models+warehouse only).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# Skip entire module when generation deps (anthropic, google-genai, strawberry) aren't installed
pytest.importorskip("anthropic", reason="generation extras not installed")
pytest.importorskip("google.genai", reason="generation extras not installed")

from agentwarehouses.models.video import (
    CinematicPromptRequest,
    CinematicPromptResponse,
    GenerationConfig,
    GenerationModel,
    GenerationTask,
    PromptStyle,
    VideoAsset,
    VideoMetadata,
    VideoResolution,
    VideoStatus,
)

# ── Claude Prompts Tests ─────────────────────────────────────────


class TestCinematicPromptGenerator:
    @patch("agentwarehouses.generation.claude_prompts.anthropic.Anthropic")
    def test_generate_returns_response(self, mock_anthropic_cls):
        from agentwarehouses.generation.claude_prompts import CinematicPromptGenerator

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="A slow dolly shot reveals a mountain at dawn.")]
        mock_message.usage.input_tokens = 150
        mock_message.usage.output_tokens = 80
        mock_message.usage.cache_read_input_tokens = 0
        mock_message.usage.cache_creation_input_tokens = 50
        mock_client.messages.create.return_value = mock_message

        gen = CinematicPromptGenerator(api_key="test-key")
        request = CinematicPromptRequest(topic="Mountain sunrise")
        response = gen.generate(request)

        assert isinstance(response, CinematicPromptResponse)
        assert "dolly" in response.prompt
        assert response.style == PromptStyle.CINEMATIC
        assert response.model_used == "claude-opus-4-6"
        assert response.usage["input_tokens"] == 150

        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-opus-4-6"
        assert call_kwargs["max_tokens"] == 2048

    @patch("agentwarehouses.generation.claude_prompts.anthropic.Anthropic")
    def test_generate_with_negative_splits_output(self, mock_anthropic_cls):
        from agentwarehouses.generation.claude_prompts import CinematicPromptGenerator

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Cinematic ocean waves.\nNEGATIVE: blurry, artifacts")]
        mock_message.usage.input_tokens = 100
        mock_message.usage.output_tokens = 60
        mock_client.messages.create.return_value = mock_message

        gen = CinematicPromptGenerator(api_key="test-key")
        request = CinematicPromptRequest(topic="Ocean waves", style=PromptStyle.DOCUMENTARY)
        response = gen.generate_with_negative(request)

        assert response.prompt == "Cinematic ocean waves."
        assert response.negative_prompt == "blurry, artifacts"

    @patch("agentwarehouses.generation.claude_prompts.anthropic.Anthropic")
    def test_generate_with_negative_no_negative_marker(self, mock_anthropic_cls):
        from agentwarehouses.generation.claude_prompts import CinematicPromptGenerator

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Just a prompt, no negative.")]
        mock_message.usage.input_tokens = 80
        mock_message.usage.output_tokens = 30
        mock_client.messages.create.return_value = mock_message

        gen = CinematicPromptGenerator(api_key="test-key")
        request = CinematicPromptRequest(topic="Simple scene")
        response = gen.generate_with_negative(request)

        assert response.prompt == "Just a prompt, no negative."
        assert response.negative_prompt is None

    @patch("agentwarehouses.generation.claude_prompts.anthropic.Anthropic")
    def test_generate_api_error_logged_and_raised(self, mock_anthropic_cls):
        import anthropic

        from agentwarehouses.generation.claude_prompts import CinematicPromptGenerator

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.side_effect = anthropic.APIError(
            message="rate limited", request=MagicMock(), body=None
        )

        gen = CinematicPromptGenerator(api_key="test-key")
        request = CinematicPromptRequest(topic="Test topic")
        with pytest.raises(anthropic.APIError):
            gen.generate(request)

    @patch("agentwarehouses.generation.claude_prompts.anthropic.Anthropic")
    def test_all_styles_produce_different_system_prompts(self, mock_anthropic_cls):
        from agentwarehouses.generation.claude_prompts import CinematicPromptGenerator

        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Prompt text")]
        mock_message.usage.input_tokens = 50
        mock_message.usage.output_tokens = 20
        mock_client.messages.create.return_value = mock_message

        gen = CinematicPromptGenerator(api_key="test-key")
        system_prompts = set()

        for style in PromptStyle:
            request = CinematicPromptRequest(topic="Test", style=style)
            gen.generate(request)
            call_kwargs = mock_client.messages.create.call_args[1]
            system_prompts.add(call_kwargs["system"])

        assert len(system_prompts) == len(PromptStyle)


# ── Veo Client Tests ─────────────────────────────────────────────


class TestVeoClient:
    @patch("agentwarehouses.generation.veo_client.genai.Client")
    def test_submit_generation_success(self, mock_client_cls):
        from agentwarehouses.generation.veo_client import VeoClient

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_operation = MagicMock()
        mock_client.models.generate_videos.return_value = mock_operation

        client = VeoClient(api_key="test-key")
        operation, task = client.submit_generation(prompt="A sunrise", title="Sunrise Video")

        assert operation is mock_operation
        assert task.status == VideoStatus.GENERATING
        assert task.prompt == "A sunrise"
        assert task.video_asset is not None
        assert task.video_asset.metadata.title == "Sunrise Video"
        mock_client.models.generate_videos.assert_called_once()

    @patch("agentwarehouses.generation.veo_client.genai.Client")
    def test_submit_generation_api_failure(self, mock_client_cls):
        from agentwarehouses.generation.veo_client import VeoClient

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.models.generate_videos.side_effect = RuntimeError("API unavailable")

        client = VeoClient(api_key="test-key")
        operation, task = client.submit_generation(prompt="Failing test")

        assert operation is None
        assert task.status == VideoStatus.FAILED
        assert "submission failed" in task.error

    @patch("agentwarehouses.generation.veo_client.genai.Client")
    def test_poll_generation_none_operation(self, mock_client_cls):
        from agentwarehouses.generation.veo_client import VeoClient

        client = VeoClient(api_key="test-key")
        task = GenerationTask(id="t1", prompt="test", status=VideoStatus.FAILED, error="already failed")

        result = client.poll_generation(None, task)
        assert result is task
        assert result.status == VideoStatus.FAILED

    @patch("agentwarehouses.generation.veo_client.genai.Client")
    @patch("agentwarehouses.generation.veo_client.time.sleep")
    def test_poll_generation_timeout(self, mock_sleep, mock_client_cls):
        from agentwarehouses.generation.veo_client import VeoClient

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_operation = MagicMock()
        mock_operation.done = False
        mock_client.operations.get.return_value = mock_operation

        client = VeoClient(api_key="test-key")
        task = GenerationTask(id="t1", prompt="test", status=VideoStatus.GENERATING)

        result = client.poll_generation(mock_operation, task, poll_interval=1.0, max_wait=2.0)

        assert result.status == VideoStatus.FAILED
        assert "timed out" in result.error

    @patch("agentwarehouses.generation.veo_client.genai.Client")
    @patch("agentwarehouses.generation.veo_client.time.sleep")
    def test_poll_generation_no_videos(self, mock_sleep, mock_client_cls):
        from agentwarehouses.generation.veo_client import VeoClient

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.result.generated_videos = []

        client = VeoClient(api_key="test-key")
        task = GenerationTask(id="t1", prompt="test", status=VideoStatus.GENERATING)

        result = client.poll_generation(mock_operation, task)

        assert result.status == VideoStatus.FAILED
        assert "No videos" in result.error

    @patch("agentwarehouses.generation.veo_client.genai.Client")
    @patch("agentwarehouses.generation.veo_client.time.sleep")
    def test_poll_generation_success(self, mock_sleep, mock_client_cls):
        from agentwarehouses.generation.veo_client import VeoClient

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_video = MagicMock()
        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.result.generated_videos = [mock_video]
        mock_client.files.download.return_value = b"fake-video-bytes"

        client = VeoClient(api_key="test-key")
        task = GenerationTask(
            id="t1",
            prompt="test",
            status=VideoStatus.GENERATING,
            video_asset=VideoAsset(
                id="a1",
                status=VideoStatus.GENERATING,
                metadata=VideoMetadata(title="Test", duration_seconds=10.0),
            ),
        )

        result = client.poll_generation(mock_operation, task, output_dir="/tmp/test-videos")

        assert result.status == VideoStatus.READY
        assert result.video_asset.status == VideoStatus.READY
        assert result.video_asset.url is not None

    @patch("agentwarehouses.generation.veo_client.genai.Client")
    def test_generate_and_wait_delegates(self, mock_client_cls):
        from agentwarehouses.generation.veo_client import VeoClient

        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_operation.result.generated_videos = []
        mock_client.models.generate_videos.return_value = mock_operation

        client = VeoClient(api_key="test-key")
        result = client.generate_and_wait(prompt="Test prompt", title="Test")

        assert result.status == VideoStatus.FAILED


# ── GraphQL Server Tests ─────────────────────────────────────────


class TestGraphQLConverters:
    def test_pydantic_to_gql_video_asset(self):
        from agentwarehouses.generation.graphql_server import _pydantic_to_gql_video_asset

        asset = VideoAsset(
            id="a1",
            url="https://example.com/video.mp4",
            status=VideoStatus.READY,
            metadata=VideoMetadata(title="Test Video", duration_seconds=10.0, resolution=VideoResolution.HD_1080P),
        )
        gql = _pydantic_to_gql_video_asset(asset)

        assert str(gql.id) == "a1"
        assert gql.url == "https://example.com/video.mp4"
        assert gql.status == "ready"
        assert gql.metadata.title == "Test Video"
        assert gql.metadata.resolution == "1080p"

    def test_pydantic_to_gql_gen_task(self):
        from agentwarehouses.generation.graphql_server import _pydantic_to_gql_gen_task

        task = GenerationTask(
            id="t1",
            prompt="Test prompt",
            config=GenerationConfig(model=GenerationModel.VEO_3_1_FAST),
            status=VideoStatus.PENDING,
        )
        gql = _pydantic_to_gql_gen_task(task)

        assert str(gql.id) == "t1"
        assert gql.prompt == "Test prompt"
        assert gql.model == "veo-3.1-fast-generate-001"
        assert gql.status == "pending"
        assert gql.video_asset is None
