"""
Brady Spears
7/16/25

Contains the `QCMixin` class. The `QCMixin` comes loaded with methods to allow 
for the easy Quality Control of derivative Object-relation-mapped instances.
Quality control works both on the structure as a whole as well as on the values 
contained in that structure.
"""

# ==============================================================================

from __future__ import annotations
import re
from typing import Callable
from functools import partial

from sqlalchemy.sql.base import ReadOnlyColumnCollection

# ==============================================================================

DEFAULT_CHECKS = {
    'gt' : lambda val, ref : val > ref,
    'lt' : lambda val, ref : val < ref,
    'ge' : lambda val, ref : val >= ref,
    'le' : lambda val, ref : val <= ref,
    'equal' : lambda val, ref : val == ref,
    'nequal' : lambda val, ref : val != ref,
    'range_ex' : lambda val, ref : val > ref[0] and val < ref[1],
    'range_in' : lambda val, ref : val >= ref[0] and val <= ref[1],
    'regex' : lambda val, ref : bool(re.fullmatch(ref, val)),
    'options' : lambda val, ref : val in ref,
    'min_length' : lambda val, ref : len(val) >= ref,
    'max_length' : lambda val, ref : len(val) <= ref
}

# ==============================================================================

class QCResult:
    """
    Class to contain the result of a simple_qc() output.

    Attributes
    ----------
    result : dict[str, list[dict[str, Any]]]
        Dictionary mapping a key to a Callable and a boolean result.
    
    Methods
    -------
    add_result(self, key : str, func : Callable, result : bool) -> None:
        Appends the result attribute to associate a key with a function and 
        the boolean result of the execution of that function.
    """

    def __init__(self) -> None:
        """
        Initializes a QCResult object with an empty result.
        """

        self.result = {}
    
    def __str__(self) -> str:
        """
        Returns a formatted string detailing the key, check, and result (PASS/
        FAIL) of the execution of a check.
        """

        lines = []
        for key, checks in self.result.items():
            if not checks:
                lines.append(f"{key}: No checks performed")
                continue

            lines.append(f"{key}:")
            for entry in checks:
                check_name = entry["check"]
                result = "PASS" if entry["result"] else "FAIL"
                lines.append(f"  - {check_name}: {result}")
        return "\n".join(lines) + "\n"

    def add_result(self, key : str, func : Callable, result : bool) -> None:
        """
        Appends the result attribute to associate a key with a function and 
        the boolean result of the execution of that function.
        
        Parameters
        ----------
        key : str
            Key to associate a check and result with.
        func : Callable
            Function that was executed.
        result : bool
            Boolean result of executing that function.
        """

        entry = {'check' : func, 'result' : result}

        self.result.setdefault(key, []).append(entry)

# ==============================================================================

class QCMixin:
    """
    Contains functionality to perform quality control (QC) on values contained 
    within an ORM instance.

    Attributes
    ----------
    _checks : dict[str, Callable]
        Dictionary mapping specific keywords to specific functions. When 
        iterating through an ORM's columns, any reference to the key inside the 
        Column object's 'info' dictionary will map to the function defined here.
    _qc_struct : dict[str, list[Callable]]
        Dictionary mapping column names to a list of functions. When calling the 
        simple_qc() method, this variable will determine the quality control 
        checks to be performed on each column.
    
    Methods
    -------
    simple_qc(cls) -> QCResult
        Iterates through each column in the input class and performs any checks 
        associated with that column on the value associated with that column. 
    """

    def __new__(cls, *args, **kwargs) -> None:
        """
        Extend the __new__() method up the MRO to add quality control properties 
        to the inheriting class.
        """

        cls._checks = DEFAULT_CHECKS
        cls._qc_struct = create_qc_lambdas(cls.__table__.columns, cls._checks)

        return super().__new__(cls)

    def simple_qc(cls) -> QCResult:
        """
        Iterates through each column in the input class and performs any checks 
        associated with that column on the value associated with that column.

        Parameters
        ----------
        cls : type[QCMixin]
            Class inheriting from QCMixin. Should have "_checks" attribute and 
            "_qc_struct" attribute defined.
        """

        _qc_result = QCResult()
        for key, val in cls.items():
            for check in cls._qc_struct[key]:
                _qc_result.add_result(key, check, check(val))
            
        return _qc_result

# ==============================================================================

def create_qc_lambdas(columns : ReadOnlyColumnCollection, checks : dict[str, Callable]) -> dict[str, list[Callable]]:
    """
    Create a dictionary mapping a Column object to a series of checks, based on 
    the keys contained in the Column object's 'info' dictionary. If a key in the 
    'info' dictionary is recognized as a key in input 'checks', the mapped 
    Callable will be stored in a 'qc_struct' dictionary.

    Parameters
    ----------
    columns : sqlalchemy.sql.base.ReadOnlyColumnCollection
        Iterable containing SQLAlchemy Column objects.
    checks : dict[str, Callable]
        Dictionary mapping specific keys contained in a Columnn's 'info' 
        dictionary to a Callable, like a lambda function.
    
    Returns
    -------
    qc_struct : dict[str, list[Callable]]
        A dictionary mapping a column to a list of Callables or "checks" that 
        return boolean values.
    """

    qc_struct = {}
    for column in columns:
        qc_struct[column.name] = [partial(checks[key], ref = val) for key, val in column.info.items() if key in checks.keys()]
    
    return qc_struct
