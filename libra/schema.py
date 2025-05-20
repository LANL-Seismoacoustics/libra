"""
Brady Spears
5/5/25

Contains the `Schema` object, which is the primary object for containing 
abstract ORM instances, A.K.A "Models". "Models" within the `Schema` object can 
then be mapped to relational database tables in your SQL backend by assigning 
the respective model a '__tablename__' attribute. Libra's `Schema` object 
relies on SQLAlchemy's declarative base class, which is applied directly to all
models belonging to a `Schema` object. The declarative base class, by default, 
inherits functionality from Libra's `MetaClass` object, but can be augmented 
with any custom metaclass implementation. Model behavior can be further 
augmented through "mix-in" classes, which are passed to a `Schema` object's 
models and are designed to add specialized functionality to ORM instances.

The `Schema` object can load and write models to/from various text-based 
formats. Libra supports three built-in options, herein referred to as "Transfer
Strategies," which must, by definition, have a 'load()' and 'write()' method 
defined. The three built-in transfer strategies include loading models from 
Python dictionaries, from a correctly-formatted YAML file, or from a particular 
set of database tables. Functionality is provided for the construction of 
custom transfer strategy objects, should the user want their models constructed
or deconstructed to/from a different format.
"""

# ==============================================================================

from __future__ import annotations
import os
import ast
from copy import deepcopy
from abc import ABC, abstractmethod
from typing import Any, Self, TextIO

import yaml
import sqlalchemy
from sqlalchemy import inspect
from sqlalchemy import create_engine, and_
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.ext.declarative import declared_attr
from pydantic_settings import BaseSettings, SettingsConfigDict

from libra.metaclass import MetaClass
from libra.util import (
    ColumnHandler, ConstraintHandler, TypeHandler, TypeMap
)
from libra.util.error import (
    SchemaNotFoundError,
    ModelNotFoundError,
    ColumnNotFoundError,
    TableNotFoundError
)

# ==============================================================================

LIBRA_YAML : os.PathLike = os.path.abspath('libra/schemas/libra.yaml')

# ==============================================================================

class SchemaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix = 'libra_')

class DictionarySettings(SchemaSettings):
    # Python dictionary containing schema description information
    dictionary : dict[str, dict | str] | None = None

class YAMLFileSettings(SchemaSettings):
    # Path to the YAML File containing schema description information
    file : str | os.PathLike | None = None

class DatabaseSettings(SchemaSettings):
    # Database connection string
    connection_str : str | None = None

    # Models required for Libra to run & their associated tablenames
    libra_model_tablenames : dict[str, str] | None = {
        'schemadescript'     : 'schemadescript',
        'modeldescript'      : 'modeldescript',
        'columnassoc'        : 'columnassoc',
        'columndescript'     : 'columndescript',
        'constraintdescript' : 'constraintdescript'
    }

    namespace : str | None = None # A.K.A. table owner or "schema" ('otheruser.tablename') 
    prefix :    str | None = None # Prefix for all tables created ('custom_tablename')
    suffix :    str | None = None # Suffix for all tables created ('tablename_custom')

# ==============================================================================

class Schema:
    
    def __init__(self, name : str, *, 
        metaclass : type[DeclarativeMeta] = MetaClass,
        mixins : tuple[type[DeclarativeMeta]] | None = None,
        typemap : TypeMap = TypeMap()
        ) -> None:

        # Name of the Schema
        self.name = name

        # SQLALchemy Declarative Base Class
        self.base = declarative_base(metaclass = metaclass)
        
        # Handling Mixin Classes (augment declarative base instances)
        if not mixins:
            mixins = ()
        self.mixins = mixins
        
        self.description = None
        self.models = []

        # Set various handlers
        self.typemap = typemap
        self.typehandler = TypeHandler(self.typemap)
        self.columnhandler = ColumnHandler(self.typehandler)
        self.constrainthandler = ConstraintHandler()
    
    def model_names(self):
        return [model_name for model_name in self.models]

    def list_models(self):
        return [getattr(self, name) for name in self.model_names()]

    def items(self):
        return zip(self.model_names(), self.list_models())

    def add_model(self, cls : type[DeclarativeMeta]) -> None:

        if cls.__name__ in self.models:
            raise AttributeError(f'Model \'{cls.__name__}\' already exists in schema.')
        
        def wrap(_cls : Any) -> type[DeclarativeMeta]:
            return _process_model(self, _cls)
        
        if cls is None:
            return wrap

        setattr(self, cls.__name__, wrap(cls))

        self.models.append(cls.__name__)

    def remove_model(self, model_name : str) -> None:
        try:
            delattr(self, model_name)
            self.models.remove(model_name)

        except AttributeError as e:
            return f'Model {model_name} not associated with {self.name}. {e}'

    # ==========================================================================

    def assign_tablenames(self, *, 
        namespace : str | None = None,
        prefix : str | None = None,
        suffix : str | None = None,
        **name_mapping : dict[str, str] | None
    ) -> None:
        
        if not namespace:
            namespace = ''
        else:
            namespace = f'{namespace}.'

        if not prefix:
            prefix = ''
        if not suffix:
            suffix = ''

        for model in self.models:

            # Model is defined in tablename map; only use namespace
            if model in name_mapping.keys():
                tablename = f'{namespace}{name_mapping[model]}'
            
            # Model is not in tablename map; construct using prefix/suffix
            else:
                tablename = f'{namespace}{prefix}{model}{suffix}'

            # Build model constraints here; append on to __table_args__
            constraints = []
            _constraint_dict = getattr(self, model)._constraintbuild
            for _condictionary in _constraint_dict:
                _contype, _condict = list(_condictionary)[0], list(_condictionary.values())[0]

                constraints.append(self.constrainthandler.construct(tablename, _contype, _condict))

            getattr(self, model).__table_args__ = tuple(constraints)
            
            setattr(self, model, type(model, (getattr(self, model),), {'__tablename__' : tablename}))

    # ==========================================================================

    @staticmethod
    def _dispatch_strategy(settings : type[SchemaSettings]) -> type[TransferStrategy]:
        """
        Dispatch the appropriate strategy type based on the passed settings. 

        Parameters
        ----------
        settings : type[SchemaSettings]
            Child of SchemaSettings, which is itself a child of Pydantic's 
            BaseSettings object, where settings are specified as key-value 
            pairs. The type of the SchemaSettings object will determine which 
            strategy is returned. Three children of SchemaSettings are 
            supported (DictionarySettings, YAMLFileSettings, DatabaseSettings) 
            and map appropriately a TransferStrategy. Unsupported children of 
            SchemaSettings require a 'transfer_strategy' parameter to be defined
            within the object that points to an appropriately-mapped child of 
            TransferStrategy.
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
    
    def load(self, 
        settings : type[SchemaSettings], 
        models : list[str] | None = None
        ) -> Self:
        """
        Loads all abstract ORM instances (models) associated with the current 
        schema.

        Parameters
        ----------
        """

        transfer_strat = self._dispatch_strategy(settings)

        self = transfer_strat.load(self, settings, models)

        return self

    def write(self,
        settings : type[SchemaSettings],
        models : list[str] | None = None
        ) -> None:
        """
        Writes all abstract ORM instances (models) in the associated schema to 
        the appropriate type. 

        Parameters
        ----------
        """

        transfer_strat = self._dispatch_strategy(settings)

        self = transfer_strat.write(settings, models)

        return self

# ==============================================================================

class TransferStrategy(ABC):
    
    @abstractmethod
    def load(schema : Schema, settings : type[SchemaSettings], models : list[str] | None = None) -> Schema:
        """Loads models into a Schema object"""
        ...

    @abstractmethod
    def write(schema : Schema, settings : type[SchemaSettings], models : list[str] | None = None) -> None:
        """Writes models, columns, & constraints from Schema object"""
        ...

class DictionaryTransferStrategy(TransferStrategy):
    """Built-in strategy to load/write schemas to/from a Python dictionary"""

    def load(
        schema : Schema,
        settings : DictionarySettings,
        models : list[str] | None = None
    ) -> Schema:
        
        schema_dict = settings.dictionary[schema.name]

        if not schema.description:
            schema.description = schema_dict['description']
        
        if not models:
            models = list(schema_dict['models'].keys())

        for model in models:
            model_dict = schema_dict['models'][model]

            # Add columns to the model
            columns = {}
            for col in model_dict['columns']:
                col_name, coldef_dict = list(col.keys())[0], list(col.values())[0]

                coldef_dict.update(schema_dict['columns'][col_name])
                
                columns[col_name] = schema.columnhandler.construct(col_name, coldef_dict)
                
            constraints = model_dict['constraints']

            # Higher-level schema.make_model functions?? Utilizes Base & Mixin classes.
            _cls = type(model, (), {'constraints' : constraints, 'columns' : columns})
            
            schema.add_model(_cls)

        return schema
    
    def write(
        schema : Schema,
        settings : DictionarySettings,
        models : list[str] | None = None
    ) -> dict[str, str]:
        return NotImplementedError
    
class YAMLFileTransferStrategy(TransferStrategy):
    """Built-in strategy to load/write schemas to/from a YAML File"""

    @staticmethod
    def _open_yaml_file(settings : YAMLFileSettings) -> dict[str, str]:
        """Open a yaml file, return the contents as a Python dictionary"""

        if hasattr(settings, 'file'):
            with open(settings.file, 'r') as file:
                return yaml.safe_load(file)
        else:
            raise AttributeError('YAMLFileSettings object must have \'file\' defined as an attribute.')

    def load(
        schema : Schema,
        settings : YAMLFileSettings,
        models : list[str] | None = None
    ) -> Schema:
        
        yaml_dict = YAMLFileTransferStrategy._open_yaml_file(settings)

        settings = DictionarySettings(dictionary = yaml_dict)

        return DictionaryTransferStrategy.load(schema, settings, models)
    
    def write(
        schema : Schema,
        settings : YAMLFileSettings,
        models : list[str] | None = None
    ) -> TextIO:
        
        return NotImplementedError
    
class DatabaseTransferStrategy(TransferStrategy):
    """Built-in strategy to load/write schemas to/from database tables"""

    @staticmethod
    def _create_db_connection(settings : DatabaseSettings) -> Session:
        """Create database session object from a passed connection string"""

        if hasattr(settings, 'connection_str'):
            engine = create_engine(settings.connection_str)

            return Session(engine)
        else:
            raise AttributeError('DatabaseSettings object must have \'connection_str\' defined as an attribute.')
    
    @staticmethod
    def _create_db_tables(session : Session, settings : DatabaseSettings) -> None:
        pass

    def load(
        schema : Schema,
        settings : DatabaseSettings,
        models : list[str] | None = None
    ) -> Schema:
        # TODO: Handle errors in this code
        
        if not settings.libra_model_tablenames:
            settings.libra_model_tablenames = {}
        
        session = DatabaseTransferStrategy._create_db_connection(settings)

        # Create Models of the self-describing Libra Schema
        libra = Schema('Libra', typemap = schema.typemap).load(settings = YAMLFileSettings(file = LIBRA_YAML))
        libra.assign_tablenames(**settings.libra_model_tablenames)

        # Get the database tables
        Schemadescript     = libra.schemadescript
        Modeldescript      = libra.modeldescript
        Columndescript     = libra.columndescript
        Columnassoc        = libra.columnassoc
        Constraintdescript = libra.constraintdescript

        for key, val in libra.items():
            if not inspect(session.bind).has_table(val.__tablename__):
                raise TableNotFoundError(f'Table \'{val.__tablename__}\' not found in Database.')

        # Get Schema
        schemadescript = session.query(Schemadescript).filter(Schemadescript.schema_name == schema.name).first()

        # Get all models belonging to the schema if models are not explicitly called.
        if not models:
            models = [name[0] for name in list(session.query(Modeldescript.model_name).filter(Modeldescript.schema_name == schema.name))]

        # Set up the schema_dict which will be passed onto DictionaryTransferStrategy.load()
        schema_dict = {schema.name : {
            'description' : schemadescript.description,
            'columns' : {},
            'models' : {m : 
                {'description' : None,
                 'columns' : [],
                 'constraints' : []
                }
                for m in models}
            }
        }
        
        # Go grab the columndescripts and the columnassocs for each model
        for model_name in models:

            modeldescript = session.query(Modeldescript).filter(and_(
                Modeldescript.model_name == model_name,
                Modeldescript.schema_name == schema.name
            )).first()

            schema_dict[schema.name]['models']['description'] = modeldescript.description
            schema_dict[schema.name]['models'][model_name]['columns'] = []
            schema_dict[schema.name]['models'][model_name]['constraints'] = []

            colassoc_query = session.query(Columnassoc).filter(and_(
                Columnassoc.model_name == model_name,
                Columnassoc.schema_name == schema.name
            )).order_by(Columnassoc.column_position)

            condescript_query = session.query(Constraintdescript).filter(and_(
                Constraintdescript.model_name == model_name,
                Constraintdescript.schema_name == schema.name
            ))

            for colassoc in colassoc_query:
                coldescript = session.query(Columndescript).filter(and_(
                    Columndescript.column_name == colassoc.column_name,
                    Columndescript.schema_name == schema.name
                )).first()

                coldescript = coldescript.to_dict()
                colassoc = colassoc.to_dict()

                # Delete some unecessary administrative key-value pairs
                del colassoc['modauthor']; del colassoc['loadauthor']
                del colassoc['moddate']; del colassoc['loaddate']
                del coldescript['modauthor']; del coldescript['loadauthor']
                del coldescript['moddate']; del coldescript['loaddate']
                del colassoc['schema_name']; del coldescript['schema_name']
                del colassoc['column_position']

                model_name = colassoc['model_name']; del colassoc['model_name']; 
                column_name = colassoc['column_name']; del colassoc['column_name']; del coldescript['column_name']

                schema_dict[schema.name]['models'][model_name]['columns'].append({column_name : colassoc})
                # schema_dict[schema.name]['models'][model_name]['constraints'].append({})

                schema_dict[schema.name]['columns'][column_name] = coldescript
            
            for constraint in condescript_query:
                condescript = constraint.to_dict()

                con_type = condescript['constraint_type']
                columns  = condescript['columns']

                # Aggressive massaging of condescript based on type of key
                match con_type:
                    case 'pk':
                        schema_dict[schema.name]['models'][model_name]['constraints'].append({con_type : ast.literal_eval(columns)})
                    case 'uq':
                        schema_dict[schema.name]['models'][model_name]['constraints'].append({con_type : ast.literal_eval(columns)})

                    case _:
                        pass

                # schema_dict[schema.name]['models'][model_name]['constraints'].append({con_type : condescript})

        dict_settings = DictionarySettings(dictionary = schema_dict)

        return DictionaryTransferStrategy.load(schema, dict_settings, models)
    
    def write(
        schema : Schema,
        settings : DatabaseSettings,
        models : list[str] | None = None
    ) -> None:
        return NotImplementedError

# ==============================================================================

def _process_model(
    schema : Schema,
    cls : Any
) -> type[DeclarativeMeta]:

    parents = (schema.base, *schema.mixins, )

    # TODO: cls likely needs its own __table_args__ optional input. Constraints should be passed as an additional attribute to _cls
    try:
        __table_args__ = declared_attr(lambda _: cls.__table_args__)
    except AttributeError:
        __table_args__ = ()

    _cls = type(cls.__name__, parents, {'__abstract__' : True, '__table_args__' : __table_args__, '_constraintbuild' : cls.constraints, **cls.columns})
    
    return _cls
