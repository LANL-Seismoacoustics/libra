"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Contains the `QCMixin` object, which acts to automate the quality control of 
SQLAlchemy ORM objects, based on known schema definitions provided in Libra's
`Schema` class. Attributes that are QC'ed include model/table structures 
(constraints, columns, types) and values contained in ORM instances.
Summary statistics are also provided.
"""

# ==============================================================================

from __future__ import annotations
import os
import re
from collections import Counter
from typing import (
    Any,
    Callable,
    TypeVar
)

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.padding import Padding

# ==============================================================================
# Typing

Schema = TypeVar('Schema', bound = Any) # Defined as generic class to avoid circular import

# ==============================================================================
# Global Rule Registry

DEFAULT_RULE_REGISTRY : dict[str, Callable] = {
    'le' : lambda v, ref: v is None or v <= ref,
    'ge' : lambda v, ref: v is None or v >= ref,
    'lt' : lambda v, ref: v is None or v < ref,
    'gt' : lambda v, ref: v is None or v > ref,
    'eq' : lambda v, ref: v is None or v == ref,
    'ne' : lambda v, ref: v is None or v != ref,
    'min_length' : lambda v, ref : v is None or len(v) >= ref,
    'max_length' : lambda v, ref : v is None or len(v) <= ref,
    'regex' : lambda v, ref: v is None or re.match(ref, str(v))
}

# ==============================================================================

class QCReport:

    def __init__(self) -> None:
        self.sections : list[tuple[str, list[object]]] = []
        self.console : Console = Console(highlight = False)
    
    def section(self, title : str) -> None:
        self.sections.append((title, []))
    
    def add(self, renderable : Any) -> None:
        if not self.sections:
            self.section('General')
        self.sections[-1][1].append(renderable)
    
    def _render_with_console(self, console : Console) -> None:
        for title, items in self.sections:
            console.print(Panel(title, style = 'bold cyan'))
            for item in items:
                console.print(item)
    
    def render(self) -> None:
        self._render_with_console(self.console)
    
    def render_to_file(self, filepath : str | os.PathLike, width : int = 80, clear : bool = True) -> None:
        mode = 'w' if clear else 'a'

        with open(filepath, mode, encoding = 'utf-8') as f:
            file_console = Console(
                file = f, width = width, highlight = False, force_terminal = False
            )
            self._render_with_console(file_console)

# ==============================================================================

class QCInspector:
    
    def __init__(
        self,
        model_cls : type[DeclarativeBase],
        instances : list[type[DeclarativeBase]],
        schema : Schema,
        rule_registry : dict[str, Callable] | None = None
    ) -> None:
        self.model_cls = model_cls
        self.instances = instances
        self.schema = schema
        self.rule_registry = rule_registry or {}
    
    def inspect_column_structure(self) -> tuple[str, list[Any]]:
        report_items = []

        model_cols = [col.name for col in self.model_cls.__table__.columns]

        for model_name, model_def in self.schema._registry.models.items():
            if model_cols == model_def['columns']:
                report_items.append(
                    f"[green][\u2714]'{self.model_cls.__tablename__}' found as model '{model_name}' in schema '{self.schema.name}'"
                )
                return model_name, report_items
        
        report_items.append(
            f"[red][\u2718]'{self.model_cls.__tablename__}' not found as a valid model defined in schema '{self.schema.name}'"
        )
        return None, report_items

    def inspect_constraint_structure(self, model_name : str) -> list[Any]:
        report_items = []

        model_def = self.schema._registry.models[model_name]

        def _normalize_constraint(con : dict) -> dict:
            key = list(con.keys())[0]
            value = con[key]

            if 'columns' in value:
                value = {**value, 'columns' : sorted(value['columns'])}
            
            return {key : value}

        actual_constraints = []
        for constraint in self.model_cls.__table__.constraints:
            if isinstance(constraint, sqlalchemy.PrimaryKeyConstraint):
                actual_constraints.append({'pk' : {'columns' : sorted([c.name for c in constraint.columns])}})
            elif isinstance(constraint, sqlalchemy.UniqueConstraint):
                actual_constraints.append({'uq' : {'columns' : sorted([c.name for c in constraint.columns])}})
            elif isinstance(constraint, sqlalchemy.CheckConstraint):
                actual_constraints.append({'ck' : {'sqltext' : str(constraint.sqltext)}})
            else:
                pass
        
        for index in self.model_cls.__table__.indexes:
            actual_constraints.append({'ix' : {'columns' : sorted([c.name for c in index.columns])}})
        
        expected_constraints = [_normalize_constraint(c) for c in model_def.get('constraints', [])]
        actual_constraints = [_normalize_constraint(c) for c in actual_constraints]

        unmatched_expected, unmatched_actual = [], actual_constraints.copy()
        for expected in expected_constraints:
            if expected in actual_constraints:
                unmatched_actual.remove(expected)
            else:
                unmatched_expected.append(expected)
        
        if unmatched_expected:
            report_items.append(
                f"[red][\u2718] Missing constraint(s) : '{unmatched_expected}"
            )
        
        if unmatched_actual:
            report_items.append(
                f"[yellow][\u0021] Unexpected constraint(s) : '{unmatched_actual}'"
            )
        
        if not unmatched_expected and not unmatched_actual:
            report_items.append(
                f"[green][\u2714] Constraint structure for '{self.model_cls.__tablename__}' validated against schema '{self.schema.name}'"
            )
        
        return report_items

    def inspect_constraint_violations(self) -> list[Any]:
        report_items = []

        if not self.instances:
            report_items.append(f"No instances provided to assess constraint violations")
            return report_items

        constraints = []
        for constraint in self.model_cls.__table__.constraints:
            if isinstance(constraint, sqlalchemy.PrimaryKeyConstraint):
                constraints.append(('pk' , [c.name for c in constraint.columns]))
            elif isinstance(constraint, sqlalchemy.UniqueConstraint):
                constraints.append(('uq', [c.name for c in constraint.columns]))
        
        for constraint_type, columns in constraints:
            seen, duplicates = set(), []
            for instance in self.instances:
                if not isinstance(instance, self.model_cls):
                    report_items.append(f"[red] Invalid instance type in validation list: expected '{self.model_cls.__name__}', got '{type(instance).__name__}'")
                    return report_items
                
                key = tuple(getattr(instance, col) for col in columns)
                
                if constraint_type == 'uq' and any(v is None for v in key):
                    continue
                    
                if key in seen:
                    duplicates.append(key)
                else:
                    seen.add(key)
            
            if duplicates:
                report_items.append(
                    f"  [red][\u2718] {constraint_type.upper()} violation on column(s) {columns}: duplicate values {duplicates}"
                )
            else:
                report_items.append(
                    f"  [green][\u2714] {constraint_type.upper()} constraint satisified for column(s) {columns}"
                )
        
        return report_items

    def inspect_values(self) -> tuple[list[str], list[Any]]:
        report_items, col_names = [], []

        for col in self.model_cls.__table__.columns:
            col_names.append(col.name)
            rules = col.info or {}
            if not rules:
                continue

            failures = 0
            for instance in self.instances:
                value = getattr(instance, col.name)
                for key, expected in rules.items():
                    rule = self.rule_registry.get(key)
                    if not callable(rule):
                        continue
                        
                    if not rule(value, expected):
                        failures += 1
            
            if failures:
                report_items.append(
                    f"\t[red]Column '{col.name}' : {failures} rule violations"
                )
            else:
                report_items.append(
                    f"\t[green]Column '{col.name}' : 0 rule violations"
                )

        return col_names, report_items

    def summarize_values(self, column_name : str, top_n = 5) -> list[Any]:
        report_items = []

        values = [
            getattr(instance, column_name) for instance in self.instances
        ]

        counts = Counter(values)
        most_common = counts.most_common(top_n)

        table = Table(title = f"Top {top_n} values for Column '{column_name}'")
        table.add_column('Value', width = 30, justify = 'right')
        table.add_column('Count', width = 10)

        for value, count in most_common:
            table.add_row(str(value), str(count))
        
        report_items.append(Padding.indent(table, 8))
        
        return report_items

# ==============================================================================

class QCMixin:

    @classmethod
    def qc(
        cls : type[DeclarativeBase],
        instances : list[type[DeclarativeBase]],
        schema : Schema,
        report : QCReport | None = None,
        column_rules : dict[str, Callable] | None = None,
        summarize : bool = False,
        summarize_n : int = 5
    ) -> QCReport:
        
        rule_registry = DEFAULT_RULE_REGISTRY

        if column_rules:
            rule_registry.update(column_rules)
        
        inspector = QCInspector(
            model_cls = cls,
            instances = instances,
            schema = schema,
            rule_registry = rule_registry
        )

        if not report:
            report = QCReport()
        
        # Structure (by Column)
        report.section(f"Table '{cls.__tablename__}' Validation")
        model_name, items = inspector.inspect_column_structure()
        for item in items:
            report.add(item)
        
        # Structure (by Constraint)
        if model_name:
            items = inspector.inspect_constraint_structure(model_name)
            for item in items:
                report.add(item)

        # Instance Constraint Violations
        items = inspector.inspect_constraint_violations()
        for item in items:
            report.add(item)
        
        # Values
        col_names, items = inspector.inspect_values()
        for item in items:
            report.add(item)
        
        report.add('\n')

        # Summary
        if summarize:
            for col_name in col_names:
                items = inspector.summarize_values(col_name, summarize_n)
                for item in items:
                    report.add(item)
        
        return report