"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Contains the LibraMetaClass object, which, as a child of SQLAlchemy's own 
DeclarativeMeta class, passes methods and attributes to all ORM objects 
inheriting from it. By default, all models belonging to a libra.Schema object 
will inherit functionality from this metaclass.
"""

# ==============================================================================

from __future__ import annotations
import decimal
from typing import Any
from typing import Iterator

import sqlalchemy
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_base import _declarative_constructor
from sqlalchemy.sql.schema import ScalarElementColumnDefault, CallableColumnDefault

# ==============================================================================
# Metaclass Methods

def _positional_init(self, *args : Any) -> None:
    """
    Initialize self with required, positional arguments - one for each column in 
    a model's mapped table.

    Parameters
    ----------
    *args : Any
        Argument for each column in a table in positional order of the columns.
    
    Raises
    ------
    ValueError
        If the expected number of positional arguments does not match the number
        of columns belonging to a model's mapped table.
    """

    if len(args) != len(self.__table__.columns):
        raise ValueError(f'Positional arguments required for each column. Got {len(args)}, expected {len(self.__table__.columns)}.')
    
    for column, ival in zip(self.__table__.columns, args):
        if ival is None and column.default:
            if isinstance(column.default, CallableColumnDefault) or hasattr(column.default, '__call__'):
                setattr(self, self._attrname[column.name], column.default.arg(''))
            else:
                setattr(self, self._attrname[column.name], column.default.arg)
        else:
            setattr(self, self._attrname[column.name], ival)

def _keyword_init(self, **kwargs : Any) -> None:
    """
    Initialize self with keyword arguments, where each keyword maps to a column 
    in a model's mapped table.

    Parameters
    ----------
    **kwargs : Any
        Keyword belongs to a column in a model, and the associated value is 
        mapped to that attribute of the model
    """

    _declarative_constructor(self, **kwargs)
    for column in self.__mapper__.columns:
        val = getattr(self, column.name, None)
        if val is None and column.default:
            if isinstance(column.default, CallableColumnDefault) or hasattr(column.default, '__call__'):
                setattr(self, self._attrname[column.name], column.default.arg(''))
            else:
                setattr(self, self._attrname[column.name], column.default.arg)
        else:
            setattr(self, self._attrname[column.name], val)

def _init(self, *args : Any | None, **kwargs : Any | None) -> None:
    """
    Constructor for a model.

    Parameters
    ----------
    *args : Any
        Positional arguments mapped to each column in a model's __table__ 
        attribute.
    **kwargs : Any
        Keyword arguments mapped to column names in a model's __table__ 
        attribute.
    
    Raises
    ------
    ValueError
        Raised if both positional and keyword arguments are passed in an attempt
        to instantiate an ORM instance.
    """

    if args and kwargs:
        raise ValueError('Either positional or keyword arguments accepted.')
    
    if args:
        _positional_init(self, *args)
    else:
        _keyword_init(self, **kwargs)

def _str(self) -> str:
    """Show all columns and their assigned values."""

    try:
        items = [(col.name, _normalize_decimal(col.type.python_type), getattr(self, col.name)) for col in self.__mapper__.columns]
    except NotImplementedError: # col.type.python_type is NotImplemented for non-standard types
        items = [(col.name, str, getattr(self, col.name)) for col in self.__mapper__.columns]
    
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

def _getitem(self, item : int | str) -> Any:
    """
    Get the associated value for a particular column; either by keyword or by 
    the column's position.

    Parameters
    ----------
    item : int | str
        Keyword associated with the column or integer position of the column 
        in the model's __table__ attribute.
    
    Returns
    -------
    Any
        The value associated with that column.
    """

    if isinstance(item, int):
        item = self.__table__.columns[item].name
    
    val = getattr(self, item)

    if isinstance(val, ScalarElementColumnDefault):
        val = val.arg

    return val

def _setitem(self, item : int | str, val : Any) -> None:
    """
    Set a column to a particular value. 

    Parameters
    ----------
    item : int | str
        Column name of column position within a models __table__ attribute.
    val : Any
        Value to associate with that column
    """

    if isinstance(item, int):
        item = self.__table__.columns[item].name
    
    if val is None and self.__table__.columns[item].default:
        val = self.__table__.columns[item].default
    
    setattr(self, item, val)

def _len(self) -> int:
    """
    Returns the number of columns in a model's __table__ attribute.

    Returns
    -------
    int
        Integer number of columns in a model.
    """

    return len(self.__table__.columns)

def _eq(self, other : type[LibraMetaClass]) -> bool:
    """
    Determines if two children of LibraMetaClass are equal on the values 
    contained in their primary key columns.

    Parameters
    ----------
    other : type[LibraMetaClass]
        A child of LibraMetaClass
    
    Returns
    -------
    bool
        True if values on all primary keys between the two instances are equal; 
        False if they are not.
    """

    return all([getattr(self, col.name) == getattr(other, col.name) for col in self.__table__.primary_key.columns])

def _repr(self) -> str:
    """Show only primary key columns and their assigned values."""
    
    try:
        items = [(col.name, _normalize_decimal(col.type.python_type), getattr(self, col.name)) for col in self.__mapper__.primary_key]
    except NotImplementedError:
        items = [(col.name, str, getattr(self, col.name)) for col in self.__mapper__.primary_key]
    
    _string = self.__class__.__name__ + '('
    for i, item in enumerate(items):
        key, _type_op, val = item[0], item[1], item[2]

        if isinstance(val, ScalarElementColumnDefault):
            val = val.arg

        if isinstance(val, str) and _type_op == str:
            _string += f'{key}=\'{val}\''
        else:
            _string += f'{key}={val}'
        
        if i != len(items) - 1:
            _string += ', '
    
    return _string + ')'

def _keys(self) -> list[str]:
    """Return a list of columns in a model's __table__ attribute"""

    return [c.name for c in self.__table__.columns]

def _values(self) -> list[Any]:
    """Return a list of values for each key in a model"""

    return [self[k] for k in self.keys()]

def _items(self) -> Iterator[tuple[str, Any]]:
    """Return a zipped tuple containing keys and values of a model"""

    return zip(self.keys(), self.values())

def _to_dict(self) -> dict[str, Any]:
    """Convert instance to a dict of form {<column_name> : <value>}"""

    return {col.name : getattr(self, col.name) for col in self.__table__.columns}

# ==============================================================================

class LibraMetaClass(DeclarativeMeta):
    """
    Metaclass instance to be used within the instantiation of an SQLAlchemy 
    declarative base class that will bequeath its methods onto all subclasses 
    inheriting from that declarative base class.
    """

    def __new__(cls, clsname : str, parents : tuple[Any], dct : dict[str, Any]) -> None:

        dct['__init__']        = _init
        dct['__str__']         = _str
        dct['__repr__']        = _repr
        dct['__getitem__']     = _getitem
        dct['__setitem__']     = _setitem
        dct['__len__']         = _len
        dct['__eq__']          = _eq
        dct['keys']            = _keys
        dct['values']          = _values
        dct['items']           = _items
        dct['to_dict']         = _to_dict

        dct['_col_registry'] = {}

        try:
            schema, tablename = dct['__tablename__'].split('.')
            dct['__tableowner__'], dct['__tablename__'] = schema, tablename

            SchemaBase = declarative_base(metadata = sqlalchemy.MetaData(schema = schema))

            for p in parents:
                if getattr(p, '_col_registry', {}):
                    SchemaBase._col_registry = p._col_registry
            
            parents = (SchemaBase, ) + parents
        
        except KeyError: # No __tablename__ or __table_args__
            pass

        except ValueError: # Not a schema-qualified name
            dct['_tableowner'] = None

        return super(LibraMetaClass, cls).__new__(cls, clsname, parents, dct)

    def __init__(cls, clsname : str, parents : tuple[Any], dct : dict[str, Any]) -> None:

        super(LibraMetaClass, cls).__init__(clsname, parents, dct)

        if hasattr(cls, '__table__'):
            cls._attrname = {col.name : col.key for col in cls.__mapper__.columns}
            cls._tabletype = parents[0].__name__
            cls._tableschema = parents[0].__module__.split('.')[-1]
        
# ==============================================================================

def _normalize_decimal(value : Any) -> Any:
    """
    Some SQLAlchemy Type objects' associated Python types map to a
    decimal.Decimal object. For those cases, we'd prefer a standard Python type
    of int or float.

    Parameters
    ----------
    value : Any
        Value of any type, where decimal.Decimal types are specifically cast to
        either an int or float Python type. 
    
    Returns
    -------
    Any
        Input value if type is not decimal.Decimal, otherwise a translated 
        float or int Python type.
    """

    if not isinstance(value, decimal.Decimal):
        return value

    if value == value.to_integral_value():
        return int(value)
    else:
        return float(value)
    