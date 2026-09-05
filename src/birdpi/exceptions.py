"""
BirdPi exception hierarchy.
"""


class BirdPiError(Exception):
    """Base exception for expected BirdPi errors."""


class CameraError(BirdPiError):
    """Base exception for camera related errors."""


class CaptureError(CameraError):
    """Raised when an image capture fails."""


class PreviewError(CameraError):
    """Raised when the camera preview fails."""


class VideoError(CameraError):
    """Raised when video recording or processing fails."""


class StorageError(BirdPiError):
    """Base exception for storage related errors."""


class ThumbnailError(StorageError):
    """Raised when thumbnail creation fails."""


class RuntimeCommandError(BirdPiError):
    """Raised when communication with the runtime fails."""


class ServiceControlError(BirdPiError):
    """Raised when service control fails."""
