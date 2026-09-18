"""Application-level errors mapped by the presentation layer."""


class ApplicationError(Exception):
    """Base class for expected application failures."""


class InvalidRequest(ApplicationError):
    """The request violates a business rule."""


class ResourceNotFound(ApplicationError):
    """A requested series, episode, or comment target does not exist."""
