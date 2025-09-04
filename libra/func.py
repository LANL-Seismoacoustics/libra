"""
Brady Spears
7/16/25

Contains top-level utility functions. Generally, these functions exploit 
methods added to ORM instances through Mixin classes.
"""

# ==============================================================================

from __future__ import annotations
from typing import TYPE_CHECKING
import pdb
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    import pandas as pd

import sqlalchemy

from libra import Schema
from libra import MetaClass

# ==============================================================================
# Quality Control Support Classes
# TODO: This may need some additional thought

def simple_qc(orms : type[MetaClass]) -> None:
    pass

# ==============================================================================
# Pandas DataFrame Support

def to_dframe(orms : list[type[MetaClass]]) -> "pd.DataFrame":
    """
    Converts a list of object-relation-mapped instances to a Pandas DataFrame 
    object. 

    Parameters
    ----------
    orms : list[type[MetaClass]]
        Object-relation-mapped instances deriving from Libra's MetaClass.All 
        list members must be of the same type. 
    
    Returns
    -------
    pd.DataFrame
        Pandas DataFrame object. Columns of the DataFrame correspond to the 
        columns of the ORM objects. Each entry in the orms input list will 
        map to a separate row in the DataFrame object.
    
    Raises
    ------
    ImportError
        Raised if there is an error importing optional pandas module.
    ModuleNotFoundError
        Raised if optional pandas module is not in the current environment.
    """

    try:
        import pandas as pd
    except ImportError:
        raise
    except ModuleNotFoundError:
        raise

    return pd.DataFrame([orm.values() for orm in orms], columns = orms[0].keys())

def from_dframe(dframe : pd.DataFrame, model : type[MetaClass]) -> list[type[MetaClass]]:
    """
    Attempts to convert a given Pandas DataFrame into the provided model. 

    Parameters
    ----------
    dframe : pd.DataFrame
        A Pandas DataFrame object, with defined columns and values.
    model : type[MetaClass]
        Empty abstract ORM instance with columns directly mapped to the columns 
        in dframe.
    
    Returns
    -------
    list[type[MetaClass]]
        A list of models populated with the values contained in dframe; one 
        entry in the list per row of the DataFrame.
    """

    pdb.set_trace()

# ==============================================================================
# FlatFile read/write Support

def from_string(
        cls : type[MetaClass],
        lines : list[str],
        default_on_error : list[str] | None = None
    ) -> list[type[MetaClass]]:
    """
    Convert a given list of strings into a list of ORM instances.

    Parameters
    ----------
    cls : type[MetaClass]
        ORM instance with _format_string() attribute defined
    lines : list[str]
        List of strings formatted according to an ORM's ._format_string() 
        property. 
    default_on_error : list[str] | None = None
        List of qualifying column names that return either a Column's attributed
        default value or, if a default value isn't defined, a None value if 
        there is an error parsing an entry in lines.
    
    Returns
    -------
    list[type[MetaClass]]
        List of ORMs with values assigned from the provided list of strings.
    """
    
    orms = [None] * len(lines)
    for idx, row in enumerate(lines):
        orms[idx] = cls.from_string(row, default_on_error)

    return orms

def to_string(orms : list[type[MetaClass]]) -> list[str]:
    """
    Pulls values from each entry in a list of ORM instances and formats those 
    values into a list of strings.

    Parameters
    ----------
    orms : list[type[MetaClass]]
        List of ORMs, each with a _format_string() attribute.
    
    Returns
    -------
    list[str]
        List of strings with each entry corresponding to the ORMs values, 
        formatted according to the ORM's _format_string() attribute.
    """

    strings = [None] * len(orms)
    for idx, orm in enumerate(orms):
        strings[idx] = orm.to_string()

    return strings

# ==============================================================================
