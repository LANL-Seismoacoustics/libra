"""
Brady Spears
5/5/25

Libra-specific exceptions.
"""

# ==============================================================================

class LibraException(Exception):
    def __init__(self, message : str) -> None:
        super().__init__(message)

# ==============================================================================

class SchemaNotFoundError(LibraException): 
    """Raised when a schema name is not found in a schema repository resource."""
    ...

class ModelNotFoundError(LibraException):
    """Raised when a model name is not found in a schema repository resource."""
    ...

class ColumnNotFoundError(LibraException):
    """Raised when a column name is not found in a schema repository resource."""

class TableNotFoundError(LibraException): 
    """Raised when the table name associated with a table is not found in the database."""
    ...

