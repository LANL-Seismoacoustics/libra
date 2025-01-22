from __future__ import annotations
import os
from typing import Any
from typing import TypedDict, TypeVar
from typing import TYPE_CHECKING

import sqlalchemy
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import Session

from .transfer import SchemaTransferStrategy
if TYPE_CHECKING:
    from ..schema import Schema

# ==============================================================================
# Generic Typehinting

# Arbitrary Mixin class is any class designed to add functionality to an 
#  abstract ORM instance, additional to the DeclarativeMeta class that the 
#  ORM primarily inherits from.
_Mixin   = TypeVar('_Mixin', bound = Any)

# Arbitrary type inheriting from any SQLAlchemy datatype object. For a full 
#  list of these objects: https://docs.sqlalchemy.org/en/20/core/types.html
_SQLType = TypeVar('_SQLType', bound = sqlalchemy.types)

# Arbitrary type representing an abstract ORM instance prior to the addition of 
#  a user-defined DeclarativeMeta and any other Mixin classes. Upon processing,
#  (see schema._process_orm() method), the resultant ORM inherits from 
#  DeclarativeMeta and any provided Mixin classes.
_PreprocessedORM = TypeVar('_PreprocessedORM', bound = Any)

# Arbitrary type representing a "processed" ORM instance. Processed involves 
#  the re-casting of a _PreprocessedORM type to a child of the DeclarativeMeta 
#  metaclass. The processed ORM instance will also inherit secondarily from any 
#  other declared Mixin classes.
_ProcessedORM = TypeVar('_ProcessedORM', bound = DeclarativeMeta)

# ==============================================================================
# Schema method parameters

class SchemaLoadParams(TypedDict):
    """Acceptable parameters to pass to the Schema.load() method"""

    schema : Schema
    models : str | list[str] | None

    file : str | os.PathLike | None
    schema_dict : dict[str, Any] | None
    session : Session | None

    strategy : type[SchemaTransferStrategy] | None

class SchemaWriteParams(TypedDict):
    """Acceptable parameters to pass to the Schema.write() method"""

    pass

# ==============================================================================