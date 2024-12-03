from __future__ import annotations

class LibraError(Exception):
    """Specific Errors handled by Libra"""

# ==============================================================================

class SchemaNotFoundError(LibraError):
    """Raise when a schema is not found in the provided schema definition repo"""

    def __init__(self, schema_name : str) -> None:
        self.schema_name = schema_name
    
    def __str__(self) -> str:
        return f'Schema \'{self.schema_name}\' not found in the provided schema definition repository.'

class ModelNotFoundError(LibraError):
    """Raise when a model is not found in provided schema definition repo"""

    def __init__(self, model_name : str) -> None:
        self.model_name = model_name
    
    def __str__(self) -> str:
        return f'Model \'{self.model_name}\' not found in the provided schema definition repository.'
    
class ColumnNotFoundError(LibraError):
    """Raise when a model is not found in provided schema definition repo"""

    def __init__(self, col_name : str) -> None:
        self.col_name = col_name
    
    def __str__(self) -> str:
        return f'Column \'{self.col_name}\' not found in the provided schema definition repository.'