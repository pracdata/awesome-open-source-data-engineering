"""SemVer, conventional commits, and upstream dependency tracking models."""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

__all__ = [
    "SemVer",
    "ConventionalCommitType",
    "ConventionalCommit",
    "UpstreamDependency",
    "DependencyBump",
    "ReleaseManifest",
    "ReleasePleaseConfig",
    "PackageConfig",
    "ChangelogSection",
]

SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<pre>[0-9A-Za-z\-.]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z\-.]+))?$"
)


class SemVer(BaseModel):
    """Semantic version per semver.org 2.0.0."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    major: int = Field(ge=0)
    minor: int = Field(ge=0)
    patch: int = Field(ge=0)
    prerelease: str | None = None
    build_metadata: str | None = None

    @classmethod
    def parse(cls, version: str) -> SemVer:
        m = SEMVER_RE.match(version.strip())
        if not m:
            raise ValueError(f"Invalid semver: {version}")
        return cls(
            major=int(m["major"]),
            minor=int(m["minor"]),
            patch=int(m["patch"]),
            prerelease=m["pre"],
            build_metadata=m["build"],
        )

    def __str__(self) -> str:
        v = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            v += f"-{self.prerelease}"
        if self.build_metadata:
            v += f"+{self.build_metadata}"
        return v

    def bump_major(self) -> SemVer:
        return SemVer(major=self.major + 1, minor=0, patch=0)

    def bump_minor(self) -> SemVer:
        return SemVer(major=self.major, minor=self.minor + 1, patch=0)

    def bump_patch(self) -> SemVer:
        return SemVer(major=self.major, minor=self.minor, patch=self.patch + 1)


class ConventionalCommitType(StrEnum):
    """Conventional Commits 1.0.0 types."""

    FEAT = "feat"
    FIX = "fix"
    DEPS = "deps"
    CHORE = "chore"
    DOCS = "docs"
    REFACTOR = "refactor"
    PERF = "perf"
    TEST = "test"
    CI = "ci"
    BUILD = "build"
    REVERT = "revert"


class ConventionalCommit(BaseModel):
    """A conventional commit message parsed into structured fields."""

    model_config = ConfigDict(str_strip_whitespace=True)

    type: ConventionalCommitType
    scope: str | None = None
    description: str
    body: str | None = None
    breaking: bool = False
    footers: dict[str, str] = Field(default_factory=dict)

    def format_subject(self) -> str:
        scope = f"({self.scope})" if self.scope else ""
        bang = "!" if self.breaking else ""
        return f"{self.type}{scope}{bang}: {self.description}"

    def bump_type(self) -> str:
        """Return 'major', 'minor', or 'patch' based on commit semantics."""
        if self.breaking:
            return "major"
        if self.type == ConventionalCommitType.FEAT:
            return "minor"
        return "patch"


class UpstreamDependency(BaseModel):
    """An upstream dependency whose version changes trigger a model bump.

    When anthropic SDK or MCP SDK v2 publishes a new release, renovate/dependabot
    creates a PR with a `deps(anthropic-sdk): bump to X.Y.Z` commit. release-please
    picks this up and bumps our MINOR version.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(description="PyPI package name")
    repository: str = Field(description="GitHub repo (owner/name)")
    min_version: SemVer = Field(description="Minimum supported version")
    current_version: SemVer | None = Field(default=None, description="Currently pinned version")
    bump_on_update: ConventionalCommitType = Field(
        default=ConventionalCommitType.DEPS,
        description="Commit type to use when this dep updates",
    )

    @field_validator("repository")
    @classmethod
    def validate_repo(cls, v: str) -> str:
        if "/" not in v:
            raise ValueError(f"Repository must be owner/name format: {v}")
        return v


class DependencyBump(BaseModel):
    """Record of a dependency version bump."""

    model_config = ConfigDict(str_strip_whitespace=True)

    dependency: str
    from_version: SemVer
    to_version: SemVer
    commit: ConventionalCommit
    bumped_at: datetime = Field(default_factory=datetime.utcnow)


class ChangelogSection(BaseModel):
    """release-please changelog section mapping."""

    type: str
    section: str
    hidden: bool = False


class PackageConfig(BaseModel):
    """release-please per-package configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    release_type: str = Field(default="python", alias="release-type")
    package_name: str = Field(alias="package-name")
    bump_minor_pre_major: bool = Field(default=True, alias="bump-minor-pre-major")
    bump_patch_for_minor_pre_major: bool = Field(default=True, alias="bump-patch-for-minor-pre-major")
    changelog_path: str = Field(default="CHANGELOG.md", alias="changelog-path")
    versioning: str = "default"
    extra_files: list[str] = Field(default_factory=list, alias="extra-files")


class ReleasePleaseConfig(BaseModel):
    """release-please-config.json schema."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    packages: dict[str, PackageConfig]
    changelog_sections: list[ChangelogSection] = Field(default_factory=list, alias="changelog-sections")


class ReleaseManifest(BaseModel):
    """.release-please-manifest.json — maps package paths to current versions."""

    model_config = ConfigDict(extra="allow")

    versions: dict[str, str] = Field(default_factory=dict)
