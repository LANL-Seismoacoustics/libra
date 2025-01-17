from __future__ import annotations
import os
import pathlib
import yaml
import importlib
from ast import literal_eval
from abc import ABC, abstractmethod
from typing import TypedDict, Unpack
from typing import Any, Callable,Dict, List
from typing import Callable, Optional, Self, Tuple, Type, Union

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    PrimaryKeyConstraint, 
    UniqueConstraint
)
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeMeta, declarative_base
from sqlalchemy.ext.declarative import declared_attr

from .metaclass import LibraMetaClass
from .util.typing import _Mixin, _SQLType, _PreprocessedORM, _ProcessedORM
from .util.typing import SchemaLoadParams, SchemaWriteParams
from .util import ColumnHandler, Default_ColumnHandler
from .util import SchemaTransferStrategy
from .util import SchemaTransferDict, SchemaTransferYAML, SchemaTransferDB
from .util.errors import SchemaNotFoundError, ModelNotFoundError, ColumnNotFoundError

# ==============================================================================

class Schema:
    """The Schema object contains all information necessary to dynamically 
    construct abstract ORM instances, A.K.A "Models" which belong to a Schema.

    A Schema contains abstract object-relation-mapped instances, sometimes 
    referred to as 'models' that represent the structure of a table in a 
    relational database, including columns and the various primary, unique, and
    foreign keys associated with that table. Construction of these models is 
    reliant on the declarative mapping functionality of SQLAlchemy, and can be
    extended with a __tablename__ attribute to cast them as proper SQLAlchemy 
    ORM Table objects, which can be manipulated in the Python OOP environment 
    and, via SQLAlchemy, those manipulations are reflected in the relational 
    database environment.

    Note
    ----
        A 'Schema' in Libra's context (and other relational database backends) 
        refers to a contained set of database tables that are related to one 
        another. It is important to note that in some backends, a 'Schema' is 
        fundamentally equivalent to the 'owner' of a set of database tables - 
        this is not necessarily the case in Libra's definition of a Schema.

    Attributes
    ----------
    name : str
        Required name of the associated Schema
    base : sqlalchemy.orm.DeclarativeMeta or subclass, optional
        Declarative metaclass from which all models in the Schema object will 
        inherit (default is a DeclarativeMeta object inheriting from the 
        built-in libra.metaclass.LibraMetaClass).
    mixins : tuple of libra.util.mixin or subclass, optional
        Class defining custom methods in addition to those defined in the 
        metaclass contained in 'base' that are attributed to all models within 
        the associated Schema object (default is a tuple of #TODO)
    columnhandler : libra.util.columnhandler or subclass, optional
        Subclass of the ColumnHandler object, which defines specific methods to
        construct or deconstruct an SQLAlchemy Column object (default is the 
        built-in Default_ColumnHandler object).
    type_map : dict, optional
        Passed on to the columnhandler object to map SQLAlchemy datatype objects 
        to other SQLAlchemy datatype objects - useful in the case that 
        SQLAlchemy's 'CamelCase' datatypes do not automatically map to the 
        desired or backend-specific datatype (default is None).
        For more info on SQLAlchemy's Datatypes:
        https://docs.sqlalchemy.org/en/20/core/types.html

    Methods
    -------
    load(self, **kwargs)
        Reads in schema metadata from one of several built-in metadata resources 
        or a custom-built resource and constructs abstract ORM instances from 
        those resources, adding them as additional attributes of the Schema 
        object.
    write(self, **kwargs)
        Writes schema metadata from the Schema object to one of several built-in
        metadata resources or a custom-built resource.
    add_model(self, _cls)
        Adds an abstract ORM instance (model) to the Schema object.

    Examples
    --------
    # TODO: Add Schema Examples
    """

    def __init__(self, 
        name : str, *, 
        base : type[DeclarativeMeta] | None = None,
        mixins : type[_Mixin] | tuple[type[_Mixin]] | None = None,
        columnhandler : type[ColumnHandler] = Default_ColumnHandler,
        type_map : dict[type[_SQLType], type[_SQLType]] | None = None
        ) -> None:

        self.name = name

        self.columnhandler = columnhandler
        if type_map:
            setattr(self.columnhandler, 'type_map', type_map)

        # Use default LibraMetaClass if not user-defined
        if not base:
            self.base = declarative_base(metaclass = LibraMetaClass, constructor = None)
        else:
            self.base = base

        # Clean up mixins input (passed as str | tuple[str] | None)
        if not mixins:
            mixins = ()
        
        if not isinstance(mixins, tuple):
            mixins = (mixins, )
        
        self.mixins = mixins

    def __repr__(self) -> str:
        return f'Schema(\'{self.name}\')'

    def load(self, **kwargs : Unpack[SchemaLoadParams]) -> Self:
        """Loads abstract ORM instances (models) from several built-in or 
        custom-defined metadata resource formats and adds those models as 
        attributes of self.

        Parameters
        ----------
        **kwargs : SchemaLoadParams
            TypedDict of load method keywords passed onto the _direct_params()
            static method defined below.
        
        Returns
        -------
        self
            Instance of Schema-self where models are encoded as attributes of 
            the self.

        Examples
        --------
        To load from a Python dictionary:
        >>> Schema('MySchema').load(schema_dict = mydict)

        To load from a YAML file:
        >>> Schema('My Schema').load(file = '/path/to/file.yml')

        To load from database tables:
        >>> Schema('My Schema').load(session = Session('sqlite://mydb.db')

        To load specific model(s) from a schema from any of these methods, add
        the 'models' keyword:
        >>> Schema('My Schema').load(file = 'schema.yml', models = 'my_model')
        >>> Schema('My Schema').load(schema_dict = mydict, \
            models = ['my_model1', 'my_model2'])
        """
        
        strategy = self._direct_params(**kwargs)

        if kwargs.get('strategy'):
            del kwargs['strategy']

        self = strategy.load(schema = self, **kwargs)

        return self

    def write(self, **kwargs : Unpack[SchemaWriteParams]) -> None:
        """Writes metadata contained in Schema-self instance to one of several 
        built-in or custom-defined metadata resource formats.
        
        Parameters
        ----------
        **kwargs : SchemaWriteParams
            TypedDict of write method keywords passed onto the _direct_params()
            static method defined below.
        
        Examples
        --------
        # TODO: Schema.write() examples
        """

        strategy = self._direct_params(**kwargs)

        if kwargs.get('strategy'):
            del kwargs['strategy']
        
        self.strategy.write(schema = self, **kwargs)
    
    def add_model(self, cls : _PreprocessedORM) -> None:
        """Adds an abstract ORM instance defined in _cls to the current Schema.

        The add_model() method receives an arbitrary, yet properly-formatted 
        class, re-casts it using the Schema._process_orm() function, and adds 
        it to self.

        Note
        ----
        The resultant model will be added as an attribute of self.

        Parameters
        ----------
        cls : object
            Properly-formatted arbitrary class defining the structure of a 
            desired abstract ORM instance. The add_model method references 
            the self's 'base' property and any 'mixin' classes to re-cast the 
            input class as a child of 'base' and any 'mixin' classes.

        Example
        -------
        >>> from sqlalchemy import Column
        >>> from sqlalchemy import DateTime, Integer, String
        >>>
        >>> from libra import Schema
        >>>
        >>> myschema = Schema('My Schema')
        >>>
        >>> @myschema.add_model
        >>> class Person:
        >>>     personid     : Column(Integer, primary_key = True)
        >>>     first_name   : Column(String(30))
        >>>     last_name    : Column(String(30))
        >>>     email        : Column(String(50))
        >>>     user_created : Column(DateTime)
        """

        # TODO: type[DeclarativeMeta] is not proper output should be type[sqlalchemy.]
        def wrap(_cls : _PreprocessedORM) -> type[DeclarativeMeta]:
            return process_model(_cls, self.base, self.mixins)
        
        if cls is None:
            return wrap
        
        setattr(self, cls.__name__, wrap(cls))

    def remove_model(self, model : str) -> None:
        """TODO: Remove a model from the schema"""
        return NotImplementedError
    
    @staticmethod
    def _direct_params(**kwargs : Unpack[SchemaLoadParams | Unpack[SchemaWriteParams]]) -> type[SchemaTransferStrategy]:
        """Returns the appropriate SchemaTransferStrategy subclass based on the 
        passed keyword arguments. 

        Keyword-to-SchemaTransferStrategy subclass are as follows:
            - 'strategy'    -> custom subclass of SchemaTransferStrategy
            - 'session'     -> SchemaTransferDB
            - 'file'        -> SchemaTransferYAML
            - 'schema_dict' -> SchemaTransferDict

        Parameters
        ----------
        **kwargs : SchemaLoadParams | SchemaWriteParams
            One of two separate TypedDicts, where SchemaLoadParams contains:
                - schema : Schema, required
                - models : str | list[str] | None, optional
                - file : str | os.PathLike | None, optional
                - session : sqlalchemy.orm.Session | libra.Session | None, 
                    optional
                - strategy : type[SchemaTransferStrategy] | None, optional
            And SchemaWriteParams contains:
                # TODO: Define SchemaWriteParams
        
        Returns
        -------
        type[SchemaTransferStrategy]
            Subclass of abstract base class SchemaTransferStrategy with 
            defined load and write methods.
        
        Raises
        ------
        NotImplementedError
            If a passed keyword argument does not map to a built-in 
            SchemaTransferStrategy subclass.
        """

        if kwargs.get('strategy'):
            return kwargs['strategy']
        
        if kwargs.get('session'):
            return SchemaTransferDB
        
        if kwargs.get('file'):
            if pathlib.Path(kwargs['file']).suffix == '.yaml':
                return SchemaTransferYAML
        
        if kwargs.get('schema_dict'):
            return SchemaTransferDict
        
        raise NotImplementedError('Schema transfer method not supported.')

# ==============================================================================

def process_model(cls : _PreprocessedORM,
        base : type[DeclarativeMeta] | None = None, #TODO: Not of type[DeclarativeMeta]
        mixins : tuple[type[_Mixin]] | None = None
        ) -> _ProcessedORM:
    """Processes an arbitrary class defining the structure of an abstract ORM 
    (AKA an SQL table without a concrete tablename), and returns the abstract 
    ORM as the child of the appropriate DeclarativeMeta superclass and any 
    declared Mixin classes. Primary keys, unique constraints, and foreign keys 
    are also cast properly here. 

    Parameters
    ----------
    cls : object
        Properly-fromatted arbitrary class defining the structure of a 
        desired abstract ORM instance. Will be recast to the output object 
        as a subclass inheriting primarily from input base and secondarily 
        from input mixins.
    base : object
        Metaclass inheriting from DeclarativeMeta. Input cls will be re-cast as 
        a new object inheriting from base.
    mixins : tuple
        Tuple containing mixin classes. Input cls, re-cast using input base, 
        will secondarily inherit from all classes contained in this mixins 
        input.
    
    Returns
    -------
    object
        Class re-cast to inherit from input base and mixin classes with primary 
        keys, unique keys, and foreign keys cast to the SQLAlchemy ORM model 
        properly.
    
    Examples
    --------
    #TODO: Provide Examples
    """

    if not base:
        base = declarative_base(metaclass = LibraMetaClass)

    if not mixins:
        mixins = ()

    parents = (base, *mixins, )

    all_constraints = {
        'cc' : CheckConstraint,
        'fk' : ForeignKeyConstraint,
        'pk' : PrimaryKeyConstraint,
        'uc' : UniqueConstraint
    }

    orm_constraint = []
    for k in all_constraints.keys():
        _con = cls.__dict__.get(k, None)
        if _con:
            if type(_con) == dict:
                _args = _con['columns']; del _con['columns']
            elif type(_con) == list:
                _args = _con; _con = {}
            orm_constraint.append(all_constraints[k](*_args, **_con))
            delattr(cls, k)
    
    __table_args__ = tuple(orm_constraint)
    
    _cls = type(
        cls.__name__, 
        parents,
        {
            '__abstract__' : True, 
            '__table_args__' : __table_args__,
            **{col : val for col, val in cls.__dict__.items() if col != '__dict__'}
        }
    )

    return _cls
