"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

"Handler" objects which are responsible for the serialization/deserialization 
of text into SQLAlchemy objects and vice versa. Specifically, these SQLAlchemy 
objects include Types, Constraints, Columns, and Models.
"""

# ==============================================================================

from __future__ import annotations

import re
import ast
import copy
import inspect
import operator
from abc import ABC, abstractmethod
from functools import singledispatch
from datetime import datetime, timezone
from typing import (
    Any,
    Callable,
    TypeVar
)

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Constraint
from sqlalchemy.sql.elements import ClauseElement

# ==============================================================================
# Typing

SaType = TypeVar('SaType', bound = sqlalchemy.types)

# ==============================================================================
# Safe Evaluation Functions for use in ColumnHandler.safe_eval_registry

def utcdatetime(_) -> datetime:
    """Return current datetime object at UTC timezone"""

    return datetime.now(timezone.utc)

# ==============================================================================
# Default Evaluation Registry Global Variable

DEFAULT_SAFE_EVAL_REGISTRY : dict[str, Any] = {
    'datetime.now' : utcdatetime
}

# ==============================================================================
# TypeMap Class

class TypeMap:
    """
    Hash structure to contain mapping behavior between strings and SQLAlchemy 
    "CamelCase" and "UPPERCASE" type objects. 

    NOTE: Keys are required to be unique across keys and values are required 
    to be unique across values, or in other words, a unique string will need 
    to map to a unique sqlalchemy type.

    Attributes
    ----------
    _mapping : dict
        Hash map connecting strings to SQLAlchemy type objects. Default is 
        the attached DEFAULT_TYPEHASH parameter.
    """

    DEFAULT_TYPEHASH : dict[str, SaType] = {
        'BigInteger' : sqlalchemy.BigInteger,
        'Boolean' : sqlalchemy.Boolean,
        'Date' : sqlalchemy.Date,
        'DateTime' : sqlalchemy.DateTime,
        'Enum' : sqlalchemy.Enum,
        'Double' : sqlalchemy.Double,
        'Float' : sqlalchemy.Float,
        'Integer' : sqlalchemy.Integer,
        'Interval' : sqlalchemy.Interval,
        'LargeBinary' : sqlalchemy.LargeBinary,
        'Numeric' : sqlalchemy.Numeric,
        'PickleType' : sqlalchemy.PickleType,
        'SmallInteger' : sqlalchemy.SmallInteger,
        'String' : sqlalchemy.String,
        'Text' : sqlalchemy.Text,
        'Time' : sqlalchemy.Time,
        'Unicode' : sqlalchemy.Unicode,
        'UnicodeText' : sqlalchemy.UnicodeText,
        'Uuid' : sqlalchemy.Uuid,
        'ARRAY' : sqlalchemy.ARRAY,
        'BIGINT' : sqlalchemy.BIGINT,
        'BINARY' : sqlalchemy.BINARY,
        'BLOB' : sqlalchemy.BLOB,
        'BOOLEAN' : sqlalchemy.BOOLEAN,
        'CHAR' : sqlalchemy.CHAR,
        'CLOB' : sqlalchemy.CLOB,
        'DATE' : sqlalchemy.DATE,
        'DATETIME' : sqlalchemy.DATETIME,
        'DECIMAL' : sqlalchemy.DECIMAL,
        'DOUBLE' : sqlalchemy.DOUBLE,
        'DOUBLE_PRECISION' : sqlalchemy.DOUBLE_PRECISION,
        'FLOAT' : sqlalchemy.FLOAT,
        'INT' : sqlalchemy.INT,
        'JSON' : sqlalchemy.JSON,
        'INTEGER' : sqlalchemy.INTEGER,
        'NCHAR' : sqlalchemy.NCHAR,
        'NVARCHAR' : sqlalchemy.NVARCHAR,
        'NUMERIC' : sqlalchemy.NUMERIC,
        'REAL' : sqlalchemy.REAL,
        'SMALLINT' : sqlalchemy.SMALLINT,
        'TEXT' : sqlalchemy.TEXT,
        'TIME' : sqlalchemy.TIME,
        'TIMESTAMP' : sqlalchemy.TIMESTAMP,
        'UUID' : sqlalchemy.UUID,
        'VARBINARY' : sqlalchemy.VARBINARY,
        'VARCHAR' : sqlalchemy.VARCHAR
    }

    def __init__(self, typehash : dict[str, SaType] | None = None) -> None:
        """
        Constructs a TypeMap object, overriding key-value pairs of the 
        attached DEFAULT_TYPEHASH as provided.

        Parameters
        ----------
        typehash : dict[str, SaType] | None = None
            Optional dictionary specifying which entries in self._mapping should 
            be overwritten, updated, or added.
        """

        self._mapping = copy.deepcopy(TypeMap.DEFAULT_TYPEHASH)

        if typehash:
            for key, value in typehash.items():
                self[key] = value
        
    def __call__(self) -> dict[str, SaType]:
        """Returns the typehash as defined in self._mapping"""

        return self._mapping

    def __getitem__(self, identifier : str | SaType) -> SaType | str:
        """
        Gets either the string reference to the SQLAlchemy type object given the
        object, or gets the SQLAlchemy type object give its string reference.

        Parameters
        ----------
        identifier : str | SaType
            String or SQLAlchemy type object to retrieve the corollary item
        
        Returns
        -------
        SaType | str
            The mapped hash of the passed identifier.
        """

        _types = tuple(type(v) for v in self._mapping.values())

        if isinstance(identifier, str):
            return self._mapping[identifier]
        elif isinstance(identifier, _types):
            return [key for key, val in self._mapping.items() if val == identifier][0]
        else:
            raise TypeError(f'Identifier type must be of type <str> or <sqlalchemy.types>; Got: \'{type(identifier)}\'')

    def __setitem__(self, key : str, value : SaType) -> None:
        """
        Updates self._mapping to include the passed key-value pair. Keys must 
        be unique across all self._mapping. Existing keys will have their values
        replaced, and existing values will have their keys replaced. 
        Non-existing keys will be appended onto self._mapping. 

        Parameters
        ----------
        key : str
            String call to an SQLAlchemy type object. (e.g. 'String', 'VARCHAR')
        value : SaType
            SQLAlchemy type object. (e.g. sqlalchemy.Integer, sqlalchemy.Date)
        """

        keys_to_remove = [k for k, v in self._mapping.items() if v is value]
        for k in keys_to_remove:
            del self._mapping[k]
        
        self._mapping[key] = value

    def __eq__(self, other : TypeMap) -> bool:
        """Equal if all _mapping key-value pairs are the same between self and other"""

        return self._mapping == other._mapping


# ==============================================================================
# Handler Abstract Base Class

class Handler(ABC):
    """Abstract Hanlder class to serialize & deserialize ORM objects"""

    @abstractmethod
    def deserialize(self) -> Any:
        """Builds desired ORM object from a text-based blueprint"""
        ...

    @abstractmethod
    def serialize(self) -> Any:
        """Builds text-based blueprint from an ORM object"""
        ...


# ==============================================================================
# Various Classes to Serialize & Deserialize SQLAlchemy components

class TypeHandler(Handler):
    """
    Hanlder class to handle SQLAlchemy type objects, including the 
    deserialization of strings to SQLALchemy type objects and the serialization 
    of SQLAlchemy type objects to strings.

    Attributes
    ----------
    typemap : TypeMap
        TypeMap object containing explicity mappings from recognized 
        strings to SQLALchemy type objects. Used by TypeHandler to invoke 
        the desired SQLAlchemy type upon deserialization or invoke the 
        mapped string upon serialization.
    evaluator : TypeParamEvaluator
        TypeParamEvaluator interprets and emits parameters for a specific 
        string - SQLAlchemy type pair.
    """

    def __init__(self, typemap : TypeMap = TypeMap()) -> None:
        """
        Constructs a TypeHandler object.

        Parameters
        ----------
        typemap : TypeMap
            TypeMap object containing explicity mappings from recognized 
            strings to SQLALchemy type objects. Used by TypeHandler to invoke 
            the desired SQLAlchemy type upon deserialization or invoke the 
            mapped string upon serialization.
        """

        self.typemap = typemap

    def deserialize(self, type_str : str) -> type[SaType]:
        """
        Construct an SQLAlchemy type object from a plain string.

        Parameters
        ----------
        type_str : str
            Call to an SQLAlchemy type object, with any parameters included in 
            the string (e.g. 'String(8)', 'Float(precision = 53)')
        
        Returns
        -------
        SaType
            SQLAlchemy.types object, overriden by any non-default mapping 
            provided in self.typemap.
        
        Raises
        ------
        KeyError
            Raised in the case that a call to a specific type isn't in the 
            typemap attribute.
        """

        # Grab any inputs out of input string 
        _inputs = re.findall(r'\(([^)]*)\)', type_str)

        # Evaluate extracted _inputs from type_str, pass to args, kwargs
        args, kwargs = (), {}
        if _inputs:
            args, kwargs = parse_param_string(_inputs[0])
        
        # Map type_name to self.typemap
        type_name = re.split(r'\([^)]*\)', type_str)[0]
        sa_type = self.typemap[type_name]

        return sa_type(*args, **kwargs)

    def serialize(self, sa_type : SaType) -> str:
        """
        Deconstruct an SQLAlchemy type object into a string.

        Parameters
        ----------
        sa_type : SaType
            SQLAlchemy.types object to be converted into a string.
        
        Returns
        -------
        str
            String representation of the passed object, with any parameters 
            also included.
        """

        # Grab all possible __init__ parameters of the SQLAlchemy type obj
        parameters = {}
        for _member in type(sa_type).__mro__[::-1]:
            if _member in list(self.typemap._mapping.values()):
                _sig = inspect.signature(_member.__init__)
                parameters.update(_sig.parameters)
        
        # Keep only non-default __init__ parameters
        nondef_params = {}
        for name, param in parameters.items():
            try:
                if sa_type.__dict__[name] != param.default:
                    nondef_params.update({name : sa_type.__dict__[name]})
            except KeyError:
                pass
        
        # Determine if non-instance or instance (e.g. 'Integer' vs 'Integer()')
        if sa_type.__class__.__name__ == 'type':
            _mapped_type = self.typemap[sa_type]
            return_str = f'{_mapped_type}'
            _add_paren = False
        else:
            _mapped_type = self.typemap[type(sa_type)]
            return_str = f'{_mapped_type}'
            _add_paren = True
        
        if nondef_params != {}:
            return_str += '('
            for i, (key, val) in enumerate(nondef_params.items()):
                if isinstance(val, str):
                    return_str = f"{return_str}{key} = '{val}'"
                else:
                    return_str = f"{return_str}{key} = {val}"
                
                if i != len(nondef_params.keys()) - 1:
                    return_str += ', '
            return_str += ')'
        
        else:
            if _add_paren:
                return_str += '()'
        
        return return_str


class ColumnHandler(Handler):
    """
    Handler class to serialize and deserialize SQLAlchemy column objects. 
    
    Attributes
    ----------
    typehandler : libra.util.TypeHandler
        TypeHandler object responsible for serializing/deserializing SQLAlchemy
        Type objects associated with a Column.
    """

    CALLABLE_COLUMN_KWARGS : set[str] = (
        "default",
        "onupdate",
        "insert_default",
    )

    def __init__(self, typehandler : TypeHandler = TypeHandler(), safe_eval_registry : dict[str, Any] = DEFAULT_SAFE_EVAL_REGISTRY) -> None:
        """
        Constructor for a ColumnHandler object
        
        Parameters
        ----------
        typehandler : TypeHandler = TypeHandler()
            TypeHandler object to convert between string calls to SQLALchemy 
            types and their mapped SQLAlchemy types. Default is a generic 
            TypeHandler object with no overridden types.
        safe_eval_registry : dict[str, Any]
            Safe evaluation registry, containing string-value pairs where the 
            associated value will override the referenced string in a Column's
            construction.
        """

        self.typehandler = typehandler
        self.safe_eval_registry = safe_eval_registry
    
    def _to_ref(self, obj : Any) -> dict[str, Any] | None:
        """Convert Python object to a {'$ref' : ...} mapping if allowed"""

        for key, val in self.safe_eval_registry.items():
            if val is obj:
                return {'$ref' : key}
        
        return None

    def _unwrap_column_default(self, value : Any) -> str:
        """Normalize SQLAlchemy default wrappers."""

        if isinstance(
            value, 
            (
                sqlalchemy.sql.schema.CallableColumnDefault, 
                sqlalchemy.sql.schema.ScalarElementColumnDefault
            )
        ):
            return value.arg
        return value

    def deserialize(self, coldict_ : dict[str, dict[str, Any]]) -> Column:
        """
        Deserialize a dictionary describing the name and __init__ variables of 
        an SQLAlchemy column, which are also passed as a dictionary of key-
        value pairs.

        Parameters
        ----------
        coldict_ : dict[str, dict[str, Any]]
            Dictionary describing the initialization variables for a column of 
            the form: 
            {'column_name' : {'type' : 'String(8)', 'nullable' : False}}
        
        Returns
        -------
        Column
            SQLAlchemy Column object, initialized with parameters included in 
            the input dictionary.
        
        Raises
        ------
        ValueError : Serialized Column dictionary must contain one column name.
            Raised in the case that coldict does not contain one column name.
        ValueError : Reference not supported for Column kwarg.
            Raised in the case that a serialized reference ('$ref') is made to 
            a Column's __init__ parameter incapable of supporting that 
            serialized reference. 
        KeyError : 'type' keyword must be specified.
            Raised in the case that a 'type' keyword is not provided within the 
            dictionary assigned to a column's name.
        KeyError : Unsafe or unknown reference
            Raised in the case that a reference to a serialized object is not 
            recognized in the ColumnHandler's 
        """

        coldict = copy.deepcopy(coldict_)

        if len(coldict) != 1:
            raise ValueError('Serialized Column dictionary must contain exactly one column name.')
        
        colname, params = next(iter(coldict.items()))
        
        try:
            type_str = params.pop('type')
        except KeyError:
            raise KeyError('\'type\' keyword must be specified.')
        
        coltype = self.typehandler.deserialize(type_str)

        resolved : dict[str, Any] = {}
        for key, value in params.items():
            if isinstance(value, dict) and '$ref' in value:
                if key not in self.CALLABLE_COLUMN_KWARGS:
                    raise ValueError(f'Reference not supported for Column kwarg \'{key}\'.')
                
                ref = value['$ref']
                try:
                    resolved[key] = self.safe_eval_registry[ref]
                except KeyError:
                    raise KeyError(f'Unsafe or unknown reference: {ref}')
            else:
                resolved[key] = value

        return Column(colname, coltype, **resolved)

    def serialize(self, ref_name : str, column : Column) -> dict[str, dict[str, Any]]:
        """
        Serialize an SQLAlchemy Column object to a dictionary containing key-
        value pairs describing that Column object's initialization parameters.
         
        Parameters
        ----------
        ref_name : str
            The column's name passed as a string.
        column : Column
            SQLAlchemy Column object to deconstruct.
        
        Returns
        -------
        dict[str, dict[str, Any]]
            Nested dictionary containing the column's name, as well as all of 
            its non-default __init__ parameters as key-value pairs.
        
        Raises
        ------
        ValueError : Callable not allowed for Column kwarg.
            Raised in the case that a callable is passed to a Column.__init__s'
            kwargs not listed in self.CALLABLE_COLUMN_KWARGS
        ValueError : Callable not registered in safe_eval_registry.
            Raised in the case that a callable mapped to one of the kwargs in a 
            Column's __init__ method is not registered as a safe reference.
        """

        parameters = {}
        _sig = inspect.signature(column.__init__)
        parameters.update(_sig.parameters)

        col_init_params = {
            'type' : self.typehandler.serialize(column.type)
        }

        for name, param in parameters.items():
            try:
                value = column.__dict__[name]
            except KeyError:
                continue

            # Skip defaults
            if value == param.default:
                continue

            value = self._unwrap_column_default(value)

            # Callable handling
            if callable(value):
                if name not in self.CALLABLE_COLUMN_KWARGS:
                    raise ValueError(f'Callable not allowed for Column kwarg \'{name}\'.')

                # Resolve non-serialized objects
                ref = self._to_ref(value)
                if ref is None:
                    raise ValueError(f'Callable \'{value}\' not registered in safe_eval_registry.')
                
                col_init_params[name] = ref

                continue

            col_init_params[name] = value
            
        # --- SQLAlchemy cleanup rules ---

        # nullable = True is implicit
        if col_init_params.get('nullable') is True:
            del col_init_params['nullable']
        
        # SQLAlchemy injects this sometimes
        if col_init_params.get('info') == {}:
            del col_init_params['info']
        
        # Internal bookkeeping
        col_init_params.pop('key', None)
        col_init_params.pop('name', None)

        # default = _NoArg.NO_ARG -> remove
        if 'default' in col_init_params and not col_init_params['default']:
            del col_init_params['default']
        
        return {ref_name : col_init_params}
        

class ConstraintHandler(Handler):
    """
    Handler class to deserialize and serialize SQLALchemy Constraints & Indexes

    Supported constraint objects:
        - PrimaryKeyConstraint (pk)
        - UniqueConstraint (uq)
        - CheckConstraint (ck)
        - Index (ix)

    ForeignKeyConstrain support is intentionally dropped due to depedency on 
    Table.__tablename__ and DDL registration issues.
    """
    
    def _get_constraint_init_params(self, cls : type) -> dict[str, inspect.Parameter]:
        """
        Walk up a constraint class's mro and pull all __init__ parameters.

        Parameters
        ----------
        cls : type
            Class object, typically an SQLAlchemy Constraint object

        Returns
        -------
        dict[str, inspect.Parameter]
            A dictionary mapping a parameter name to an inspect.Parameter value
        """

        params : dict[str, inspect.Parameter] = {}
        for base in reversed(cls.__mro__):
            init = getattr(base, '__init__', None)
            if init is None:
                continue
            
            try:
                sig = inspect.signature(init)
            except (TypeError, ValueError):
                continue

            params.update(sig.parameters)

        return params

    def deserialize(self, condict_ : dict[str, dict[str, Any]]) -> type[Constraint]:
        """
        Deserialize a dictionary describing the constraint and any accompanying 
        __init__ parameters.

        Parameters
        ----------
        condict_ : dict[str, dict[str, Any]]
            Nested dictionary identifying one of four constraints ('pk', 'uq',
            'ck', 'ix') and all of the __init__ parameters associated with that 
            SQLAlchemy constraint type.

        Returns
        -------
        type[Constraint]
            One of SQLAlchemy's PrimaryKeyConstraint, UniqueConstraint, 
            CheckConstraint, or Index.
        
        Raises
        ------
        ValueError : Unsupported constraint type
            Raised when one of the four supported constraints are not passed
        """

        condict = copy.deepcopy(condict_)
        key, con_dict = next(iter(condict.items()))

        match key:
            case 'pk':
                columns = con_dict.pop('columns')
                return sqlalchemy.PrimaryKeyConstraint(*columns, **con_dict)
            case 'uq':
                columns = con_dict.pop('columns')
                return sqlalchemy.UniqueConstraint(*columns, **con_dict)
            case 'ck':
                sqltext = _deserialize_expr(con_dict.pop('sqltext'))
                return sqlalchemy.CheckConstraint(sqltext, **con_dict)
            case 'ix':
                columns = [sqlalchemy.column(col) for col in con_dict.pop('columns')]
                return sqlalchemy.Index(con_dict.pop('name', None), *columns, **con_dict)
            case _:
                raise ValueError(f'Unsupported constraint type: {key}')

    def serialize(self, constraint : type[Constraint]) -> dict[str, dict[str, Any]]:
        """
        Serialize an SQLAlchemy Constraint object into a dictionary, with any 
        accompanying parameters also serialized in that dictionary.

        Parameters
        ----------
        constraint : type[Constraint]
            SQLAlchemy Constraint type; supported types include:
            - PrimaryKeyConstraint
            - UniqueConstraint
            - CheckConstraint
            - Index
        
        Returns
        -------
        dict[str, dict[str, Any]]
            Serialized dictionary containing the type of constraint as a two-
            letter string ('pk', 'uq', 'ck', 'ix') and any args or kwargs 
            included in the nested dictionary.
        
        Raises
        ------
        ValueError
            Raised in the case that a Constraint object is unsupported
        """

        @singledispatch
        def _process(constraint : type[Constraint]) -> tuple[str, dict[str, Any]]:
            raise ValueError(f'Unsupported constraint type: {type(constraint)}')

        @_process.register(sqlalchemy.PrimaryKeyConstraint)
        def _(constraint : sqlalchemy.PrimaryKeyConstraint) -> tuple[str, dict[str, Any]]:
            columns = constraint._pending_colargs
            return 'pk', {'columns' : columns}

        @_process.register(sqlalchemy.UniqueConstraint)
        def _(constraint : sqlalchemy.UniqueConstraint) -> tuple[str, dict[str, Any]]:
            columns = constraint._pending_colargs
            return 'uq', {'columns' : columns}

        @_process.register(sqlalchemy.CheckConstraint)
        def _(constraint : sqlalchemy.CheckConstraint) -> tuple[str, dict[str, Any]]:
            sqltext = _serialize_expr(constraint.sqltext)
            return 'ck', {'sqltext' : sqltext}

        @_process.register(sqlalchemy.Index)
        def _(constraint : sqlalchemy.Index) -> tuple[str, dict[str, Any]]:
            columns = [c.name for c in constraint.expressions]
            name = constraint.name
            return 'ix', {'columns' : columns, 'name' : name}
        
        contype, type_params = _process(constraint)
        
        # Include any non-default kwargs from __init__
        parameters = self._get_constraint_init_params(type(constraint))

        con_init_params = {}
        for name, param in parameters.items():
            if name in ('self', 'table'): # skip table references
                continue
            
            # Skip sqlalchemy internals of Index
            if isinstance(constraint, sqlalchemy.Index) and name == 'expressions':
                continue

            try:
                value = constraint.__dict__[name]
                if value != param.default:
                    con_init_params[name] = value

            except KeyError:
                continue
            
        con_init_params.update(type_params)

        return {contype : con_init_params}

# ==============================================================================
# Helpful Functions

def parse_param_string(param_str : str) -> tuple[tuple, dict]:
    """
    Parses a string formatted as inputs to a function, using ast.literal_eval() 
    to evaluate each arg and kwarg in the parameter string.

    Parameters
    ----------
    param_str : str
        Input parameter string: "8, variable1 = 'example', variable2 = 43.0"
    
    Returns
    -------
    tuple[tuple, dict]
        Parameter string broken into args and kwargs.
    """

    tree = ast.parse(f"f({param_str})", mode = 'eval')

    call = tree.body
    args = [ast.literal_eval(a) for a in call.args]
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}

    return tuple(args), kwargs

def _deserialize_expr(expr_str : str) -> type[ClauseElement]:
    """
    Deserialize a string representing a safe SQLAlchemy expression or raw SQL 
    into a ClauseElement. Only supports conversions to ClauseElements, 
    SQLAlchemy functions, and text(...). Python-native literals and operators 
    are rejected.

    Parameters
    ----------
    expr_str : str
        Serialized SQL/ClauseElement string.
    
    Returns
    -------
    type[ClauseElement]
        SQLAlchemy ClauseElement or child of ClauseElement to be passed to a 
        CheckConstraint object.
    
    Raises
    ------
    TypeError
        Raised in the case that an SQLAlchemy object is not returned
    ValueError
        Raised in the case that an AST node cannot be parsed or is unsupported
    """

    AST_OP_MAP : dict[type[ast.cmpop], Callable] = {
        ast.Gt : operator.gt,
        ast.Lt : operator.lt,
        ast.GtE : operator.ge,
        ast.LtE : operator.le,
        ast.Eq : operator.eq,
        ast.NotEq : operator.ne,
        ast.Add : operator.add,
        ast.Sub : operator.sub,
        ast.Mult : operator.mul,
        ast.Div : operator.truediv,
        ast.And : operator.and_,
        ast.Or : operator.or_
    }

    tree = ast.parse(expr_str, mode = 'eval')

    def _convert(node : Any):
        # ---- Literals ----
        if isinstance(node, ast.Constant):
            return sqlalchemy.literal(node.value)
        
        # ---- Column References ----
        if isinstance(node, ast.Name):
            return sqlalchemy.column(node.id)
        
        # ---- func.xxx(...) ----
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ('and_', 'or_'):
                args = [_convert(a) for a in node.args]

                if node.func.id == 'and_':
                    return sqlalchemy.and_(*args)
                
                if node.func.id == 'or_':
                    return sqlalchemy.or_(*args)

            if isinstance(node.func, ast.Name) and node.func.id == 'column':
                if len(node.args) != 1:
                    raise ValueError('column() takes exactly one argument')
                
                arg = node.args[0]
                if not isinstance(arg, ast.Constant) or not isinstance(arg.value, str):
                    raise ValueError('column() argument must be a string literal')
                
                return sqlalchemy.column(arg.value)

            if isinstance(node.func, ast.Name) and node.func.id == 'text':
                arg = _convert(node.args[0])
                return sqlalchemy.text(arg.value if hasattr(arg, 'value') else arg)
            
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'func':
                    func_name = node.func.attr
                    args = [_convert(a) for a in node.args]
                    return getattr(sqlalchemy.func, func_name)(*args)
            
            if isinstance(node.func, ast.Attribute):
                target = _convert(node.func.value)
                method = node.func.attr

                if method == 'in_':
                    args = [_convert(a) for a in node.args]
                    return target.in_(*args)
            
            raise ValueError(f'Unsupported function call : {ast.dump(node)}')
        
        # ----- Binary Operators (>, <, ==, etc.) ----
        if isinstance(node, ast.BinOp):
            left = _convert(node.left)
            right = _convert(node.right)
            op = AST_OP_MAP.get(type(node.op))
            if not op:
                raise ValueError(f'Unsupported operator : {ast.dump(node.op)}')
            return op(left, right)
        
        # ---- Comparisons ----
        if isinstance(node, ast.Compare):
            if len(node.ops) != 1 or len(node.comparators) != 1:
                raise ValueError('Chained comparisons are not supported')

            left = _convert(node.left)
            op_node = node.ops[0]
            right_node = node.comparators[0]

            if isinstance(op_node, ast.In):
                values = _convert(right_node)
                return left.in_(values)
            
            if isinstance(op_node, ast.NotIn):
                values = _convert(right_node)
                return ~left.in_(values)
            
            right = _convert(right_node)
            op = AST_OP_MAP.get(type(node.ops[0]))
            if not op:
                raise ValueError(f'Unsupported comparison : {ast.dump(node.ops[0])}')
            
            return op(left, right)
        
        # ---- Boolean expressions ----
        if isinstance(node, ast.BoolOp):
            values = [_convert(v) for v in node.values]
            op = AST_OP_MAP.get(type(node.op))
            if not op:
                raise ValueError(f'Unsupported boolean operator : {ast.dump(node.op)}')
            result = values[0]
            for v in values[1:]:
                result = op(result, v)
            return result
        
        # ---- Unary (NOT, -) ----
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -_convert(node.operand)
            if isinstance(node.op, ast.Not):
                from sqlalchemy import not_
                return not_(_convert(node.operand))
            raise ValueError(f'Unsupported unary operator : {ast.dump(node.op)}')

        if isinstance(node, (ast.Tuple, ast.List)):
            values = []
            for v in node.elts:
                converted = _convert(v)
                if hasattr(converted, 'value'):
                    values.append(converted.value)
                else:
                    values.append(converted)
            
            return values
        
        raise ValueError(f'Unsupported AST node : {ast.dump(node)}')
        
    result = _convert(tree.body)
    if not isinstance(result, ClauseElement):
        raise TypeError(f'Expression did not produce an SQLAlchemy object : {type(result)}')
    
    return result
    
def _serialize_expr(expr : type[ClauseElement]) -> str:
    """
    Serialize a ClauseElement into a string expression that can be passed to 
    _deserialize_expr.

    Parameters
    ----------
    expr : type[ClauseElement]
        ClauseElement object to serialize into a string
    
    Returns
    -------
    str
        Serialized ClauseElement
    """

    OPERATOR_SYMBOLS : dict[Callable, str] = {
        operator.eq: "==",
        operator.ne: "!=",
        operator.lt: "<",
        operator.le: "<=",
        operator.gt: ">",
        operator.ge: ">=",
        operator.add: "+",
        operator.sub: "-",
        operator.mul: "*",
        operator.truediv: "/",
        sqlalchemy.sql.operators.in_op : 'IN',
        sqlalchemy.sql.operators.not_in_op : 'NOT IN'
    }
    
    if expr is None:
        return None
    
    if isinstance(expr, sqlalchemy.sql.elements.TextClause):
        return f'text({expr.text!r})'

    if isinstance(expr, sqlalchemy.sql.functions.Function):

        args = ', '.join(_serialize_expr(a) for a in expr.clauses)

        return f'func.{expr.name}({args})'

    if isinstance(expr, sqlalchemy.sql.elements.ColumnClause):
        return f'column({expr.name!r})'

    if isinstance(expr, sqlalchemy.sql.elements.BinaryExpression):

        left = _serialize_expr(expr.left)
        right = _serialize_expr(expr.right)

        if expr.operator is sqlalchemy.sql.operators.in_op:
            return f'{left}.in_({right})'
        
        if expr.operator is sqlalchemy.sql.operators.not_in_op:
            return f'({left} not in {right})'
        
        op = OPERATOR_SYMBOLS.get(expr.operator)
        if not op:
            raise ValueError(f'Unsupported operator during serialization: {expr.operator}')

        return f'({left} {op} {right})'

    if isinstance(expr, sqlalchemy.sql.elements.UnaryExpression):
        
        element = _serialize_expr(expr.element)

        # Unary minus
        if expr.operator is operator.neg or str(expr.operator) == 'neg':
            return f'(-{element})'
        
        # SQL NOT (~)
        if expr.operator is sqlalchemy.sql.operators.inv:
            return f'not {element}'

        raise ValueError(f'Unsupported unary operator: {expr.operator}')
    
    if isinstance(expr, sqlalchemy.sql.elements.BindParameter):
        return repr(expr.value)

    if isinstance(expr, sqlalchemy.sql.elements.Label):
        return _serialize_expr(expr.element)

    if isinstance(expr, (str, int, float, bool)):
        return repr(expr)
    
    if isinstance(expr, sqlalchemy.sql.elements.BooleanClauseList):
        if expr.operator is operator.and_:
            func_name = 'and_'
        elif expr.operator is operator.or_:
            func_name = 'or_'
        else:
            raise ValueError(f'Unsupported boolean operator: {expr.operator}')
        
        args = ', '.join(_serialize_expr(clause) for clause in expr.clauses)

        return f'{func_name}({args})'
    
    if isinstance(expr, sqlalchemy.sql.elements.Grouping):
        return _serialize_expr(expr.element)

    if isinstance(expr, sqlalchemy.sql.ClauseElement):
        raise ValueError(f"Unsupported ClauseElement type during serialization: {type(expr)}")
    
    return repr(expr)
