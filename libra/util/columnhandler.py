from __future__ import annotations
from abc import ABC, abstractmethod
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
    def construct(self, name : str, coldef : Dict[str, Any], type_key : str = 'type') -> Column:
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
        'regex', 'min', 'max', 'description', 'format'
    ]
    
    def construct(self, name : str, coldef : Dict[str, Any], type_key : str = 'type') -> Column:
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
            if key == type_key:
                _type = self.type_map.get(value.__class__, value)
                if _type != value:
                    _type = _type(**value.__dict__)
            
            if key in self.info_keys:
                info.update({key : value})
            else:
                kwargs.update({key : value})

        del kwargs[type_key]
        return Column(name, _type, info = info, **kwargs)

    def deconstruct(self):
        return NotImplementedError
    
# ==============================================================================