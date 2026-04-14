"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Contains the `Schema` object, which is the container for abstract-relation-
mapped (ORM) instances. These 'models' can then be derived from, adding a 
'__tablename__' attribute, which will appropriately map back to the table in 
your SQL backend.
"""

# ==============================================================================

from __future__ import annotations

import pdb
import os
import ast
import copy
import warnings
from importlib import resources
from importlib.resources.abc import Traversable
from functools import singledispatch
from abc import ABC, abstractmethod
from typing import (
    Any,
    Self,
    TypeVar
)

import yaml
import sqlalchemy
import sqlalchemy.dialects
import sqlalchemy.dialects.oracle
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import (
    declarative_base,
    DeclarativeBase, 
    DeclarativeMeta
)

from .ext import (
    FlatFileMixin,
    PandasMixin,
    QCMixin
)
from .metaclass import LibraMetaClass
from .registry import Registry, _UnbasedClass
from .util import (
    TypeMap,
    DatabaseSettings, 
    SchemaSchemaSettings
)
from .util import (
    StrategyUnsupported,
    SchemaNotFoundError,
    ModelNotFoundError,
    BackendUnsupported
)

# ==============================================================================

ModelMixin = TypeVar('ModelMixin')

# ==============================================================================

class Schema:
    """
    The Schema class contains attributes and methods needed to serialize & 
    deserialize abstract SQLAlchemy ORM Table instances, including their 
    associated columns and constraints. All abstract Table instances (models) 
    inherit from a common SQLAlchemy Declarative Base class, which is 
    inherent to a Schema object. In addition, all models will also inherit 
    from any mix-in classes defined in the instantiation of the Schema object.

    Attributes
    ----------
    name : str
        Required identifying name of the schema
    description : str | None
        Description of the associated schema
    _registry : libra.Registry
        Libra Registry object responsible for caching serialized model and 
        column definitions and dynamically creating unbased classes which 
        ultimately become abstract sqlalchemy.Table instances
    _model_cache : dict[str, type[DeclarativeBase]]
        Cache dictionary to map lazily-loaded abstract Table instances to their
        appropriate model names. Models are assigned as they are constructed
        and _model_cache is responsible for storing them.
    mixins : tuple[ModelMixin]
        Tuple of classes that deserialized models will inherit from in addition 
        to the metaclass defined above. Mixin classes are intended to add 
        additional parameters or functionality to models
    base : DeclarativeBase
        SQLAlchemy DeclarativeBase class instance applied to all SQLAlchemy 
        abstract Table instances belonging to a Schema upon deserialization.
    """
    
    def __init__(
        self,
        name : str, *,
        description : str | None = None,
        metaclass : type[DeclarativeMeta] = LibraMetaClass,
        typemap : TypeMap | None = None,
        mixins : tuple[ModelMixin] | None = None
    ) -> None:
        """
        Construct a Schema instance.

        Parameters
        ----------
        name : str
            Required identifying name of the schema
        description : str, Optional
            Description of the associated schema; default is None
        metaclass : type[DeclarativeMeta], Optional
            Metaclass passed to SQLAlchemy's orm.declarative_base() function. 
            Default is Libra's custom metaclass instance.
        typemap : type[TypeMap], Optional
            Libra TypeMap instance to override default SQLAlchemy type objects 
            during serialization/deserialization of model instances. Default is 
            a new, untouched TypeMap object.
        mixins : tuple[ModelMixin], Optional
            Tuple of classes that deserialized models will inherit from in addition 
            to the metaclass defined above. Mixin classes are intended to add 
            additional parameters or functionality to models. Default is None.
        """
        
        self.name = name
        self.description = description

        if not typemap:
            typemap = TypeMap()

        # Construct a Registry object
        self._registry = Registry(typemap)

        # Assign Mixins if they exist
        self.mixins = tuple(mixins) if mixins else (FlatFileMixin, PandasMixin, QCMixin, )

        # Initialize SQLAlchemy Declarative Base
        self.base : DeclarativeBase = declarative_base(metaclass = metaclass)

        # Place to cache lazily-loaded models
        self._model_cache : dict[str, type[DeclarativeBase]] = {}

    def __repr__(self) -> str:
        return f'Schema(\'{self.name}\')'
    
    def __getattr__(self, name : str) -> type[DeclarativeBase]:
        """
        Return the SQLAlchemy abstract Table instance for a given model by 
        consulting the Schema's _registry attribute and constructing it if it 
        hasn't been cached already.

        Parameters
        ----------
        name : str
            Model name as defined in the Schema's _registry attribute. Or other 
            attribute of self.
        
        Returns
        -------
        type[DeclarativeBase]
            Child of SQLAlchemy DeclarativeBase class, representing an abstract 
            SQLAlchemy Table instance (abstract because it doesn't have a 
            __tablename__ attribute assigned yet)
        
        Raises
        ------
        libra.util.ModelNotFoundError
            Raised if the provided model name does not exist in the _registry 
            attribute.
        """

        # Check existing attributes (._registry, .typemap, .mixins, etc.)
        if name in self.__dict__:
            return self.__dict__[name]
        
        # If not found, assume looking for model name
        if name not in self._registry.models:
            raise ModelNotFoundError(f'Schema has no model \'{name}\'.')

        # Check for lazily-loaded model
        if name in self._model_cache:
            return self._model_cache[name]
        
        # If not found, build unbased class
        unbased = self._registry._create(name)

        # Process to SQLAlchemy class
        model_cls = _process_model(self, unbased)

        # Cache it
        self._model_cache[name] = model_cls
        
        return model_cls
        
    def load(self, source : Any) -> Self:
        """
        Load a schema definition format.

        Parameters
        ----------
        source : Any
            Source to load a schema definition from. Libra natively accepts:
            - Python dictionaries
            - Strings or os.PathLike objects, with '.yml' or '.yaml' extension
            - libra.util.DatabaseSettings object
            - libra.util.SchemaSchemaSettings object
        
        Returns
        -------
        Self
            An instance of Schema with _registry populated to contain the loaded
            schema definitions. Attributes corresponding to each model in the 
            _registry attribute's model dictionary are also added to the 
            instance of self. When called, these attributes deserialize the 
            information contained in _registry into an abstract SQLAlchemy 
            Table instance.
        """

        _transfer_strat = _resolve_load_strategy(source)

        self = _transfer_strat.load_from(self, source)

        return self

    def dump(self, target : Any = None) -> Any:
        """
        Dump a serialized schema definition.

        Parameters
        ----------
        target : Any
            Target to a dump a serialized schema. Libra natively supports:
            - Python dictionaries
            - Strings or os.PathLike objects with '.yml' or '.yaml' extensions
            - libra.util.DatabaseSettings object
            - libra.util.SchemaSchemaSettings object
        
        Returns
        -------
        Any
        """

        _transfer_strat = _resolve_dump_strategy(target)

        return _transfer_strat.dump_into(self, target)

# ==============================================================================
# TransferStrat Abstract Base Class

class TransferStrat(ABC): 
    """Abstract Transer Strategy class to load & dump schema definitions"""

    @staticmethod
    @abstractmethod
    def load_from(schema : Schema, source : Any) -> None:
        ...
    
    @staticmethod
    @abstractmethod
    def dump_into(schema : Schema, target : Any) -> Any:
        ...
    
# ==============================================================================
# Dictionary Transfer Strategy

class DictTransferStrat(TransferStrat):
    """
    TransferStrategy subclass to load and dump schema definitions to/from a 
    Python dictionary.
    """
    
    @staticmethod
    def load_from(schema : Schema, schemadict : dict[str, Any]) -> Schema:
        """
        Load schema definitions from a Python dictionary

        Parameters
        ----------
        schema : Schema
            Initialized Libra Schema object with a specified name attribute.
        schemadict : dict[str, Any]
            Dictionary containing populated schema definitions
        
        Returns
        -------
        schema : Schema
            The same input Schema object, with an updated _registry object to 
            reflect information contained within the input schemadict. 
        """

        if not isinstance(schemadict, dict):
            raise TypeError(f'Expected dictionary, got {type(schemadict)}')
        
        if schema.name not in schemadict:
            raise SchemaNotFoundError(f'Schema \'{schema.name}\' not found in the provided dictionary.')
        
        schema_block = schemadict[schema.name]

        if not isinstance(schema_block, dict):
            raise TypeError(f'Schema definition for \'{schema.name}\' must be a dictionary.')
        
        # Clear any previous Registry state & schema attributes
        schema._registry.clear()
        schema._model_cache.clear()

        schema.description = schema_block.get('description', None) # Override any existing description

        # ---------------
        # Extract Columns
        # ---------------

        columns_block = schema_block.get('columns', {})
        if not isinstance(columns_block, dict):
            raise TypeError('\'columns\' key of schema dictionary must be a dictionary.')
        
        for column_name, column_def in columns_block.items():
            if not isinstance(column_def, dict):
                raise TypeError(f'Column definition for \'{column_name}\' must be a dictionary.')

            schema._registry.register_column(column_name, column_def)
        
        # --------------
        # Extract Models
        # --------------

        models_block = schema_block.get('models', {})
        if not isinstance(models_block, dict):
            raise TypeError('\'models\' key of schema dictionary must be a dictionary.')
        
        for model_name, model_def in models_block.items():
            if not isinstance(model_def, dict):
                raise TypeError(f'Model definition for \'{model_name}\' must be a dictionary.')
            
            schema._registry.register_model(model_name, model_def)
        
        return schema
    
    @staticmethod
    def dump_into(schema : Schema, target : Any = None) -> dict[str, Any]:
        """
        Dump schema definitions from a Schema into a Python Dictionary.

        Parameters
        ----------
        schema : Schema
            Initialized Libra Schema object with a specified name attribute and 
            populated _registry attribute.
        
        Returns
        -------
        dict[str, Any]
            Python dictionary containing serialized schema definitions
        """

        registry = schema._registry

        schemadict : dict[str, Any] = {
            schema.name : {
                'description' : schema.description,
                'columns'     : copy.deepcopy(registry.columns),
                'models'      : copy.deepcopy(registry.models)
            }
        }

        return schemadict

# ==============================================================================
# YAML File Transfer Strategy

class YAMLTransferStrat(TransferStrat):

    @staticmethod
    def load_from(schema : Schema, file : str | os.PathLike) -> Schema:
        """
        Load schema definitions from a correctly-formatted YAML file.

        Parameters
        ----------
        schema : Schema
            Initialized Libra Schema object with a specified name attribute.
        file : str | os.PathLike
            YAML file containing schema definitions. When loaded in, the YAML 
            file should reflect a dictionary structure compatible with 
            DictTransferStrat.
        
        Returns
        -------
        schema : Schema
            The same input Schema object, with an updated _registry object to 
            reflect information contained within the input YAML file.
        """
        
        if isinstance(file, Traversable):
            with file.open('r', encoding = 'utf-8') as f:
                data = yaml.safe_load(f)
        else:
            path = os.fspath(file)

            if not os.path.exists(path):
                raise FileNotFoundError(f'No such file : \'{path}\'')

            with open(path, 'r', encoding = 'utf-8') as f:
                data = yaml.safe_load(f)
        
        if not isinstance(data, dict):
            raise TypeError('YAML file must deserialize to a dictionary.')
        
        # Delegate to DictTransferStrat
        return DictTransferStrat.load_from(schema, data)

    @staticmethod
    def dump_into(schema : Schema, file : str | os.PathLike) -> None:
        """
        Dump schema definitions into a YAML file.

        Parameters
        ----------
        schema : Schema
            Initialized Libra Schema object with a specified name attribute and 
            populated _registry attribute.
        file : str | os.PathLike
            File path of a YAML file to dump schema definitions into. 
        """

        path = os.fspath(file)

        # Get canonical dictionary form
        data = DictTransferStrat.dump_into(schema)
        data = _normalize(data) # Normalize any sqlalchemy-injected weirdness

        with open(path, 'w', encoding = 'utf-8') as f:
            yaml.safe_dump(
                data, f, sort_keys = False, default_flow_style = False
            )

# ==============================================================================
# Libra Database Encoded Transfer Strategy

class DBTransferStrat(TransferStrat):

    # LIBRASCHEMA = resources.files('libra.schemas').joinpath('libra.yaml').open('r')
    SUPPORTED_PYTYPES : dict[str, type] = {
        'int' : int,
        'str' : str,
        'float' : float,
        'bool' : bool,
        'dict' : dict,
        'list' : list
    }

    @staticmethod
    def load_from(schema : Schema, db_settings : DatabaseSettings) -> Schema:
        """
        Load schema definitions from Libra's database schema.

        Parameters
        ----------
        schema : Schema
            Initialized Libra Schema object with a specified name attribute.
        db_settings : libra.util.DatabaseSettings
            Object containing injected information about a database connection 
            as well as explicit table names for the reference schema 
            description tables.
        
        Returns
        -------
        schema : Schema
            The same input Schema object, with an updated _registry object to 
            reflect information contained within the queried relational database
        """

        from libra.resources import load_yaml_resource

        _libra_dict = load_yaml_resource('libra.schemas', 'libra.yaml')
        
        _libra_schema = Schema('Libra').load(_libra_dict)
        (
            Schemadescript, 
            Modeldescript,
            Columnassoc,
            Columndescript,
            Columninfo,
            Constraintdescript
        ) = db_settings._generate(_libra_schema)

        if db_settings.create_tables:
            _libra_schema.base.metadata.create_all(db_settings.engine)

        schema_dict = {
            schema.name : {
                'description' : None,
                'columns' : {},
                'models' : {}
            }
        }

        with db_settings.engine.begin() as conn:
            # Load Schema description
            schema_row = (
                conn.execute(
                    sqlalchemy.select(Schemadescript).where(
                        Schemadescript.schema_name == schema.name
                    )
                ).mappings().one_or_none()
            )

            if not schema_row:
                raise SchemaNotFoundError(f'Schema \'{schema.name}\' not found in database.')

            schema_dict[schema.name]['description'] = schema_row.get('description', '-')

            # Load models
            model_rows = (
                conn.execute(
                    sqlalchemy.select(Modeldescript).where(
                        Modeldescript.schema_name == schema.name
                    )
                ).mappings().all()
            )
            
            for model in model_rows:
                model_name = model['model_name']

                assoc_columns = (
                    conn.execute(
                        sqlalchemy.select(Columnassoc.column_name).where(sqlalchemy.and_(
                            Columnassoc.model_name == model_name,
                            Columnassoc.schema_name == schema.name
                        )).order_by(Columnassoc.column_position)
                    ).scalars().all()
                )

                assoc_constraints = (
                    conn.execute(
                        sqlalchemy.select(Constraintdescript).where(
                            Constraintdescript.model_name == model_name,
                            Constraintdescript.schema_name == schema.name
                        )
                    ).mappings().all()
                )

                constraints = []
                for con in assoc_constraints:
                    _type = con.get('constraint_type')
                    _contypes = [list(_con.keys())[0] for _con in constraints]
                    if _type != 'ck':
                        if _type in _contypes:
                            idx = _contypes.index(_type)
                            constraints[idx][_type]['columns'].append(con.get('column_name'))
                        else:
                            constraints.append({_type : {'columns' : [con.get('column_name')]}})
                    else:
                        constraints.append({_type : {'sqltext' : con.get('sqltext')}})

                schema_dict[schema.name]['models'][model_name] = {
                    'columns' : assoc_columns,
                    'constraints' : constraints
                }

            # Load Columns
            column_rows = (
                conn.execute(
                    sqlalchemy.select(Columndescript).where(
                        Columndescript.schema_name == schema.name
                    )
                ).mappings().all()
            )

            colinfo_rows = (
                conn.execute(
                    sqlalchemy.select(Columninfo).where(
                        Columninfo.schema_name == schema.name
                    )
                ).mappings().all()
            )
            
            for column in column_rows:
                column_name = column.get('column_name')

                colinfo_entries = [e for e in colinfo_rows if e['column_name'] == column_name]
                info = {}
                for cinfo in colinfo_entries:
                    info[cinfo['key_name']] = DBTransferStrat.SUPPORTED_PYTYPES[cinfo.get('key_type', 'str')](cinfo['key_value'])

                columndict = {
                    'type' : column.get('type')
                }

                if column.get('nullable') == 'n':
                    columndict['nullable'] = False
                elif column.get('nullable') == 'y':
                    columndict['nullable'] = True

                default = column.get('_default', None)
                if default:
                    if isinstance(default, str) and default.startswith('{'):
                        try: default = ast.literal_eval(default)
                        except Exception: pass
                    columndict['default'] = default
                
                onupdate = column.get('onupdate', '-')
                if onupdate != '-':
                    if isinstance(onupdate, str) and onupdate.startswith('{'):
                        try: onupdate = ast.literal_eval(onupdate)
                        except Exception: pass
                    columndict['onupdate'] = onupdate
                
                if info:
                    columndict['info'] = info

                # Get columninfo

                schema_dict[schema.name]['columns'][column_name] = columndict

            return DictTransferStrat.load_from(schema, schema_dict)

    @staticmethod
    def dump_into(schema : Schema, db_settings : DatabaseSettings) -> None:
        """
        TODO : write this docstring
        """
        
        from libra.resources import load_yaml_resource

        _libra_dict = load_yaml_resource('libra.schemas', 'libra.yaml')

        _libra_schema = Schema('Libra', typemap = schema._registry.typemap).load(_libra_dict)
        (
            Schemadescript, 
            Modeldescript,
            Columnassoc,
            Columndescript,
            Columninfo,
            Constraintdescript
        ) = db_settings._generate(_libra_schema)

        # --------------------------------
        # Create Libra tables if requested
        # --------------------------------
        if db_settings.create_tables:
            _libra_schema.base.metadata.create_all(db_settings.engine)
        
        with db_settings.engine.begin() as conn:
            # -------------------------
            # Check for existing schema
            # -------------------------

            existing = conn.execute(
                sqlalchemy.select(sqlalchemy.func.count()).select_from(Schemadescript).where(Schemadescript.schema_name == schema.name)
            ).scalar_one()

            if existing and not db_settings.overwrite:
                raise ValueError(f'Schema \'{schema.name}\' already exists in database. Set overwrite=True in DatabaseSettings to replace it.')

            # ------------------------------------
            # If overwrite -> delete existing rows
            # ------------------------------------

            if existing and db_settings.overwrite:

                conn.execute(
                    sqlalchemy.delete(Constraintdescript).where(Constraintdescript.schema_name == schema.name)
                )

                conn.execute(
                    sqlalchemy.delete(Columninfo).where(Columninfo.schema_name == schema.name)
                )

                conn.execute(
                    sqlalchemy.delete(Columnassoc).where(Columnassoc.schema_name == schema.name)
                )

                conn.execute(
                    sqlalchemy.delete(Columndescript).where(Columndescript.schema_name == schema.name)
                )

                conn.execute(
                    sqlalchemy.delete(Modeldescript).where(Modeldescript.schema_name == schema.name)
                )

                conn.execute(
                    sqlalchemy.delete(Schemadescript).where(Schemadescript.schema_name == schema.name)
                )
            
            # ---------------------
            # Insert Schemadescript
            # ---------------------
            conn.execute(
                sqlalchemy.insert(Schemadescript).values(
                    schema_name = schema.name,
                    description = schema.description or '-',
                    modauthor = db_settings.author,
                    loadauthor = db_settings.author
                )
            )
            
            # ----------------------------------
            # Insert columndescript & columninfo
            # ----------------------------------
            for column_name, col in schema._registry.columns.items():
                conn.execute(
                    sqlalchemy.insert(Columndescript).values(
                        column_name = column_name,
                        type = col.get('type'),
                        nullable = 'y' if col.get('nullable') else 'n',
                        _default = str(col.get('default')) if col.get('default') else None,
                        onupdate = str(col.get('onupdate', '-')),
                        schema_name = schema.name,
                        modauthor = db_settings.author,
                        loadauthor = db_settings.author,
                    )
                )

                for key, value in col.get('info', {}).items():
                    conn.execute(
                        sqlalchemy.insert(Columninfo).values(
                            column_name = column_name,
                            schema_name = schema.name,
                            key_name = key,
                            key_type = type(value).__name__,
                            key_value = str(value),
                            modauthor = db_settings.author,
                            loadauthor = db_settings.author
                        )
                    )
            
            # ------------------------------------------------
            # Insert modeldescript & columnassoc & constraints
            # ------------------------------------------------
            for model_name, model in schema._registry.models.items():
                conn.execute(
                    sqlalchemy.insert(Modeldescript).values(
                        model_name = model_name,
                        description = model.get('description', '-'),
                        schema_name = schema.name,
                        modauthor = db_settings.author,
                        loadauthor = db_settings.author
                    )
                )

                for idx, column_name in enumerate(model.get('columns', {})):
                    conn.execute(
                        sqlalchemy.insert(Columnassoc).values(
                            column_name = column_name,
                            model_name = model_name,
                            column_position = idx,
                            schema_name = schema.name,
                            modauthor = db_settings.author,
                            loadauthor = db_settings.author
                        )
                    )
                
                for constraint in model.get('constraints', {}):
                    for ctype, payload in constraint.items():
                        if ctype == 'ck':
                            conn.execute(
                                sqlalchemy.insert(Constraintdescript).values(
                                    constraint_type = ctype,
                                    column_name = '-',
                                    sqltext = payload.get('sqltext', '-'),
                                    model_name = model_name,
                                    schema_name = schema.name,
                                    modauthor = db_settings.author,
                                    loadauthor = db_settings.author
                                )
                            )
                        else:
                            for column in payload.get('columns', []):
                                conn.execute(
                                    sqlalchemy.insert(Constraintdescript).values(
                                        constraint_type = ctype,
                                        column_name = column,
                                        sqltext = '-',
                                        model_name = model_name,
                                        schema_name = schema.name,
                                        modauthor = db_settings.author,
                                        loadauthor = db_settings.author
                                    )
                                )

# ==============================================================================
# Legacy "Schema-Schema" Encoded Transfer Strategy

class SSTransferStrat(TransferStrat):
    """
    TransferStrategy subclass to load and dump schema definitions to/from 
    schema-schema formatted database tables described in Carr et al., 2007.

    NOTE: Being a legacy format, the "Schema-Schema" has a number of caveats to 
    its assumptions behind serialization:
        1. Oracle-centric, so only a subset of Oracle types are supported in 
           serialization/deserialization.
        2. Formatting metadata that accompanies columns is assumed to be defined 
           in explicit Fortran specification.
        3. No support for check constraints or indexing - only primary keys and 
           unique constraints; also, constraint info is tightly coupled with 
           column definitions, so any combination of columns belonging to a 
           single table are assumed to create a composite constraint. 
    """

    # List of keys to exclude from serialized column definitions
    EXCLUDE_KEYS : list[str] = [
        'column_name', 'table_name', 'schema_name', 'internal_format', 
        'na_allowed', 'na_value', 'column_type', 'column_position', 
        'auth', 'lddate', 'auth_1', 'lddate_1', 'schema_name_1', 'column_name_1',
        'nativekeyname', 'nativekeyschema'
    ]

    # Custom byte-encoded VARCHAR2
    class VARCHAR2(sqlalchemy.String): ...

    @compiles(VARCHAR2)
    def _compile(type_, compiler, **kw):
        len = type_.length
        return 'VARCHAR2(%i BYTE)'

    @staticmethod
    def load_from(schema : Schema, ss_settings : SchemaSchemaSettings) -> Schema:
        """
        Load schema definitions from the Schema-Schema self-describing schema

        Parameters
        ----------
        schema : Schema
            Initialized Libra Schema object with a specified name attribute.
        ss_settings : libra.util.SchemaSchemaSettings
            Settings object with an initialized SQLAlchemy Engine for database 
            connection and all relevant table names defined.
        
        Returns
        -------
        Schema
            The same input Schema object, with an updated _registry object to 
            reflect information contained within the input schemadict. 
        """

        if ss_settings.engine.dialect.name != 'oracle':
            raise BackendUnsupported(f'Schema-schema load is only supported by Oracle backends; got \'{ss_settings.engine.dialect.name}\'')

        metadata = sqlalchemy.MetaData()

        # Reflecting schema-schema tables - have to deal with Oracle-style tablenames
        tabdescript = _fix_reflected_tables(ss_settings.engine, metadata, ss_settings.tabdescript)
        colassoc = _fix_reflected_tables(ss_settings.engine, metadata, ss_settings.colassoc)
        coldescript = _fix_reflected_tables(ss_settings.engine, metadata, ss_settings.coldescript)
        
        # Mutate Schema TypeMap - SchemaSchema only supports four Oracle types
        new_typemap = TypeMap({
            'DATE' : sqlalchemy.DateTime,
            'FLOAT' : sqlalchemy.dialects.oracle.FLOAT,
            'NUMBER' : sqlalchemy.dialects.oracle.NUMBER,
            'VARCHAR2' : SSTransferStrat.VARCHAR2
        })

        schema.typemap = new_typemap
        schema._registry.typemap = new_typemap
        schema._registry.columnhandler.typehandler.typemap = new_typemap

        # Initialize output dictionary structure
        schema_dict = {
            schema.name : {
                'description' : None,
                'columns' : {},
                'models'  : {}
            }
        }

        with ss_settings.engine.connect() as conn:

            # Fetch models
            models = [model[0] for model in conn.execute(sqlalchemy.select(tabdescript.c.table_name).where(tabdescript.c.schema_name == schema.name)).fetchall()]

            schema_dict[schema.name]['models'] = {m : {'columns' : [], 'constraints' : []} for m in models}
            table_constraints = {m : {'pk' : [], 'uq' : []} for m in models}

            # Fetch columns
            col_rows = conn.execute(
                sqlalchemy.select(colassoc, coldescript).where(
                    (colassoc.c.schema_name == schema.name) &
                    (coldescript.c.schema_name == schema.name) &
                    (colassoc.c.column_name == coldescript.c.column_name)
                ).order_by(colassoc.c.column_position)
            ).fetchall()

            # Parse columns
            for row in col_rows:
                table_name = row.table_name
                column_name = row.column_name

                internal = row.internal_format.upper()
                nullable = True if row.na_allowed.lower() == 'y' else False
                default = row.na_value if row.na_value else None
                onupdate = None

                # Don't inject, but understand what type we're working with
                # (Can only be one of four)
                _pytype = schema._registry.typehandler.deserialize(internal).python_type if internal[0:6] != 'NUMBER' else int

                # Schema-schema doesn't support $ref encoding - force some knowns
                if column_name in ('lddate', 'moddate', 'loaddate'):
                    _pytype = str # Reset _pytype to force these to be strings
                    default = {'$ref' : 'datetime.now'}
                    onupdate = {'$ref' : 'datetime.now'}
                
                # Get info dictionary
                info = {}
                for key, value in row._mapping.items():
                    if key not in SSTransferStrat.EXCLUDE_KEYS and value is not None:
                        if key in ('nmin', 'nmax', 'emin', 'emax'):
                            info[key] = float(value)
                        else:
                            info[key] = str(value)
                
                # Fix any float/int issues
                try:
                    default = _pytype(default) if default != 'NA' else None
                except ValueError:
                    default = _pytype(float(default))

                col_def = {
                    'type' : internal,
                    'nullable' : nullable,
                    'default' : default,
                    'onupdate' : onupdate, # Only 'lddate', 'moddate', 'loaddate' is assigned 'onupdate' flag in schema-schema
                    'info' : info
                }

                # Remove implicit/default values
                if col_def['nullable'] is True: col_def.pop('nullable')
                if col_def['default'] is None: col_def.pop('default')
                if col_def['onupdate'] is None: col_def.pop('onupdate')
                if col_def['info'] is None: col_def.pop('info')

                if column_name not in schema_dict[schema.name]['columns'].keys():
                    schema_dict[schema.name]['columns'][column_name] = col_def

                schema_dict[schema.name]['models'][table_name]['columns'].append(column_name)

                # Assemble constraints
                if row.column_type == 'primary key':
                    table_constraints[table_name]['pk'].append(column_name)
                
                if row.column_type == 'unique key':
                    table_constraints[table_name]['uq'].append(column_name)
        

        for table_name, cons in table_constraints.items():
            if cons['pk']:
                schema_dict[schema.name]['models'][table_name]['constraints'].append({'pk' : {'columns' : cons['pk']}})
            if cons['uq']:
                schema_dict[schema.name]['models'][table_name]['constraints'].append({'uq' : {'columns' : cons['uq']}})

        return DictTransferStrat.load_from(schema, schema_dict)

    @staticmethod
    def dump_into(schema : Schema, ss_settings : SchemaSchemaSettings) -> None:
        return NotImplementedError('Schema-schema dump ability currently unsupported')

# ==============================================================================
# Additional Functions

def _process_model(schema : Schema, cls : _UnbasedClass) -> type[DeclarativeBase]:
    """
    Convert an 'unbased' ORM definition into a subclass of SQLAlchemy's 
    DeclarativeBase. 

    Parameters
    ----------
    schema : Schema
        Libra Schema instance, with a _registry object to consult for handling 
        constraint deserialization.
    cls : _UnbasedClass
        'unbased' class with 'columns' and 'constraints' attributes 
        representative of what's desired in the final abstract ORM Table 
        instance.
    
    Returns
    -------
    type[DeclarativeBase]
        Subclass of SQLAlchemy's DeclarativeBase class, representing an abstract 
        SQLAlchemy Table instance.
    
    Warns
    -----
    RuntimeWarning
        Raised when a ForeignKeyConstraint type is included in the unbased 
        class' __table_args__ attribute to warn about potentially unexpected 
        behavior. SQLAlchemy.ForeignKeyConstraint expects reference columns to 
        be constructed as: <__tablename__>.<reference_column>. Because these 
        are abstract ORM instances, __tablename__ is not defined yet and 
        cannot be used to construct a valid ForeignKeyConstraint.
    """

    parents = (*schema.mixins, schema.base)

    # ------------------------
    # Construct __table_args__
    # ------------------------

    # table_args = getattr(cls, '__table_args__', None)
    if hasattr(cls, '__table_args__'):
        table_args = cls.__table_args__

        # Warn on FK constraints
        for con in table_args:
            if isinstance(con, sqlalchemy.ForeignKeyConstraint):
                warnings.warn('Including ForeignKeyConstraint in abstract model definitions may lead to unexpected behavior', RuntimeWarning)
    
    else:
        constraints = [schema._registry.constrainthandler.deserialize(con) for con in getattr(cls, 'constraints', [])]

        table_args = tuple(constraints)
    
    # --------------------------
    # Build attribute dictionary
    # --------------------------

    attrs = {
        '__abstract__' : True,
        '__table_args__' : table_args,
        **cls.columns
    }

    model_cls = type(cls.__name__, parents, attrs)

    return model_cls

def _resolve_load_strategy(source : Any) -> type[TransferStrat]:
    """
    Resolve appropriate load strategy based on a given source object.

    Parameters
    ----------
    source : Any
        Variable whose type informs which child of TransferStrat to call
    
    Returns
    -------
    type[TransferStrat]
        Child of TransferStrategy object
    
    Raises
    ------
    AttributeError
        Raised in the event that a custom source is passed and doesn't 
        clearly specify the appropriate transfer_strategy as an attribute 
        of the input source.
    libra.util.StrategyUnsupported
        Raised in the event that a passed string or os.PathLike object does 
        not have a recognized file extension.
    """

    @singledispatch
    def _dispatch(source : Any) -> type[TransferStrat]:
        try:
            return source.transfer_strategy
        except AttributeError:
            raise AttributeError('Custom source must contain \'transfer_strategy\' as an attribute.')

    @_dispatch.register(dict)
    def _(dict : dict) -> DictTransferStrat:
        return DictTransferStrat

    @_dispatch.register(str)
    @_dispatch.register(os.PathLike)
    def _(file : str | os.PathLike) -> YAMLTransferStrat:
        ext = os.path.splitext(file)[1].lower()
        if ext in {'.yaml', '.yml'}:
            return YAMLTransferStrat
        raise StrategyUnsupported(f'Only strings containing yaml filepaths are supported. Got \'{file}\'')
    
    @_dispatch.register(DatabaseSettings)
    def _(dbsettings : DatabaseSettings) -> DBTransferStrat:
        return DBTransferStrat

    @_dispatch.register(SchemaSchemaSettings)
    def _(sssetings : SchemaSchemaSettings) -> SSTransferStrat:
        return SSTransferStrat

    return _dispatch(source)

def _resolve_dump_strategy(target : Any) -> type[TransferStrat]:
    """
    Resolve appropriate dump strategy based on given target object or lack of 
    target object.

    Parameters
    ----------
    target : Any
        Variable whose type informs which child of TransferStrat to call
    
    Returns
    -------
    type[TransferStrat]
        Child of TransferStrategy object
    
    Raises
    ------
    AttributeError
        Raised in the event that a custom target is passed and doesn't 
        clearly specify the appropriate transfer_strategy as an attribute 
        of the input target.
    libra.util.StrategyUnsupported
        Raised in the event that a passed string or os.PathLike object does 
        not have a recognized file extension.
    """

    @singledispatch
    def _dispatch(target : Any) -> type[TransferStrat]:
        if target is None: # If None - dump as a dictionary
            return DictTransferStrat
        
        try:
            return target.transfer_strategy
        except AttributeError:
            raise AttributeError('Custom target must contain \'transfer_strategy\' as an attribute.')
    
    @_dispatch.register(str)
    @_dispatch.register(os.PathLike)
    @_dispatch.register(Traversable)
    def _(file : str | os.PathLike | Traversable) -> YAMLTransferStrat:
        ext = os.path.splitext(file)[1].lower()
        if ext in {'.yaml', '.yml'}:
            return YAMLTransferStrat
        raise StrategyUnsupported(f'Only strings containing yaml filepaths are supported. Got \'{file}\'')
    
    @_dispatch.register(DatabaseSettings)
    def _(dbsettings : DatabaseSettings) -> DBTransferStrat:
        return DBTransferStrat
    
    @_dispatch.register(SchemaSchemaSettings)
    def _(sssettings : SchemaSchemaSettings) -> SSTransferStrat:
        return SSTransferStrat

    return _dispatch(target)

def _fix_reflected_tables(engine : sqlalchemy.Engine, metadata : sqlalchemy.MetaData, name : str) -> sqlalchemy.Table:
    """Reflect table given by 'name', handling Oracle '.' notation"""

    if '.' in name:
        schema, table = name.split('.', 1)
        return sqlalchemy.Table(table, metadata, schema = schema, autoload_with = engine)
    else:
        return sqlalchemy.Table(table, name, metadata, autoload_with = engine)

def _normalize(obj):
    if isinstance(obj, dict):
        return {
            str(k) if isinstance(k, sqlalchemy.sql.elements.quoted_name) else k: _normalize(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [_normalize(v) for v in obj]
    else:
        return obj
    