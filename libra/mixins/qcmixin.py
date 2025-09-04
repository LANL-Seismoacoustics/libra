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
from abc import ABC, abstractmethod

# ==============================================================================

# class QCCheck(ABC):

#     @abstractmethod
#     def run(self, *args, **kwargs) -> None:
#         ...

# class RegexCheck(QCCheck):

#     def run(self):
#         print('Running Regex Check...')

# class IntervalCheck(QCCheck):

#     def run(self):
#         print('Running Interval Check...')

# ==============================================================================

# class QCMixin:
#     """
#     Contains functionality to perform quality control (QC) on values contained 
#     within an ORM instance. 
#     """

#     def __new__(cls, *args, **kwargs) -> None:
#         """
#         Extend the __new__() method up the MRO to add a 'qc' property to the 
#         child class.
#         """

#         cls.checks : list[type[QCCheck]] = [RegexCheck, IntervalCheck]

#         return super().__new__(cls)

#     def add_check(cls, check : type[QCCheck], index : int = None) -> None:

#         if not index:
#             cls.checks.append(check)
#         else:
#             cls.checks.insert(index, check)
    
#     def run_checks(cls):

#         results = []
#         for check in cls.checks:
#             check.run(cls)
