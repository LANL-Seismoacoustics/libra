"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Contains the `Registry` object, which caches schema definitions prior to the 
conversion into abstract SQLAlchemy ORM Table instances. 
"""

# ==============================================================================

import copy
from typing import (
    Any,
    TypeVar
)

from .util import (
    TypeMap,
    TypeHandler,
    ColumnHandler,
    ConstraintHandler
)
from .util import (
    ColumnNotFoundError,
    ModelNotFoundError
)

# ==============================================================================
# Typing

_UnbasedClass = TypeVar('_UnbasedClass', bound = Any)

# ==============================================================================

class Registry:
    """
    Cached container for schema defintions and ORM object serializers & de-
    serializers, both of which are needed to dynamically construct ORM 
    instances like columns, constraints, and models.

    Attributes
    ----------
    columns : dict[str, dict[str, Any]]
        Cached column definition dictionaries of the form:
        {'userid' : {'type' : Integer(), 'nullable' : True, 'default' : -1}}
    models : dict[str, dict[str, Any]]
        Cached model definition dictionaries of the form:
        {'user' : {'columns' : ['userid', 'name', 'email'], 
            'constraints' : [{'pk':{'columns':['userid']}}]}}
    typemap : libra.util.TypeMap
        TypeMap instance to map particular strings to specific SQLAlchemy type 
        objects during serialization & deserialization.
    columnhandler : libra.util.ColumnHandler
        ColumnHandler instance responsible for serializing & deserializing 
        column definitions contained in the Registry.columns attribute.
    constrainthandler : libra.util.ConstraintHandler
        ConstraintHandler instance responsible for serializing & deserializing 
        constraint definitions attached to the Registry.models attribute.
    """

    def __init__(self, typemap : TypeMap = TypeMap()) -> None:
        """
        Constructs a new Registry object. Initialized with empty containers for 
        columns, constraint, models, and other attributes alongside the 
        handlers to serialize & deserialize those ORM features.

        Parameters
        ----------
        typemap : libra.util.TypeMap
            TypeMap instance to map particular strings to specific SQLAlchemy type 
            objects during serialization & deserialization.
        """

        # Assign typemap as an attribute of the Registry object
        self.typemap = typemap

        # Cascade handlers as attributes of registry
        self.typehandler : TypeHandler = TypeHandler(self.typemap)
        self.columnhandler : ColumnHandler = ColumnHandler(self.typehandler)
        self.constrainthandler : ConstraintHandler = ConstraintHandler()

        # Empty data for various components
        self.columns : dict[str, dict[str, Any]] = {}
        self.models  : dict[str, dict[str, Any]] = {}
    
    def _create(self, model : str) -> _UnbasedClass:
        """
        Return a mapped-out class structure of a model given the information 
        contained within the registry column & model dictionaries; deserializing
        all ORM features using injected handlers in the process.

        Parameters
        ----------
        model : str
            Name of the model to create.
        
        Returns
        -------
        _UnbasedClass
            Standardized instance without an SQLAlchemy DeclarativeBase class - 
            contains SQLAlchemy Column instances & Constraints as attributes 
            of the unbased class, as well as any additional attributes or 
            methods. 
        
        Raises
        ------
        libra.util.ModelNotFoundError
            Raised in the event that the provided model name does not exist as a
            key in the Registry.model attribute.
        libra.util.ColunNotFoundError
            Raised in the event that a column name is not found in the Registry
            column attribute.
        """

        try:
            model_dict = copy.deepcopy(self.models[model])
        except KeyError:
            raise ModelNotFoundError(f'Model \'{model}\' not found in Registry')
        
        columns = {}
        for col in model_dict['columns']:
            
            try:
                col_name, coldef_dict = col, copy.deepcopy(self.columns[col])
            except KeyError:
                raise ColumnNotFoundError(f'Column \'{col}\' not found in Registry')
            
            columns[col_name] = self.columnhandler.deserialize({col_name : coldef_dict})
        
        constraints = model_dict.pop('constraints')

        del model_dict['columns']

        return type(
            model, (),
            {
                'constraints' : constraints,
                'columns' : columns,
                **model_dict # Everything else that wasn't a column or constraint
            }
        )

    def clear(self) -> None:
        """Clear models & columns attributes from Registry"""

        self.columns.clear()
        self.models.clear()

    def register_column(self, name : str, definition : dict[str, Any]) -> None:
        """
        Update the registry's columns attribute to include a column name and 
        its definition dictionary.

        Parameters
        ----------
        name : str
            Column name
        definition : dict[str, Any]
            Dictionary describing any key-value pairs to pass to a SQLAlchemy 
            Column instance.
        """

        self.columns[name] = definition
    
    def register_model(self, name : str, definition : dict[str, Any]) -> None:
        """
        Update the registry's models attribute to include a model name and its 
        definition dictionary.

        Parameters
        ----------
        name : str
            Model name
        definition : dict[str, Any]
            Dictionary describing columns and constraints belonging to a model.
        """

        self.models[name] = definition
