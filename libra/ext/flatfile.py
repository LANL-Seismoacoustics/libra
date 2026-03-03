"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Contains the `FlatFileMixin` object, which extends flatfile read/write 
functionality to SQLAlchemy Table instances. 
"""

# ==============================================================================

import decimal
import warnings
from datetime import datetime
from typing import Callable, Self

import sqlalchemy
from sqlalchemy.sql.schema import ScalarElementColumnDefault

from libra import LibraMetaClass

# ==============================================================================

def dtfn(x, fmt):
    return datetime.strptime(x, fmt)

PARSEHASH : dict[type, Callable] = {
    str : lambda x: str(x),
    int : lambda x: int(x),
    float : lambda x: float(x),
    datetime : dtfn,
    decimal.Decimal : lambda x: int(x)
}

# ==============================================================================

class FlatFileMixin:

    @property
    def _format_string(self) -> str | None:
        return _string_formatter(self)

    @property
    def _format_widths(self) -> list[int] | None:
        
        widths = [col.info.get('width', None) for col in self.__table__.columns]

        if not all(_w is not None for _w in widths):
            warnings.warn('\'width\' keyword missing from one or more column definitions. Defaulting to variable-width flatfile writer.')

        return widths if all(_w is not None for _w in widths) else None

    def to_string(self, fixed_width : bool = True, delimiter : str = ',') -> str:
        """
        Convert the values contained in an SQLAlchemy Table ORM instance into a 
        string. If able to resolve the _format_string property of cls, go ahead 
        and assume fixed_width, if not, rely on whitespace parsing. Override 
        behavior with the 'fixed_width' flag.

        Parameters
        ----------
        cls : type[LibraMetaclass]
            Instantiated SQLAlchemy Table ORM instance with populated values 
            for each column in the table.
        fixed_width : bool
            Output string uses fixed-width format so long as every Column 
            object in the Table instance contains the 'format' keyword in its 
            'info' dictionary. If even one column's format is not defined, 
            fixed-width support is dropped in favor of a delimited output 
            string. Set to 'False' to override fixed-width behavior even if 
            'format' is defined for all columns.
        delimiter : str
            Custom delimiter in the case that fixed-width formatting is not 
            used.
        
        Returns
        -------
        str
            Values contained in the Table instance parsed out as a fixed-width 
            or variable-width delimited flatfile.
        """

        return _to_string(self, fixed_width, delimiter)
    
    def from_string(self, line : str, fixed_width : bool = True, delimiter : str = ',', default_on_error : list[str] | None = None) -> Self:
        """
        Parse a line of text into an instance of self. Works for either 
        fixed-width formats or variable-width formats.

        Parameters
        ----------
        line : str
            Input line, passed as a string, to be parsed into instance.
        fixed_width : bool
            Optional flag to specify if fixed_width should be used. If 
            self._format_widths cannot be resolved, fixed_width is automatically 
            set to False. 
        delimiter : str | None
            Optional flag to specify a recognized delimiter. Default is None,
            corresponding to general whitespace.
        default_on_error: list[str] | None
            List of column names to populate an instance's default Column 
            value if it exists and from_string() produces an error when parsing 
            that column's corresponding part in the input line.
        
        Returns
        -------
        Self
            An instance of self, with values populated corresponding to the 
            values passed in the input line.
        """
        
        return _from_string(self, line, fixed_width, delimiter, default_on_error)

# ==============================================================================

def _string_formatter(cls : type[LibraMetaClass]) -> str | None:
    """
    Get a string substitution formatter for a given ORM instance. Columns 
    belonging to the ORM instance should have the 'format' key defined within 
    each Column object's 'info' dictionary. If not defined, _format_string 
    will be None, and any flatfile reading/writing will rely on non-fixed-
    width principles.

    Parameters
    ----------
    cls : type[LibraMetaClass]
        Class deriving from LibraMetaClass
    
    Returns
    -------
    str | None
        A format string specifying fixed-width format identifiers if 'format' 
        is defined for every Column object in the class. If not, None is 
        returned.
    """

    if hasattr(cls, '__cached_format_string'):
        return cls.__cached_format_string

    meta = cls.metadata
    structure = [col.name for col in cls.__table__.columns]
    tabledct = dict([(itable.name, itable) for itable in list(meta.tables.values())])

    colfmtdct = {}
    for t in list(meta.tables.values()):
        for col in t.columns:
            _format = col.info.get('format', None)
            if not _format:
                cls.__cached_format_string = None
                return None # Missing 'format' information
            colfmtdct[col.name] = _format
    
    structfmt = []
    for idx, item in enumerate(structure):
        if item in tabledct:
            itabfmt = ' '.join(["{{{}.{}:{}}}".format(idx, col.name, col.info.get('format', '')) for col in tabledct[item].columns])
            structfmt.append(itabfmt)
        elif item in colfmtdct:
            structfmt.append('{{{}:{}}}'.format(idx, colfmtdct[item]))

    result = ''.join(structfmt) + '\n'

    cls.__cached_format_string = result

    return result

def _to_string(instance : type[LibraMetaClass], fixed_width : bool = True, delimiter : str = ' ') -> str:
    
    if instance._format_string and fixed_width:
        fmt = instance._format_string
        newline = '\n' if fmt.endswith('\n') else ''
        fmt = fmt.rstrip('\n')

        if delimiter:
            parts = fmt.split('}{')
            fmt = f'}}{delimiter}{{'.join(parts)
            
        return fmt.format(*instance) + newline
    
    _vals = []
    for idx, i in enumerate(instance):
        if isinstance(instance.__table__.columns[idx].type, (sqlalchemy.DateTime, sqlalchemy.Date, sqlalchemy.Time)):
            fmt = instance.__table__.columns[idx].info.get('format', None)
            _vals.append(datetime.strftime(i, fmt))
        else:
            _vals.append(str(i))

    return delimiter.join(_vals)

def _from_string(instance : type[LibraMetaClass], line : str, fixed_width : bool = True, delimiter : str = ',', default_on_error : list[str] | None = None) -> type[LibraMetaClass]:

    if not instance._format_widths:
        fixed_width = False
    
    # Fixed-width parsing
    pos, vals = 0, []
    if fixed_width:
        for col, width in zip(instance.__table__.columns, instance._format_widths):
            try:
                parser = PARSEHASH[col.type.python_type]
                if not isinstance(col.type, (sqlalchemy.DateTime, sqlalchemy.Date, sqlalchemy.Time)):
                    val = parser(line[pos:pos + width].strip())
                else:
                    try:
                        val = parser(line[pos:pos + width].strip(), col.info.get('format'))
                    except KeyError:
                        raise KeyError(f'Time-like Column \'{col.name}\' requires \'format\' specifier in info dictionary to successfully parse input line.')
            except ValueError as e:
                if default_on_error and col.name in default_on_error:
                    if isinstance(col.default.arg, ScalarElementColumnDefault):
                        val = col.default.arg
                    elif isinstance(col.default.arg, CallableColumnDefault):
                        val = col.default.arg()
                    else:
                        val = col.default
                else:
                    msg = f", column {col}: '{line[pos:pos + width]}', positions [{pos}:{pos + width}]"
                    raise type(e)(str(e) + msg)
            
            vals.append(val)
            pos += width + (len(delimiter) if delimiter else 1)

        return type(instance)(*vals)

    # Variable-width parsing
    if delimiter is None: # Parts of line can contain spaces; e.g. '2025-10-07 12:48:00'
        raise ValueError('Variable-width parsing requires an explicit delimiter.')

    parts = line.rstrip('\n').split(delimiter)
    if len(parts) != len(instance.__table__.columns):
        raise ValueError(f'Length of split line ({len(parts)}) does not equal length of instance ({len(instance.__table__.columns)}))')
    
    for col, raw in zip(instance.__table__.columns, parts):
        raw = raw.strip()

        try:
            parser = PARSEHASH[col.type.python_type]
            if not isinstance(col.type, (sqlalchemy.DateTime, sqlalchemy.Date, sqlalchemy.Time)):
                vals.append(parser(raw))
            else:
                vals.append(parser(raw, col.info.get('format')))
        except Exception:
            if default_on_error and col.name in default_on_error:
                if isinstance(col.default.arg, Callable):
                    default = col.default.arg.__call__('')
                else:
                    default = col.default.arg
                
                vals.append(default)
            else:
                raise
    
    return type(instance)(*vals)
