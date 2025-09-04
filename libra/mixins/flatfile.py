"""
Brady Spears
7/16/25

Contains the `FlatFile` Mixin class. The FlatFile class has functionality to 
either convert a single line of a string into an ORM instance or convert the 
ORM instance to a string.
"""

# ==============================================================================

from __future__ import annotations
from datetime import datetime
import re
from typing import Self
import pdb

import sqlalchemy

# ==============================================================================

class FlatFileMixin:
    """
    Contains functionality to read or write a string to or from an ORM instance.
    """

    def __new__(cls, *args, **kwargs) -> None:
        """
        Extends the __new__() method up the MRO to add a _format_string property
        to the child class.
        """
        
        cls._format_string = string_formatter(cls.__base__.metadata, [c.name for c in cls.__table__.columns])

        return super().__new__(cls)

    def to_string(cls) -> str:
        """
        """

        return _to_string(cls)

    @classmethod
    def from_string(cls, line : str, default_on_error : list[str] | None = None) -> Self:
        """
        """

        return _from_string(cls, line, default_on_error)

# ==============================================================================

def string_formatter(meta : sqlalchemy.MetaData, structure : list[str]) -> str:
    """
    Get a string substitution formatter for a given ORM instance. Columns 
    belonging to the ORM instance must have the 'format' key defined within the 
    Column object's 'info' dictionary. If not defined, string_formatter will 
    return a string formatting 

    Parameters
    ----------
    meta : sqlalchemy.MetaData
        SQLAlchemy MetaData object containing features of a database 
    structure : list[str]
        List of qualified column names within the MetaData object. Note: Columns
        passed to structure must contain the 'format' keyword inside the 
        Column's 'info' dictionary.
    
    Returns
    -------
    str
        Returns substitution-formatted string in the case that each Column.info
        dictionary's 'format' key is defined
    """

    tabledct = dict([(itable.name, itable) for itable in list(meta.tables.values())])

    colfmtdct = {}
    for t in list(meta.tables.values()):
        for col in t.columns:
            _format = col.info.get('format', None)

            colfmtdct[col.name] = _format

    structfmt = []
    for idx, item in enumerate(structure):
        if item in tabledct:
            itabfmt = ' '.join(["{{{}.{}:{}}}".format(idx, c.name, c.info.get('format', ''))
                for c in tabledct[item].columns])
            structfmt.append(itabfmt)
        elif item in colfmtdct:
            # e.g. {0:format} {1:format}
            structfmt.append("{{{}:{}}}".format(idx, colfmtdct[item]))

    return ' '.join(structfmt) + '\n'

def _from_string(cls : type[FlatFileMixin], line : str, default_on_error : list[str] | None = None) -> type[FlatFileMixin]:

    results = []
    cursor = 0

    # regex to extract {index:specifier}
    token_re = re.compile(r"\{(\d+):([^}]*)\}")

    for match in token_re.finditer(cls._format_string):
        _, spec = int(match.group(1)), match.group(2)

        # Handle datetime separately (identified by having %Y, %m, etc.)
        if "%" in spec:
            width = len(datetime.now().strftime(spec))
            raw = line[cursor:cursor+width]
            cursor += width
            results.append(datetime.strptime(raw.strip(), spec))
            continue

        # NOTE: Only datetime objects and strptime formatting are currently 
        # supported in custom cases under Libra. It's possible that other 
        # types with separate format identifiers exist. Examples would include 
        # datetime.timedelta objects (SQLAlchemy equivalent is Interval object),
        # pickle objects (SQLAlchemy equivalent is PickleType object), etc.

        # Extract width and type
        m = re.match(r"(\d+)(?:\.\d+)?([dfs])", spec)
        if not m:
            raise ValueError(f"Unsupported format spec: {spec}")
        width, typ = int(m.group(1)), m.group(2)

        raw = line[cursor:cursor+width]
        cursor += width

        # These do not include some native Python format identifiers - need to extend
        if typ == "d":
            results.append(int(raw.strip()))
        elif typ == "f":
            results.append(float(raw.strip()))
        elif typ == "s":
            results.append(raw.strip())
        else:
            results.append(raw.strip())

        # Skip a space if it exists in the formatted string
        if cursor < len(line) and line[cursor] == " ":
            cursor += 1
    
    return cls(*results)

def _to_string(cls : type[FlatFileMixin]) -> str:
    return cls._format_string.format(*cls)

# ==============================================================================
