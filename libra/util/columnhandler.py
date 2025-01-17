from __future__ import annotations
from abc import ABC, abstractmethod
import importlib
from typing import Any, Dict
from typing import Optional, Type

from sqlalchemy import Column

from .typing import _SQLType

# ==============================================================================

class ColumnHandler(ABC):
    """
    ColumnHandler is an abstract base class intended to re-cast text- or object-
    based definitions of SQLAlchemy Columns as true sqlalchemy.Column objects.
    The ColumnHandler object has two abstract methods - construct, which is used
    to translate fields of a column definition dictionary to a Column object,
    and deconstruct, which is used to translate a Column object back to a 
    column definition dictionary.

    Attributes
    ----------
    type_map : Dict[Type[_SQLType], Type[_SQLType]]]
        Mapping dictionary for sqlalchemy datatype objects. Useful to define if 
        there is a desire to translate types to/from dialect-specific or custom
        sqlalchemy datatypes.

    Methods
    -------
        

    Notes
    ----- 
    Input arguments of the specified type are passed on to the 
    mapped type. When explicitly declaring type_map, caution should be
    exercised such that arguments of one type will not interfere with 
    the resultant mapped type.
    """

    @property
    @abstractmethod
    def type_map(self):
        return {}
    
    @abstractmethod
    def construct(self, name : str, coldef : Dict[str, Any], type_key : str = 'data_type') -> Column:
        """Constructs sqlalchemy.Column from text-based description"""

    @abstractmethod
    def deconstruct(self) -> Dict:
        """Deconstructs sqlalchemy.Column object to a text-based dictionary"""

# ==============================================================================

class Default_ColumnHandler(ColumnHandler):
    """
    # TODO: Fix this docstring format
    """

    type_map = {}
    info_keys : list[str] = [
        'description', 'author'
    ]
    
    def construct(self, name : str, coldef : Dict[str, Any], type_key : str = 'data_type') -> Column:
        """
        Constructs an SQLAlchemy Column object from a provided column definition
        dictionary. All key-value pairs in coldef are passed onto the 
        sqlalchemy.Column.__init__() method, except those keywords which are 
        defined in the self.info_keys. Those key-value pairs are appended to the
        Column object's 'info' dictionary attribute.

        Paramters
        ---------
        name : str
            Associated name of a column
        coldef : Dict[str, Any]
            Column definition dictionary. Note: 'type' keyword must be specified
            in this dictionary in order to cast the Column to the appropriate 
            SQLAlchemy type object.
        
        Returns
        -------
        Column
            SQLAlchemy Column object
        """

        kwargs, info = {}, {}
        for key, value in coldef.items():

            # Handle data typing
            if key == type_key:
                _type = self.cast_type(value)
                
            if key in self.info_keys:
                info.update({key : value})
            else:
                kwargs.update({key : value})

        del kwargs[type_key]
        return Column(name, _type, info = info, **kwargs)

    def deconstruct(self):
        return NotImplementedError
    
    def cast_type(self, _t : str | type[_SQLType]) -> _SQLType:

        # This function is going to get insane.
        if type(_t) == str:
            args, kwargs = [], {}
            if '(' in _t and ')' in _t and (_t.index('(') + 1 != _t.index(')')):
                left, right = _t.index('('), _t.index(')')
                inputs = [i.replace(' ', '') for i in _t[left + 1:right].split(',')]
                _type_call = _t[0:left]
                for param in inputs:
                    if '=' in param:
                        key, value = param.split('=')
                        kwargs[key] = value
                    else:
                        args.append(param)
            else:
                _type_call = _t.replace('()', '')
            
            modules = ['sqlalchemy']
            mod = importlib.import_module('sqlalchemy')

            _type = getattr(mod, _type_call)(*args, **kwargs)
        
        else:
            _type = self.type_map.get(_t.__class__, _t)
            if _type != _t:
                _type = _type(**_t.__dict__)
        
        return _type
    
# ==============================================================================