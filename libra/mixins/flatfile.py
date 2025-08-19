"""
Brady Spears
7/16/25

Contains the `FlatFile` Mixin class. The FlatFile class has functionality to 
either convert a single line of a string into an ORM instance or convert the 
ORM instance to a string.
"""

# ==============================================================================

from __future__ import annotations
import pdb
import csv
from datetime import datetime
from io import StringIO
from typing import Any
from typing import Self

from sqlalchemy import DateTime

# ==============================================================================

class FlatFile:
    """
    Contains functionality to read or write a string to or from an ORM instance.

    Methods
    -------
    from_string
        Reads a 
    to_string
    """

    def from_string(self, line : str, delimiter : str = ' ', fixed_length : bool | None = None, dtime_format : str | None = None) -> Self:
        """
        Construct a mapped table instance from a correctly-formatted flat file 
        line. 

        Parameters
        ----------
        line : str
            Flat file line passed as a delimited string
        delimiter : str, optional
            Single character delimiter to join values of a model by. Default is
            whitespace ' ' not contained in double quotes. (i.e. 'val1 val2 
            val3 "My val4"' maps to ['val1', 'val2', 'val3', "My val4"])
        fixed_length : bool, optional
            Optional flag to force fixed-length formatting to be used or 
            unused, which requires the info['format'] attribute to be defined 
            for each column belonging to the ORM.
        """

        return _from_string(self, line, delimiter, fixed_length, dtime_format)
    
    def to_string(cls, delimiter : str = ' ', fixed_length : bool | None = None) -> str:
        """
        """

        return _to_string(cls, delimiter, fixed_length)

# ==============================================================================

def _str(s : Any) -> str:
    """If an input interpretted as a string has spaces, quote it"""

    s = str(s)

    if ' ' in s:
        s = f'"{s}"'
    
    return s

def _from_string(cls,
    line : str, 
    delimiter : str, 
    fixed_length : bool | None,
    dtime_format : str | None
    ) -> Self:
    """
    Construct a mapped table instance from a correctly-formatted flat file 
    line. 

    Parameters
    ----------
    line : str
        Flat file line passed as a delimited string
    delimiter : str or None
        Common delimiter to split 'line' at. Default is whitespace ' ' not 
        contained in double quotes. (i.e. 'val1 val2 val3 "My val4"' maps 
        to ['val1', 'val2', 'val3', "My val4"])
    fixed_length : bool or None
        Optional flag to force fixed-length formatting to be used or 
        unused, which requires the ORM's info['format'] attribute to be 
        defined.

    Notes
    -----
    `from_string` will first consult each `Column` object attribute, looking 
    for the 'format' keyword in the `Column's` 'info' dictionary. If found, 
    'from_string' will automatically attempt to read the input string with 
    fixed-length values as specified by the value associated with 'format'.
    This behavior can be toggled with the 'fixed_length' input parameter.
    """

    if not dtime_format:
        dtime_format = '%Y-%m-%d %H:%M:%S'

    if fixed_length == True:
        return NotImplementedError('Fixed Length support not implemented yet')

    reader = csv.reader(StringIO(line), delimiter = delimiter)
    values = next(reader)

    if len(values) != len(cls.__mapper__.columns):
        raise ValueError(f'Value unpack mismatch (expected {len(cls)}, got {len(values)})')

    for key, val in zip(cls.keys(), values):
        val = val.strip().strip('"') # Get rid of leading/trailing quotation marks and spaces

        coltype = cls.__table__.columns[key].type
        parse_func = coltype.python_type # Python type associated with the column
        
        try:
            setattr(cls, key, parse_func(val)) # Works with standard types
        except TypeError:
            match coltype:
                case DateTime():
                    parse_func = lambda s : datetime.strptime(s, dtime_format) 
                    setattr(cls, key, parse_func(val))
                case _:
                    return NotImplementedError
    
    return cls

def _to_string(cls,
    delimiter : str,
    fixed_length : bool | None
    ) -> str:
    """
    From a mapped table instance, output the model as a string.

    Parameters
        ----------
        delimiter : str
            Single character delimiter to join values of a model by
        fixed_length : bool or None
            Flag to force fixed-length formatting to be used or unused, which 
            requires the ORM's info['format'] attribute to be defined. If 
            True, the output string will be formatted according each column's 
            specified format.
    """
    
    if fixed_length == True:
        return NotImplementedError('Fixed Length support not implemented yet')
    
    return delimiter.join([_str(v) for v in cls.values()]) + '\n'

# ==============================================================================
