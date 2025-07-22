"""
Brady Spears
5/5/25

Handler objects, herein contained, are objects which are responsible for the 
conversion of text-based object definitions to and from SQLAlchemy ORM objects.
Part of Abstract Base Class `Handler` these objects contain methods for 
constructing and deconstructing SQLAlchemy ORM objects. Built-in children of 
type `Handler` include the `TypeHandler`, which constructs and deconstructs 
SQLAlchemy.types objects to/from regular Python strings; the `ColumnHandler`, 
which constructs and deconstructs SQLAlchemy.Column objects to/from regular 
Python dictionaries; and the `ConstraintHandler`, which constructs and 
deconstructs children of SQLAlchemy.constraint objects, including
PrimaryKeyConstraint and UniqueConstraint.
"""

# ==============================================================================

import re
import ast
import pdb
import inspect
import importlib
import datetime
from abc import ABC, abstractmethod
from functools import singledispatch
from typing import List, Any, TypeVar
from copy import deepcopy

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import (Constraint, PrimaryKeyConstraint, UniqueConstraint)
# Load all SQLAlchemy Types for use in TypeMap hash
# Generic "CamelCase" Types
from sqlalchemy.types import (
    BigInteger, Boolean, Date, DateTime, Enum, Double, Float, Integer, Interval,
    LargeBinary, Numeric, PickleType, SmallInteger, String, Text, Time, Unicode,
    UnicodeText, Uuid
)
# SQL Standard & Multiple Vendor "UPPERCASE" Types
from sqlalchemy.types import (
    ARRAY, BIGINT, BINARY, BLOB, BOOLEAN, CHAR, CLOB, DATE, DATETIME, DECIMAL,
    DOUBLE, DOUBLE_PRECISION, FLOAT, INT, JSON, INTEGER, NCHAR, NVARCHAR, 
    NUMERIC, REAL, SMALLINT, TEXT, TIME, TIMESTAMP, UUID, VARBINARY, VARCHAR
)
from sqlalchemy.inspection import inspect as _inspect

from .util import Evaluator

# ==============================================================================

SaType = TypeVar('SaType', bound = sqlalchemy.types)

# ==============================================================================

TYPEHASH = {
    'BigInteger' : BigInteger,
    'Boolean' : Boolean,
    'Date' : Date,
    'DateTime' : DateTime,
    'Enum' : Enum,
    'Double' : Double,
    'Float' : Float,
    'Integer' : Integer,
    'Interval' : Interval,
    'LargeBinary' : LargeBinary,
    'Numeric' : Numeric,
    'PickleType' : PickleType,
    'SmallInteger' : SmallInteger,
    'String' : String,
    'Text' : Text,
    'Time' : Time,
    'Unicode' : Unicode,
    'UnicodeText' : UnicodeText,
    'Uuid' : Uuid,
    'ARRAY' : ARRAY,
    'BIGINT' : BIGINT,
    'BINARY' : BINARY,
    'BLOB' : BLOB,
    'BOOLEAN' : BOOLEAN,
    'CHAR' : CHAR,
    'CLOB' : CLOB,
    'DATE' : DATE,
    'DATETIME' : DATETIME,
    'DECIMAL' : DECIMAL,
    'DOUBLE' : DOUBLE,
    'DOUBLE_PRECISION' : DOUBLE_PRECISION,
    'FLOAT' : FLOAT,
    'INT' : INT,
    'JSON' : JSON,
    'INTEGER' : INTEGER,
    'NCHAR' : NCHAR,
    'NVARCHAR' : NVARCHAR,
    'NUMERIC' : NUMERIC,
    'REAL' : REAL,
    'SMALLINT' : SMALLINT,
    'TEXT' : TEXT,
    'TIME' : TIME,
    'TIMESTAMP' : TIMESTAMP,
    'UUID' : UUID,
    'VARBINARY' : VARBINARY,
    'VARCHAR' : VARCHAR
}

# ==============================================================================

class TypeMap:

    def __init__(self, override : dict[str, SaType] | None = None) -> None:
        """
        Initializes a TypeMap object which contains a mapping from strings to 
        SQLAlchemy "CamelCase" and "UPPERCASE" type objects. Default behavior 
        sets the mapping to the above 'typehash' variable, with options to 
        override any of its keys with a different value.

        NOTE: Keys and values are required to be unique across self._mapping

        Parameters
        ----------
        override : dict[str, SaType]
            Dictionary mapping a unique string to a unique SQLAlchemy type class
        """

        self._mapping = deepcopy(TYPEHASH)

        if override:
            for key, value in override.items():
                self()[key] = value
    
    def __call__(self, reverse : bool = False) -> dict[str, SaType] | dict[SaType, str]:
        
        if reverse:
            return NotImplementedError
        
        return self._mapping
    
    def __getitem__(self, identifier : str | SaType) -> SaType | str:

        if isinstance(identifier, str):
            return self._mapping[identifier]
        else:
            return [key for key, val in self._mapping.items() if val == identifier]
    
    def __setitem__(self, key : str, value : SaType) -> None:
        """
        Updates self._mapping to include the passed key-value pair. Keys should 
        be unique across all self._mapping keys, so any existing keys will be 
        remapped to the passed value. Values should be unique across all 
        self._mapping values, so any existing values will be remapped to the 
        passed key. If both the passed key and value exist in self._mapping, 
        entries containing the key and value will be replaced.

        Parameters
        ----------
        key : str
        value : object

        Examples
        --------
        Mapping an existing string to a new type:
        >>> from sqlalchemy.dialects.oracle import VARCHAR2
        >>> typemap = TypeMap()['String'] = VARCHAR2

        Mapping an existing type to a new string:
        >>> typemap = TypeMap()['VARCHAR2'] = String

        Mapping a new type to a new string:
        >>> from sqlalchemy.dialects.mysql import BIT
        >>> typemap = TypeMap()['BIT'] = BIT

        Mapping an existing string to an existing type:
        >>> typemap = TypeMap()['String'] = VARCHAR
        """

        if value in self._mapping.values():
            # Find key associated with that value & delete it
            _keytoremove = [_key for _key, _val in self._mapping.items() if _val == value][0]
            del self._mapping[_keytoremove]
        
        self._mapping[key] = value

# ==============================================================================

class Handler(ABC):
    """Abstract class for constructing & deconstructing various objects"""

    @abstractmethod
    def construct(self) -> Any:
        """Builds desired object given a plain-text description"""
        ...

    @abstractmethod
    def deconstruct(self) -> Any:
        """Builds plain-text description of an object given the object"""
        ...


class TypeHandler(Handler):

    def __init__(self, typemap : TypeMap = TypeMap()) -> None:
        self.typemap = typemap
    
    def construct(self, type_str : str) -> SaType:
        """
        From a string declaration of a particular SQLAlchemy Type object, return 
        the SQLAlchemy Type object, while evaluating any args and kwargs as 
        literals, passing to the type object before returning to the user.
        NOTE: Support for overriding types is provided via the 'typemap' 
         attribute, which maps unique strings to unique SQLAlchemy type objects.
         When overriding a predefined string, any args or kwargs used in 
         'type_str' will be passed on to the mapped SQLAlchemy type.

        Parameters
        ----------
        type_str : str
            String representation of the SQLAlchemy type object, with args and 
            kwargs defined as they would be in in-line Python declarations.

        Examples
        --------
        Using default behavior:
        >>> sql_type = TypeHandler().construct('Float(precision = 53)')
        >>> sql_type
        Float(precision=53)

        Using custom typemap object:
        >>> from sqlalchemy.dialects.oracle import VARCHAR2
        >>> typemap = TypeMap()['String'] = VARCHAR2
        >>> sql_type = TypeHandler(typemap).construct('String(128)')
        >>> sql_type
        VARCHAR2(128)
        """

        try:
            _inputs = re.findall(r'\(([^)]*)\)', type_str)
        except IndexError:
            _inputs = None

        _sa_type_str = re.split(r'\([^)]*\)', type_str)[0]

        try:
            _sa_type = self.typemap[_sa_type_str]
        except KeyError:
            raise KeyError(f'Key \'{_sa_type}\' not found in TypeMap.')
        
        match _inputs:
            # _sa_type something like "DateTime()"
            case ['']: return _sa_type()

            # _sa_type something like "Integer"
            case None: return _sa_type

            # _sa_type something like "String(30)" or "Float(precision = 53)"
            case _:
                _args, _kwargs = [], {}
                for _input in _inputs:
                    if '=' in _input: # Register as kwargs
                        _key, _value = _input.split('=', 1)
                        _kwargs.update({_key.strip() : ast.literal_eval(_value.strip())})
                    else:
                        _args.append(ast.literal_eval(_input))

                return _sa_type(*_args, **_kwargs)

    def deconstruct(self, satype : SaType) -> str:

        nondef_params = {}
        signature = inspect.signature(satype.__init__)

        for name, param in signature.parameters.items():
            try:
                if satype.__dict__[name] != param.default:
                    nondef_params.update({name : satype.__dict__[name]})
            except KeyError:
                pass
        
        # Gently massage the return string
        return_str = f'{satype.__class__.__name__}'
        if nondef_params != {}:
            return_str += '('
            for i, (key, val) in enumerate(nondef_params.items()):
                return_str = f'{return_str}{key}={val}'
                if i != len(nondef_params.keys()) - 1:
                    return_str += ', '
            return_str += ')'

        return return_str


class ColumnHandler(Handler):
    
    def __init__(self, typehandler : TypeHandler = TypeHandler(), evaluator : Evaluator = Evaluator()) -> None:
        self.typehandler = typehandler
        self.evaluator = evaluator
    
    # TODO: Might be beneficial to move this out so ConstraintHandler can use it too
    @staticmethod
    def _remove_keys(_input_dict : dict, _keys : list[str]) -> dict[str, str]:
        for key in _keys:
            try:
                del _input_dict[key]
            except KeyError:
                pass
    
    # TODO: Might be beneficial to move this out so ConstraintHandler can use it too
    @staticmethod
    def _remap_keys(_input_dict : dict, _mapping_dict : dict[str, str]) -> dict[str, str]:

        new_dict = {}
        for key, val in _input_dict.items():
            if key in _mapping_dict.keys():
                if _mapping_dict[key] == 'info':
                    if 'info' not in new_dict.keys(): 
                        new_dict['info'] = {key : val}
                    else:
                        if isinstance(new_dict['info'], str):
                            new_dict['info'] = {}
                        new_dict['info'].update({key : val})
                else:
                    new_dict[_mapping_dict[key]] = val
            else:
                new_dict[key] = val
        
        return new_dict
    
    @staticmethod
    def _remap_nulls(_input_dict : dict, _null_map : dict[str, None]) -> dict[str, str | None]:
        """Remaps certain input strings to None values"""

        for key, val in _input_dict.items():
            if isinstance(val, str):
                if val in _null_map.keys():
                    _input_dict[key] = _null_map[val]
        
        return _input_dict

    def construct(self, col_name : str, coldef_dict : dict[str, str]) -> Column:
        _type = self.typehandler.construct(coldef_dict['sa_coltype'])
        del coldef_dict['sa_coltype']

        _mapping = {
            'column_alias' : 'key',
            'description'  : 'info',
            'default_val'  : 'default',
            'null_allowed' : 'nullable'
        }

        _null_map = {'-' : None}

        col_dict = self._remap_keys(coldef_dict, _mapping)
        col_dict = self._remap_nulls(col_dict, _null_map)

        for key, val in col_dict.items():
            col_dict[key] = self.evaluator(val)

        return Column(col_name, _type, **col_dict)

    def deconstruct(self, col_name : str, column : Column) -> dict[str, str | dict]:

        # Don't include any standard default arguments in Column initialization
        # Or any additional parameters that are specified here
        _additional_exclude_params = {
            'nullable' : True,
            'default' : None
        }
        
        nondef_params = {}
        signature = inspect.signature(column.__init__)
        for name, param in signature.parameters.items():
            try:
                if column.__dict__[name] != param.default:
                    nondef_params.update({name : column.__dict__[name]})
            except KeyError:
                pass
        
        new_params = {'sa_coltype' : self.typehandler.deconstruct(column.type)}

        for key, val in nondef_params.items():
            if key in _additional_exclude_params.keys() and val == _additional_exclude_params[key]:
                pass
            else:
                new_params[key] = val

        # TODO: Deal with ScalarElementColumnDefault & Info Dictionary
        
        return {col_name : new_params}


class ConstraintHandler(Handler):
    def construct(self, con_list : list[dict[str, list[str]]]) -> tuple[Constraint]:
        
        constraints = []
        for constraint in con_list:
            for key_type, columns in constraint.items():
                match key_type:
                    case 'pk':
                        constraints.append(PrimaryKeyConstraint(*columns))
                    case 'uq':
                        constraints.append(UniqueConstraint(*columns))
                    case _:
                        raise NotImplementedError('Foreign Keys, Check Constraints, and Index values not currently supported under Libra.')
        
        return tuple(constraints)
    
    def deconstruct(self, constraints : tuple[type[Constraint]]) -> list[dict[str, List[str]]]:
        
        return_con = []
        for con in constraints:
            inspector = _inspect(con)

            columns = inspector._pending_colargs

            if type(con) == PrimaryKeyConstraint:
                return_con.append({'pk' : columns})
            elif type(con) == UniqueConstraint:
                return_con.append({'uq' : columns})
            else:
                raise NotImplementedError
            
        return return_con

# ==============================================================================
