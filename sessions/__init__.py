"""Sessions — auto-populating session templates with device/surface detection."""

from sessions.session_template import SessionTemplate
from sessions.surface_lookup import DeviceInfo, SurfaceInfo, detect_device, detect_surface

__all__ = [
    "SessionTemplate",
    "DeviceInfo",
    "SurfaceInfo",
    "detect_device",
    "detect_surface",
]
