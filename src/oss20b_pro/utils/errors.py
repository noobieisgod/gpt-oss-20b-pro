from __future__ import annotations


class Oss20bError(Exception):
    """Base project error."""


class ConfigError(Oss20bError):
    """Raised when config cannot be loaded or validated."""


class BackendError(Oss20bError):
    """Base backend error."""


class ModelPathNotFoundError(BackendError):
    """Raised when the configured model path does not exist."""


class UnsupportedModelFormatError(BackendError):
    """Raised when a model path is not compatible with the selected backend."""


class IncompleteModelDirectoryError(BackendError):
    """Raised when a Transformers model directory is missing required files."""


class MissingBackendDependencyError(BackendError):
    """Raised when optional backend dependencies are missing."""


class ModelLoadError(BackendError):
    """Raised when backend model loading fails."""


class ServerUnreachableError(BackendError):
    """Raised when a configured local model server cannot be reached."""


class ServerTimeoutError(BackendError):
    """Raised when a configured local model server times out."""


class ServerResponseStatusError(BackendError):
    """Raised when a model server returns a non-success status."""


class InvalidBackendResponseError(BackendError):
    """Raised when a backend response is not shaped as expected."""


class MalformedStreamEventError(BackendError):
    """Raised when a streaming backend emits a malformed event."""
