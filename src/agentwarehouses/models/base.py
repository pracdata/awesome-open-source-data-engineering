"""Base model and shared types for agentwarehouses Pydantic models.

All models inherit from BaseModel here to ensure consistent config
across Pydantic 2.0 with forward-compatible 3.0 patterns.
"""

from __future__ import annotations

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class BaseModel(PydanticBaseModel):
    """Base for all agentwarehouses models. Pydantic 2.0 with 3.0-ready patterns."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_default=True,
        extra="forbid",
    )


class LenientModel(PydanticBaseModel):
    """Base model that allows extra fields for forward compatibility."""

    model_config = ConfigDict(
        populate_by_name=True,
        validate_default=True,
        extra="allow",
    )


class SemVer(BaseModel):
    """Semantic version following conventional-commits spec."""

    major: int = Field(ge=0)
    minor: int = Field(ge=0)
    patch: int = Field(ge=0)
    prerelease: str | None = None

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        return f"{base}-{self.prerelease}" if self.prerelease else base

    def bump_patch(self) -> SemVer:
        return SemVer(major=self.major, minor=self.minor, patch=self.patch + 1)

    def bump_minor(self) -> SemVer:
        return SemVer(major=self.major, minor=self.minor + 1, patch=0)

    def bump_major(self) -> SemVer:
        return SemVer(major=self.major + 1, minor=0, patch=0)
