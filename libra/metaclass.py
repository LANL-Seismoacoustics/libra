"""
Brady Spears
5/5/25

Contains the `MetaClass` object, which is a child of SQLAlchemy's 
DeclarativeMeta class. The `MetaClass` object defines methods to operate on 
any declarative base model inheriting from from `MetaClass`.
"""

# ==============================================================================

from __future__ import annotations
from typing import Any, List
from typing import Optional, Self, Type, Union, Iterator

import sqlalchemy
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeMeta, DeclarativeBase
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_base import _declarative_constructor
from sqlalchemy.sql.schema import ScalarElementColumnDefault
from sqlalchemy.sql.schema import CallableColumnDefault

# ==============================================================================

def _positional_init(self, *args : Any) -> None:
    """
    TODO: _positional_init docstring
    """

    if len(args) != len(self.__table__.columns):
        raise ValueError('Positional arguments required for each column.')
    
    for column, ival in zip(self.__table__.columns, args):
        # This can be done better
        if ival is None and column.default:
            setattr(self, self._attrname[column.name], column.default)
        else:
            setattr(self, self._attrname[column.name], ival)

def _keyword_init(self, **kwargs : Any) -> None:
    """
    TODO: _keyword_init docstring
    """

    _declarative_constructor(self, **kwargs)
    for column in self.__mapper__.columns:
        val = getattr(self, column.name, None)
        if val is None and column.default:
            setattr(self, self._attrname[column.name], column.default)
        else:
            setattr(self, self._attrname[column.name], val)
        
# ==============================================================================

def _init(self, *args : Optional[Any], **kwargs : Optional[Any]) -> None:
    """
    TODO: _init docstring
    """

    if args and kwargs:
        raise ValueError('Either positional or keyword arguments accepted.')
    
    if args:
        _positional_init(self, *args)
    else:
        _keyword_init(self, **kwargs)

def _str(self) -> str: 
    """
    TODO: _str() docstring
    """

    items = [(col.name, col.type.python_type, getattr(self, col.name)) for col in self.__mapper__.columns]

    _string = self.__class__.__name__ + '('
    for i, item in enumerate(items):
        key, _type_op, val = item[0], item[1], item[2]
        if isinstance(val, ScalarElementColumnDefault):
            val = val.arg
        
        if isinstance(val, str) and _type_op == str:
            _string += f'{key}=\'{_type_op(val)}\''
        else:
            _string += f'{key}={val}'

        if i != len(items) - 1:
            _string += ', '

    return _string + ')'

def _repr(self) -> str: 
    """
    TODO: _repr() docstring
    """

    items = [(col.name, getattr(self, col.name)) for col in self.__mapper__.primary_key]

    _string = self.__class__.__name__ + '('
    for i, item in enumerate(items):
        key, val = item[0], item[1]

        if isinstance(val, ScalarElementColumnDefault):
            val = val.arg
        
        if isinstance(val, bool or int or float) or val is None:
            _string += f'{key}={str(val)}'
        else:
            _string += f'{key}=\'{str(val)}\''

        if i != len(items) - 1:
            _string += ', '

    return _string + ')'

def _getitem(self, item : Union[int, str]) -> Any: 
    """
    TODO: _getitem() docstring
    """

    if isinstance(item, int):
        item = self.__table__.columns[item].name
    
    val = getattr(self, item)

    if isinstance(val, ScalarElementColumnDefault):
        val = val.arg
    
    return val

def _setitem(self, item : Union[int, str], val : Any) -> None: 
    """
    TODO: _setitem() docstring
    """

    if isinstance(item, int):
        item = self.__table__.columns[item].name
    
    if val is None and self.__table__.columns[item].default:
        val = self.__table__.columns[item].default

    setattr(self, item, val)

def _len(self) -> int: 
    """
    TODO: _len() docstring
    """

    return len(self.__table__.columns)

def _eq(self, other : Self) -> bool: 
    """
    TODO: _eq() docstring
    """

    return all([getattr(self, col.name) == getattr(other, col.name) for col in self.__table__.primary_key.columns])

def _update_docstring(cls) -> str:
    """
    TODO: _update_docstring() docstring
    """

    return NotImplementedError

def _keys(cls) -> list[str]:
    return [c.name for c in cls.__table__.columns]

def _values(cls) -> list[Any]:
    return [cls[k] for k in cls.keys()]

def _items(cls) ->  Iterator[tuple[str, Any]]:
    return zip(cls.keys(), cls.values())

def _to_dict(cls) -> dict[str, Any]:
    return {k : v for k, v in cls.items()}


# def _to_dict(cls) -> dict:

#     keys = [c.name for c in cls.__table__.columns]

#     return {k : getattr(cls, k) for k in keys}

# ==============================================================================

class MetaClass(DeclarativeMeta):
    """
    Metaclass to be used within the instantiation of an SQLAlchemy declarative 
    base class, that will bequeath its methods onto all subclasses inheriting 
    from that declarative base class.
    """

    def __new__(cls, clsname, parents, dct) -> None:

        # Child classes will have methods/data put into 'dct'
        dct['__init__']    = _init
        dct['__str__']     = _str
        dct['__repr__']    = _repr
        dct['__getitem__'] = _getitem
        dct['__setitem__'] = _setitem
        dct['__len__']     = _len
        dct['__eq__']      = _eq
        dct['keys']        = _keys
        dct['values']      = _values
        dct['items']       = _items
        dct['to_dict']     = _to_dict

        # Equal methods that compare on unique keys & all columns would be useful

        dct['_col_registry'] = {}

        try:
            schema, tablename = dct['__tablename__'].split('.')
            dct['__tableowner__'], dct['__tablename__'] = schema, tablename

            # class SchemaBase(DeclarativeBase):
            #     metadata = sqlalchemy.MetaData(schema = schema)
            SchemaBase = declarative_base(metadata = sqlalchemy.MetaData(schema=schema))
            
            for p in parents:
                if getattr(p, '_col_registry', {}):
                    SchemaBase._col_registry = p._col_registry
            
            parents = (SchemaBase, ) + parents
        
        except KeyError: # No __tablename__ or __table_args__
            pass

        except ValueError: # Not a schema-qualified name
            dct['_tableowner'] = None

        return super(MetaClass, cls).__new__(cls, clsname, parents, dct)
    
    def __init__(cls, clsname, parents, dct) -> None:
        super(MetaClass, cls).__init__(clsname, parents, dct)

        if hasattr(cls, '__table__'):
            cls._attrname = {col.name : col.key for col in cls.__mapper__.columns}
            cls.__doc__ = _update_docstring(cls)
            cls._tabletype = parents[0].__name__
            cls._tableschema = parents[0].__module__.split('.')[-1]
