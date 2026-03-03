"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Contains various `Error` objects which describe Libra-specific requirements 
when serializing & deserializing ORM instances.
"""

# ==============================================================================

class LibraException(Exception):
    def __init__(self, message : str) -> None:
        super().__init__(message)

class SchemaNotFoundError(LibraException):
    """Raised when a schema is not found within a schema definition source"""
    ...

class ModelNotFoundError(LibraException):
    """Raised when a schema is not found within a schema definition source or registry"""
    ...

class ColumnNotFoundError(LibraException):
    """Raised when a schema is not found within a schema definition source or registry"""
    ...

class StrategyUnsupported(LibraException):
    """Raised when a Schema load/dump strategy is not supported"""
    ...

class BackendUnsupported(LibraException):
    """Raised when a dialect is unsupported for a particular feature in Libra"""
    ...
    