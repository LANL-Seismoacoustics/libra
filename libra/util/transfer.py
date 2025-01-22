from __future__ import annotations
from abc import ABC, abstractmethod
import os
import importlib
from typing import Any
from typing import TYPE_CHECKING

import yaml
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import and_

if TYPE_CHECKING:
    from ..schema import Schema
from .errors import SchemaNotFoundError

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
        
        if not schema_dict.get(schema.name):
            return SchemaNotFoundError
        
        schema_dict = schema_dict[schema.name]

        for model, model_dict in schema_dict['models'].items():
            columns = {}
            for column in model_dict['columns']:
                columns[column] = schema.columnhandler().construct(
                    column, schema_dict['columns'][column]
                )
            
            del model_dict['columns']
            
            _cls = type(model, (), {**columns, **model_dict})

            schema.add_model(_cls)
        
        return schema
    
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
        
        with open(file, 'rb') as f:
            schema_dict = yaml.load(f, Loader = SchemaTransferYAML.yaml_loader())

        return SchemaTransferDict.load(schema, schema_dict, models = models)

    def write(
        schema : Schema
    ) -> None:
        return NotImplementedError

    @staticmethod
    def type_constructor(loader : yaml.SafeLoader, node : yaml.nodes.MappingNode) -> type[sqlalchemy.types]: # type: ignore
        """Constructs an sqlalchemy datatype object from a node passed within 
        the input YAML file. 

        Parameters
        ----------
        loader : object
        node : object

        Returns
        -------
        object
            Instance of subclass defined in sqlalchemy.types, or a child of an 
            SQLAlchemy datatype object.
        """

        def _type_call_parser(s : str) -> tuple[str, list[Any], dict[str, Any]]:
            args, kwargs = [], {}
            if '(' in s and ')' in s and (s.index('(') + 1 != s.index(')')):
                left, right = s.index('('), s.index(')')
                inputs = [i.replace(' ','') for i in s[left + 1:right].split(',')]
                _type_call = s[0:left]
                for param in inputs:
                    if '=' in param:
                        key, value = param.split('=')
                        kwargs[key] = value
                    else:
                        args.append(param)
            else:
                _type_call = s.replace('()', '')

            return _type_call, args, kwargs

        # TODO: Option to augment this with custom modules/types?
        modules = ['sqlalchemy']
        
        mod = importlib.import_module('sqlalchemy')

        _type_call, args, kwargs = _type_call_parser(node.value)

        return getattr(mod, _type_call)(*args, **kwargs)

    @staticmethod
    def yaml_loader() -> type[yaml.SafeLoader]:
        """Loader responsible for parsing YAML files."""

        loader = yaml.SafeLoader
        loader.add_constructor('!t', SchemaTransferYAML.type_constructor)

        return loader

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
        session : Session,
        colassoc : str,
        coldescript : str,
        tabdescript : str,
        models : str | list[str] | None = None
    ) -> Schema:
        from .doc import DOC

        # Necessary self-describing Schema Tables
        class Tabdescript(DOC.tabdescript): __tablename__ = tabdescript
        class Colassoc(DOC.colassoc): __tablename__ = colassoc
        class Coldescript(DOC.coldescript): __tablename__ = coldescript

        if not models:
            model_query = session.query(Tabdescript).filter(Tabdescript.schema_name == schema.name)
            models = [m.table_name for m in model_query]
        
        schema_dict, model_dict, column_dict = {}, {}, {}
        for model in models:
            colassoc_query = list(session.query(Colassoc).filter(and_(Colassoc.table_name == model, Colassoc.schema_name == schema.name)).order_by(Colassoc.column_position.asc()))

            
            model_dict[model] = {'columns' : []}
            for col in colassoc_query:
                column_def = session.query(Coldescript).filter(and_(
                    Coldescript.column_name == col.column_name,
                    Coldescript.schema_name == schema.name
                ))[0]

                coldict = column_def.to_dict()
                
                # Remove any non-needed arguments from coldict to construct column
                del coldict['column_name']; del coldict['schema_name']

                # Absorb kwargs column into dictionary
                if coldict.get('kwargs') is not None:
                    coldict.update(coldict['kwargs'])
                del coldict['kwargs']
                
                # Convert to sqlalchemy.Column object
                if column_dict.get(col.column_name) is None:
                    column_dict[col.column_name] = coldict

                # Append into models
                model_dict[model]['columns'].append(col.column_name)

                if col.column_type == 'primary':
                    if not model_dict[model].get('pk'):
                        model_dict[model]['pk'] = []
                    model_dict[model]['pk'].append(col.column_name)
                
                if col.column_type == 'unique':
                    if not model_dict[model].get('uc'):
                        model_dict[model]['uc'] = []
                    model_dict[model]['uc'].append(col.column_name)
            
        schema_dict = {
            schema.name : {
                'columns' : column_dict,
                'models' : model_dict
            }
        }

        return SchemaTransferDict.load(schema, schema_dict)

    def write(
        schema : Schema
    ) -> None:
        return NotImplementedError