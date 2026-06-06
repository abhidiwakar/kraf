class ProjectInitializerError(Exception):
    """Base class for user-facing project initializer errors."""


class InvalidProjectNameError(ProjectInitializerError):
    """Raised when a project name cannot produce a valid slug or package name."""


class PackError(ProjectInitializerError):
    """Raised when pack manifests or pack selections are invalid."""


class RenderError(ProjectInitializerError):
    """Raised when a project cannot be rendered safely."""
