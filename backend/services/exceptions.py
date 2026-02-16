from __future__ import annotations


class ServiceError(RuntimeError):
    pass


class ValidationError(ServiceError):
    pass
