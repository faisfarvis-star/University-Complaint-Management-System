class ServiceError(Exception):
    """Base class for business-rule failures raised by the service layer."""


class ValidationError(ServiceError):
    pass


class PermissionDenied(ServiceError):
    pass


class InvalidTransition(ServiceError):
    pass


class NotFound(ServiceError):
    pass
