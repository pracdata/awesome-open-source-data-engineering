"""Tests for version, semver, conventional commits, and dependency tracking."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from claude_code_models.models.version import (
    ChangelogSection,
    ConventionalCommit,
    ConventionalCommitType,
    DependencyBump,
    PackageConfig,
    ReleaseManifest,
    ReleasePleaseConfig,
    SemVer,
    UpstreamDependency,
)


class TestSemVer:
    @pytest.mark.semver
    def test_parse_basic(self) -> None:
        v = SemVer.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease is None
        assert v.build_metadata is None

    @pytest.mark.semver
    def test_parse_prerelease(self) -> None:
        v = SemVer.parse("0.1.0-alpha.1")
        assert v.prerelease == "alpha.1"
        assert str(v) == "0.1.0-alpha.1"

    @pytest.mark.semver
    def test_parse_build_metadata(self) -> None:
        v = SemVer.parse("1.0.0+build.42")
        assert v.build_metadata == "build.42"
        assert str(v) == "1.0.0+build.42"

    @pytest.mark.semver
    def test_parse_full(self) -> None:
        v = SemVer.parse("2.3.4-beta.2+sha.abc123")
        assert str(v) == "2.3.4-beta.2+sha.abc123"

    @pytest.mark.semver
    @pytest.mark.validation
    def test_parse_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid semver"):
            SemVer.parse("not-a-version")

    @pytest.mark.semver
    @pytest.mark.validation
    def test_parse_incomplete(self) -> None:
        with pytest.raises(ValueError, match="Invalid semver"):
            SemVer.parse("1.2")

    @pytest.mark.semver
    def test_bump_major(self) -> None:
        v = SemVer.parse("1.2.3")
        bumped = v.bump_major()
        assert str(bumped) == "2.0.0"

    @pytest.mark.semver
    def test_bump_minor(self) -> None:
        v = SemVer.parse("1.2.3")
        bumped = v.bump_minor()
        assert str(bumped) == "1.3.0"

    @pytest.mark.semver
    def test_bump_patch(self) -> None:
        v = SemVer.parse("1.2.3")
        bumped = v.bump_patch()
        assert str(bumped) == "1.2.4"

    @pytest.mark.semver
    def test_frozen(self) -> None:
        v = SemVer.parse("1.0.0")
        with pytest.raises(ValidationError):
            v.major = 2  # type: ignore[misc]

    @pytest.mark.semver
    def test_str_roundtrip(self) -> None:
        original = "3.14.159-rc.1+meta"
        assert str(SemVer.parse(original)) == original

    @pytest.mark.semver
    @pytest.mark.validation
    def test_negative_version(self) -> None:
        with pytest.raises(ValidationError):
            SemVer(major=-1, minor=0, patch=0)

    @pytest.mark.semver
    def test_zero_version(self) -> None:
        v = SemVer(major=0, minor=0, patch=0)
        assert str(v) == "0.0.0"


class TestConventionalCommit:
    def test_feat_commit(self) -> None:
        cc = ConventionalCommit(
            type=ConventionalCommitType.FEAT,
            scope="hooks",
            description="add PostCompact event",
        )
        assert cc.format_subject() == "feat(hooks): add PostCompact event"
        assert cc.bump_type() == "minor"

    def test_fix_commit(self) -> None:
        cc = ConventionalCommit(
            type=ConventionalCommitType.FIX,
            description="resolve null pointer in parser",
        )
        assert cc.format_subject() == "fix: resolve null pointer in parser"
        assert cc.bump_type() == "patch"

    def test_breaking_commit(self) -> None:
        cc = ConventionalCommit(
            type=ConventionalCommitType.FEAT,
            scope="api",
            description="remove v1 endpoints",
            breaking=True,
        )
        assert cc.format_subject() == "feat(api)!: remove v1 endpoints"
        assert cc.bump_type() == "major"

    def test_deps_commit(self) -> None:
        cc = ConventionalCommit(
            type=ConventionalCommitType.DEPS,
            scope="anthropic-sdk",
            description="bump to 0.53.0",
        )
        assert cc.bump_type() == "patch"
        assert "deps(anthropic-sdk)" in cc.format_subject()

    def test_with_footers(self) -> None:
        cc = ConventionalCommit(
            type=ConventionalCommitType.FIX,
            description="fix regression",
            footers={"Reviewed-by": "alice", "Refs": "#123"},
        )
        assert len(cc.footers) == 2

    @pytest.mark.validation
    def test_invalid_type(self) -> None:
        with pytest.raises(ValidationError):
            ConventionalCommit(type="invalid", description="test")  # type: ignore[arg-type]


class TestUpstreamDependency:
    def test_anthropic_sdk(self) -> None:
        dep = UpstreamDependency(
            name="anthropic",
            repository="anthropics/anthropic-sdk-python",
            min_version=SemVer.parse("0.52.0"),
        )
        assert dep.name == "anthropic"
        assert dep.repository == "anthropics/anthropic-sdk-python"
        assert dep.min_version.minor == 52

    def test_mcp_sdk(self) -> None:
        dep = UpstreamDependency(
            name="mcp",
            repository="modelcontextprotocol/python-sdk",
            min_version=SemVer.parse("1.9.0"),
            current_version=SemVer.parse("1.9.2"),
        )
        assert dep.current_version is not None
        assert dep.current_version.patch == 2

    @pytest.mark.validation
    def test_invalid_repository(self) -> None:
        with pytest.raises(ValidationError, match="owner/name"):
            UpstreamDependency(
                name="bad",
                repository="no-slash",
                min_version=SemVer.parse("1.0.0"),
            )


class TestDependencyBump:
    def test_create(self) -> None:
        bump = DependencyBump(
            dependency="anthropic",
            from_version=SemVer.parse("0.52.0"),
            to_version=SemVer.parse("0.53.0"),
            commit=ConventionalCommit(
                type=ConventionalCommitType.DEPS,
                scope="anthropic-sdk",
                description="bump to 0.53.0",
            ),
        )
        assert bump.dependency == "anthropic"
        assert bump.bumped_at is not None

    @pytest.mark.serialization
    def test_json_roundtrip(self) -> None:
        bump = DependencyBump(
            dependency="mcp",
            from_version=SemVer.parse("1.9.0"),
            to_version=SemVer.parse("1.10.0"),
            commit=ConventionalCommit(
                type=ConventionalCommitType.DEPS,
                description="bump mcp",
            ),
        )
        data = bump.model_dump(mode="json")
        restored = DependencyBump.model_validate(data)
        assert restored.dependency == bump.dependency


class TestReleasePleaseConfig:
    def test_config(self) -> None:
        config = ReleasePleaseConfig(
            packages={
                "claude_code_models": PackageConfig(
                    **{  # type: ignore[arg-type]
                        "release-type": "python",
                        "package-name": "claude-code-models",
                    }
                )
            },
            **{"changelog-sections": [ChangelogSection(type="feat", section="Features")]},  # type: ignore[arg-type]
        )
        assert "claude_code_models" in config.packages

    @pytest.mark.serialization
    def test_manifest(self) -> None:
        m = ReleaseManifest(versions={"claude_code_models": "0.1.0"})
        assert m.versions["claude_code_models"] == "0.1.0"
