"""
Brady Spears
7/16/25

Contains the `Schema` object, which is the primary object for containing 
abstract object-relation-mapped (ORM) instances, A.K.A "Models". Models within 
the `Schema` object can be mapped to relational database tables in your SQL 
backend by assigning the respective model a '__tablename__' attribute. 

The `Schema` object can load and write models to/from various text-based 
formats. Libra supports three built-in options, herein referred to as "Transfer 
Strategies," which must, as an abstract base class, have a 'load()' and 
'write()' method defined. The three built-in strategies include loading/writing 
to/from (1) Python Dictionaries, (2) YAML files, or (3) relational database 
tables. By inheriting from the abstract TransferStrategy class, end users can 
define load/write methods for their own formats as well.
"""

# ==============================================================================

from __future__ import annotations
import os
import pdb
import ast
from abc import ABC, abstractmethod
from typing import Any
from typing import Self, TextIO

import yaml
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr

from libra.metaclass import MetaClass
from libra.registry import Registry
from libra.util import TypeMap
from libra.util.settings import _SchemaSettings
from libra.util import (
    DictionarySettings,
    YAMLFileSettings,
    DatabaseSettings
)

# ==============================================================================

LIBRA_YAML : os.PathLike = os.path.abspath('libra/schemas/libra.yaml')

# ==============================================================================

class Schema:
    """
    Primary class responsible for containing abstract object-relation-mapped 
    (ORM) instances, or models. The term "Schema" in the context of Libra 
    refers to a set of logically related tables, not necessarily a set of tables
    that belong to a single database user or namespace, as is customary in some 
    RDMS dialects.

    Models contain columns and constraints, and models are added to the `Schema`
    object as attributes. They remain disconnected from your physical RDMS until
    a __tablename__ attribute is assigned.

    Attributes
    ----------

    Methods
    -------
    """

    def __init__(self, name : str, *,
            description : str | None = None,
            metaclass : type[DeclarativeMeta] = MetaClass,
            typemap : TypeMap = TypeMap(),
            mixins : tuple[type[DeclarativeMeta]] | None = None,
        ) -> None:
        """
        Constructs a new `Schema` object.

        Parameters
        ----------
        name : str
            Name of the associated schema.
        metaclass : type[DeclarativeMeta], optional
            Child of sqlalchemy.orm.DeclarativeMeta class, whose attributes and 
            methods are passed onto every constructed model belonging to Schema.
        typemap : TypeMap, optional
            libra.util.TypeMap object defining which specific strings map to 
            which SQLAlchemy Type object. Used in parsing of plain-text files.
        mixins : tuple[type[DeclarativeMeta]], optional
            Additional classes with methods to augment SQLAlchemy's declarative 
            base class derived from the above metaclass.
        """

        self.name = name
        
        self.typemap = typemap
        self.registry = Registry(self.typemap)
        
        self.base = declarative_base(metaclass = metaclass)

        if not mixins:
            mixins = ()
        
        self.mixins = mixins

        self.description = description
    
    def add_model(self, cls : Any) -> None:

        model_name = cls.__name__
        self.registry.models.update({model_name: {'columns' : [], 'constraints' : []}})
        for key, val in cls.__dict__.items():
            if isinstance(val, Column):
                self.registry.models[model_name]['columns'].append(key)

                self.registry.columns.update(self.registry.columnhandler.deconstruct(key, val))
            
            elif key == 'pk' or key == 'uq':
                self.registry.models[model_name]['constraints'].append({key : val})
            
            elif key == '__table_args__':
                # Assume a declared_attr was passed to __table_args__
                self.registry.models[model_name]['constraints'] = self.registry.constrainthandler.deconstruct(val.fget(cls))
    
    def __getattr__(self, model : str) -> type[DeclarativeMeta]:

        cls = self.registry._create(model)

        def wrap(_cls : Any) -> type[DeclarativeMeta]:
            return _process_model(self, _cls)
        
        if cls is None:
            return wrap

        return wrap(cls)
    
    @staticmethod
    def _dispatch_strategy(settings : type[_SchemaSettings]) -> type[TransferStrategy]:
        """
        Dispatch the appropriate strategy type based on the passed settings.

        Parameters
        ----------
        settings : type[_SchemaSettings]
            Child of `_SchemaSettings` which will return a mapped child instance
            of `TransferStrategy`.
        
        Returns
        -------
        type[TransferStrategy]
            Child of `TransferStrategy` corresponding to the input 
            `_SchemaSettings` variant.
        """

        match settings:
            case DictionarySettings():
                return DictionaryTransferStrategy
            case YAMLFileSettings():
                return YAMLFileTransferStrategy
            case DatabaseSettings():
                return DatabaseTransferStrategy
            case _:
                return settings.transfer_strategy

    def load(self, settings : type[_SchemaSettings], models : list[str] | None = None) -> Self:
        """
        Loads abstract ORM instances associated with the current schema.

        Parameters
        ----------
        settings : type[_SchemaSettings]
            Settings object containing necessary key-value pairs to access the 
            appropriate TransferStrategy.load() method.
        models : list[str], optional
            List of specific models to load from the schema definition source.
            If None, all models associated with the schema are loaded. Default 
            is None.

        Returns
        -------
        self
            Returns the self instance, with modified registry attribute to 
            contain plain-text definitions of each model, AND each abstract 
            ORM instance as an attribute of self.
        """

        transfer_strat = self._dispatch_strategy(settings)

        self = transfer_strat.load(self, settings, models)

        return self

    def write(self, settings : type[_SchemaSettings], models : list[str] | None = None) -> None:
        """
        Writes abstract ORM instances associated with the current schema to the 
        desired format.

        Parameters
        ----------
        settings : type[_SchemaSettings]
            Settings object containing necessary key-value pairs to access the 
            appropriate TransferStrategy.write() method.
        models : list[str], optional
            List of specific models to write to the schema definition source.
            If None, all models associated with the schema are written. Default 
            is None.
        """

        transfer_strat = self._dispatch_strategy(settings)

        transfer_strat.write(settings, models)

# ==============================================================================

class TransferStrategy(ABC):
    """
    Abstract base class to define the necessary format of a class responsible 
    for loading & writing a schema to or from a plain-text format. Children of 
    TransferStrategy correspond to different formats.

    Methods
    -------
    load
        Generic method to load a series of abstract ORM instances into a Schema 
        object from a plain-text format.
    write
        Generic method to write a series of abstract ORM instances contained in 
        a Schema object to a plain-text format.
    """

    @abstractmethod
    def load(schema : Schema, settings : type[_SchemaSettings], models : list[str] | None = None) -> Schema:
        """Abstract method to load a schema from an ambiguous source."""

        ...

    @abstractmethod
    def write(schema : Schema, settings : type[_SchemaSettings], models : list[str] | None = None) -> None:
        """Abstract method to write a schema to an ambiguous source."""
        
        ...


class DictionaryTransferStrategy(TransferStrategy):
    """
    "Transfer strategy" to load and write `Schema` objects (containing models,
    columns, & constraints) to/from a Python dictionary.

    Methods
    -------
    load
        Method to load abstract ORM instances (models) from a Python dictionary.
    write
        Method to write abstract ORM instances (models) to a Python dictionary.
    """

    def load(
        schema : Schema,
        settings : DictionarySettings,
        models : list[str] | None = None
    ) -> Schema:
        """
        Method to load abstract ORM instances (models) from a Python dictionary.
        
        Parameters
        ----------

        Returns
        -------
        """

        schema_dict = settings.dictionary[schema.name]

        if not schema.description:
            schema.description = schema_dict['description']
        
        if not models:
            models = list(schema_dict['models'].keys())

        # Add column and model dictionary to Schema registry object
        schema.registry.columns = schema_dict['columns']
        schema.registry.models  = schema_dict['models']

        return schema

    def write(
        schema : Schema,
        settings : DictionarySettings,
        models : list[str] | None = None
    ) -> dict[str, dict]:
        """
        Method to write abstract ORM instances (models) to a Python dictionary.
        
        Parameters
        ----------

        Returns
        -------
        """

        pass


class YAMLFileTransferStrategy(TransferStrategy):
    """
    "Transfer strategy" to load and write `Schema` objects (containing models,
    columns, & constraints) to/from a YAML File.

    Methods
    -------
    load
        Method to load abstract ORM instances (models) from a YAML file.
    write
        Method to write abstract ORM instances (models) to a YAML file.
    """
    
    def load(
        schema : Schema,
        settings : YAMLFileSettings, *,
        models : list[str] | None = None
    ) -> Schema:
        """
        Method to load abstract ORM instances (models) from a YAML file.
        """

        pass

    def write(
        schema : Schema,
        settings : YAMLFileSettings, *,
        models : list[str] | None = None
    ) -> TextIO:
        """
        Method to write abstract ORM instances (models) to a YAML file.
        """

        pass


class DatabaseTransferStrategy(TransferStrategy):
    """
    "Transfer strategy" to load and write `Schema` objects (containing models,
    columns, & constraints) to/from a relational database tables.

    Methods
    -------
    load
        Method to load abstract ORM instances (models) from database tables.
    write
        Method to write abstract ORM instances (models) to database tables.
    """

    def load(
        schema : Schema,
        settings : DatabaseSettings, *,
        models : list[str] | None = None
    ) -> Schema:
        """
        Method to load abstract ORM instances (models) from database tables.

        Parameters
        ----------
        schema : Schema
            The schema object, with a name defined, to load ORM instances into.
        settings : DatabaseSettings
            Child of _SchemaSettings object with various settings specific to 
            using `DatabaseTransferStrategy` defined as key-value pairs.
        models : list[str], optional
            List of model names to specifically load. If None, all models 
            associated with the schema found in the database are loaded. Default 
            is None.
        """

        pass

    def write(
        schema : Schema,
        settings : DatabaseSettings, *,
        models : list[str] | None = None
    ) -> None:
        """
        Method to write abstract ORM instances (models) to database tables.

        Parameters
        ----------
        schema : Schema
            The schema object, with a name defined, to write ORM instances from.
        settings : DatabaseSettings
            Child of _SchemaSettings object with various settings specific to 
            using `DatabaseTransferStrategy` defined as key-value pairs.
        models : list[str], optional
            List of model names to specifically write. If None, all models 
            associated with the schema found in the Schema object are written. 
            Default is None.
        """

        pass

# ==============================================================================

def _process_model(schema : Schema, cls : Any) -> type[DeclarativeMeta]:

    parents = (*schema.mixins, schema.base, )

    __table_args__ = ()
    if hasattr(cls, '__table_args__'):
        __table_args__ = declared_attr(lambda _: cls.__table_args__)
    else:
        __table_args__ = schema.registry.constrainthandler.construct(cls.constraints)

    _cls = type(
        cls.__name__, parents, {
            '__abstract__' : True,
            '__table_args__' : __table_args__,
            **cls.columns
        }
    )

    return _cls
