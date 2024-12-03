from __future__ import annotations
from abc import ABC, abstractmethod
import os
from typing import Any

from sqlalchemy.orm import Session as _Session

# ==============================================================================
# Abstract SchemaTransferStrategy

class SchemaTransferStrategy(ABC):
    """Abstract base class to handle dynamic loading/writing of schema info"""

    @abstractmethod
    def load(self, schema : Schema) -> Schema:
        """Required load method for a transfer strategy"""
    
    @abstractmethod
    def write(self, schema : Schema) -> None:
        """Required write method for a transfer strategy"""

# ==============================================================================
# Load/write Schema object to/from a Python dictionary

class SchemaTransferDict(SchemaTransferStrategy):
    """Load/write methods for schema metadata within a Python dictionary.
    
    SchemaTransferDict is a subclass of abstract base class 
    SchemaTransferStrategy and defines load & write methods for schema metadata 
    that is encoded in a specifically-formatted Python dictionary.
    """

    def load(
        schema : Schema,
        schema_dict : dict[str, Any],
        models : str | list[str] | None = None
    ) -> Schema:
        pass

    def write(
        schema : Schema
    ) -> None:
        return NotImplementedError

# ==============================================================================
# Load/write Schema object to/from YAML file

class SchemaTransferYAML(SchemaTransferStrategy):
    """Load/write methods for schema metadata contained in a YAML file.
    
    SchemaTransferYAML is a subclass of abstract base class 
    SchemaTransferStrategy and defines load & write methods for schema metadata
    that is encoded in a specifically-formatted YAML file.

    Note: The SchemaTransferYAML.load() method acts as a wrapper to the 
    SchemaTransferDict.load() method, where the dictionary object loaded from 
    the given YAML file is passed on as the input dictionary for 
    SchemaTransferDict.load().
    """

    def load(
        schema : Schema,
        file : str | os.PathLike,
        models : str | list[str] | None = None
    ) -> Schema:
        pass

    def write(
        schema : Schema
    ) -> None:
        return NotImplementedError

# ==============================================================================
# Load/write Schema object to/from database tables

class SchemaTransferDB(SchemaTransferStrategy):
    """Load/write methods for schema metadata contained in database tables.
    
    SchemaTransferDB is a subclass of abstract base class
    SchemaTransferStrategy and defines load & write methods for schema metadata
    that is encoded in specifically-formatted relational database tables.

    Note: The SchemaTransferDB.load() method acts as a wrapper to the 
    SchemaTransferDict.load() method, where input db tables are queried and 
    converted into Python dictionary objects (key-value pairs where keys are 
    the columns of the db table). These dictionary objects are passed on 
    as the input dictionary to the SchemaTransferDict.load() method.
    """

    def load(
        schema : Schema,
        session : _Session,
        models : str | list[str] | None = None
    ) -> None:
        pass

    def write(
        schema : Schema
    ) -> None:
        return NotImplementedError