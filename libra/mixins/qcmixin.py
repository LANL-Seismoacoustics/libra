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
from typing import Any, Callable
from functools import partial
import pdb

from sqlalchemy.sql.base import ReadOnlyColumnCollection

# ==============================================================================

DEFAULT_CHECKS = {
    'gt' : lambda val, ref : val > ref,
    'lt' : lambda val, ref : val < ref,
    'ge' : lambda val, ref : val >= ref,
    'le' : lambda val, ref : val <= ref,
    'regex' : lambda val, ref : bool(re.fullmatch(ref, val)),
    'min_length' : lambda val, ref : len(val) >= ref,
    'max_length' : lambda val, ref : len(val) <= ref
}

# ==============================================================================

class QCResult:
    def __init__(self):
        self.result = {}
    
    def __str__(self):
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
        return "\n".join(lines)

    def add_result(self, key : str, func : Callable, result : bool) -> None:
        entry = {'check' : func, 'result' : result}
        self.result.setdefault(key, []).append(entry)

# ==============================================================================

class QCMixin:
    """
    Contains functionality to perform quality control (QC) on values contained 
    within an ORM instance. 
    """

    def __new__(cls, *args, **kwargs) -> None:
        """
        Extend the __new__() method up the MRO to add a 'qc' property to the 
        child class.
        """

        cls._checks = DEFAULT_CHECKS
        cls._qc_struct = create_qc_lambdas(cls.__table__.columns, cls._checks)

        return super().__new__(cls)

    def simple_qc(cls) -> QCResult:

        _qc_result = QCResult()
        for key, val in cls.items():
            for check in cls._qc_struct[key]:
                _qc_result.add_result(key, check, check(val))
            
        return _qc_result

# ==============================================================================

def create_qc_lambdas(columns : ReadOnlyColumnCollection, checks : dict[str, Callable]) -> dict[str, Callable]:

    qc_struct = {}
    for column in columns:
        qc_struct[column.name] = [partial(checks[key], ref = val) for key, val in column.info.items() if key in checks.keys()]
    
    return qc_struct
