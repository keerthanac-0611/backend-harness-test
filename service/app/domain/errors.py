class DomainError(Exception):
    """Base class for business rule violations."""


class EmailAlreadyRegisteredError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class CustomerNotFoundError(DomainError):
    pass


class WeakPasswordError(DomainError, ValueError):
    pass
