"""
Brady Spears
7/17/25

Contains the `Registry` object, which is the object responsible for containing 
information related to models, columns, and constraints needed to construct an 
abstract ORM instance.
"""

# ==============================================================================

from __future__ import annotations
import pdb
from typing import Any

from sqlalchemy.orm import DeclarativeMeta

from libra.util import (
    ColumnHandler,
    ConstraintHandler,
    TypeHandler,
    TypeMap
)

# ==============================================================================

class Registry:
    """
    Container for information needed to construct ORM instances, including 
    various handler objects (which act as plain-text to SQLAlchemy object 
    converters) and the plain-text definitions for models, columns, and 
    constraints belonging to a schema.

    Attributes
    ----------

    Methods
    -------
    """

    def __init__(self, typemap : TypeMap = TypeMap()) -> None:
        """
        Constructs a new registry object. Initialized with empty containers for 
        columns, constraints, and models and various handler objects.

        Parameters
        ----------
        typemap : TypeMap
            Object of libra.util.handler module mapping Python string values 
            uniquely to specific SQLAlchemy Type objects.
        """

        # Assign typemap as an attribute of Registry object
        self.typemap : TypeMap = typemap

        # Cascade handlers as attributes of Registry
        self.typehandler : TypeHandler = TypeHandler(self.typemap)
        self.columnhandler : ColumnHandler = ColumnHandler(self.typehandler)
        self.constrainthandler : ConstraintHandler = ConstraintHandler()

        # Empty data for various components of abstract ORMs
        self.columns : dict[str, dict[str, Any]] = {}
        self.models : dict[str, dict[str, Any]]  = {}

    def _create(self, model : str) -> Any:

        model_dict = self.models[model]

        columns = {}
        for col in model_dict['columns']:
            if isinstance(col, str):
                col_name, coldef_dict = col, {}
            else:
                col_name, coldef_dict = list(col.keys())[0], list(col.values())[0]

            coldef_dict.update(self.columns[col_name])
            columns[col_name] = self.columnhandler.construct(col_name, coldef_dict)
        
        constraints = model_dict['constraints']

        return type(model, (), {'constraints' : constraints, 'columns' : columns})

# ==============================================================================
