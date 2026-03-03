'''
Brady Spears, Los Alamos National Laboratory
10/7/2025

Test Suite for all built-in Libra Mixin classes.
'''

# ==============================================================================

import os
import unittest
import datetime

import sqlalchemy
import pandas as pd
from rich.table import Table

from libra.schema import Schema

# ==============================================================================

TEST_SCHEMA = {
    'Test Schema' : {
        'columns': {
            'id': {
                'type': 'Integer()',
                'nullable': False,
                'default' : -1,
                'info': {'width': 5, 'format' : '5d', 'ge' : 0}
            },
            'name': {
                'type': 'String(length = 20)',
                'nullable': False,
                'info': {'format': '20.20s', 'width' : 20, 'regex' : "^[A-Z][a-z]*$"}
            },
            'score': {
                'type': 'Float()',
                'nullable': True,
                'info': {'width': 8, 'format': '8.2f', 'ge' : 0., 'le' : 100.}
            },
            'class_name' : {
                'type' : 'String(length = 20)',
                'nullable' : False,
                'info' : {'format' : '20.20s', 'width' : 20}
            },
            'created': {
                'type': 'DateTime()',
                'nullable': False,
                'default' : {'$ref' : 'datetime.now'},
                'info': {'format': '%Y-%m-%d', 'width' : 10}
            }
        },

        'models': {
            'record': {
                'columns': ['id', 'name', 'score', 'created'],
                'constraints': [
                    {'pk' : {'columns' : ['id']}},
                    {'uq' : {'columns' : ['name']}}
                ]
            },
            'class' : {
                'columns' : ['id', 'name', 'class_name', 'created'],
                'constraints' : [
                    {'pk' : {'columns' : ['id']}},
                    {'uq' : {'columns' : ['name', 'class_name']}}
                ]
            }
        }
    }
}

# ==============================================================================
# FlatFileMixin Tests

class TestFlatFileMixin(unittest.TestCase):

    def setUp(self):

        # Build schema + model dynamically
        self.schema = Schema('Test Schema').load(TEST_SCHEMA)

        class Record(self.schema.record): 
            __tablename__ = 'record'

            def __iter__(self):
                return iter([self.id, self.name, self.score, self.created])
        
        self.model = Record

        # Example test instance
        self.instance = self.model(123, 'Alice', 98.5, datetime.datetime(2025, 1, 1))
    
    def test_fixed_width_write(self):
        result = self.instance.to_string(fixed_width = True, delimiter = '')

        expected = '  123Alice                  98.502025-01-01\n'

        self.assertEqual(result, expected)
    
    def test_fixed_width_with_delimiter(self):
        result = self.instance.to_string(fixed_width = True, delimiter = '|')

        expected = '  123|Alice               |   98.50|2025-01-01\n'

        self.assertEqual(result, expected)
    
    def test_fixed_width_round_trip(self):
        line = self.instance.to_string(fixed_width = True, delimiter = '|')
        parsed = self.instance.from_string(line, fixed_width = True, delimiter = '|')

        self.assertEqual(parsed.id, 123)
        self.assertEqual(parsed.name.strip(), 'Alice')
        self.assertEqual(parsed.score, 98.5)
        self.assertEqual(parsed.created, datetime.datetime(2025, 1, 1))
    
    def test_variable_width_write(self):
        result = self.instance.to_string(fixed_width = False, delimiter = ',')

        expected = '123,Alice,98.5,2025-01-01'

        self.assertEqual(result, expected)
    
    def test_variable_width_round_trip(self):
        line = '123,Alice,98.5,2025-01-01'
        parsed = self.instance.from_string(line, fixed_width = False, delimiter = ',')

        self.assertEqual(parsed.id, 123)
        self.assertEqual(parsed.name, 'Alice')
        self.assertEqual(parsed.score, 98.5)
        self.assertEqual(parsed.created, datetime.datetime(2025, 1, 1))
    
    def test_default_on_error(self):
        bad_line = 'abc,Alice,98.5,2025-01-01'

        parsed = self.instance.from_string(
            bad_line,
            fixed_width = False,
            delimiter = ',',
            default_on_error = ['id']
        )

        self.assertEqual(parsed.id, -1)
        self.assertEqual(parsed.name, 'Alice')
    
    def test_datetime_parse_failure(self):
        bad_line = '123,Alice,98.5,not-a-date'

        parsed = self.instance.from_string(
            bad_line,
            fixed_width = False,
            delimiter = ',',
            default_on_error = ['created']
        )

        self.assertIsInstance(parsed.created, datetime.datetime)

    def test_missing_width_falls_back(self):
        self.model.__table__.columns['name'].info.pop('width')

        instance = self.model(123, 'Alice', 98.5, datetime.datetime(2025, 1, 1))
        setattr(instance, '__cached_format_string', None)

        result = instance.to_string(fixed_width = True, delimiter = ',')

        self.assertEqual(result, '123,Alice,98.5,2025-01-01')


# ==============================================================================
# PandasMixin Tests

class TestPandasMixin(unittest.TestCase):

    def setUp(self):

        # Build schema + model dynamically
        self.schema = Schema('Test Schema').load(TEST_SCHEMA)

        class Record(self.schema.record): 
            __tablename__ = 'record'
        
        self.model = Record

        # Example test instance & list of instances
        self.instance = self.model(123, 'Alice', 98.5, datetime.datetime(2025, 1, 1))
        
        self.instances = [
            self.model(1, 'Joey', 78.3, datetime.datetime(2026, 1, 12)),
            self.model(2, 'Chandler', 99.2, datetime.datetime(2026, 2, 16)),
            self.model(3, 'Monica', 93.4, datetime.datetime(2026, 5, 5)),
            self.model(4, 'Phoebe', 86.2, datetime.datetime(2026, 6, 19)),
            self.model(5, 'Ross', 93.3, datetime.datetime(2026, 7, 4)),
            self.model(6, 'Rachel', 80.0, datetime.datetime(2026, 10, 31))
        ]

    def test_to_series(self):
        s = self.instance.to_series()

        self.assertIsInstance(s, pd.Series)
        self.assertEqual(s['id'], 123)
        self.assertEqual(s['name'], 'Alice')
        self.assertEqual(s['score'], 98.5)
        self.assertEqual(s['created'], datetime.datetime(2025, 1, 1))
    
    def test_from_series(self):
        s = self.instance.to_series()
        new_instance = self.model.from_series(s)

        self.assertEqual(new_instance.id, 123)
        self.assertEqual(new_instance.name, 'Alice')
        self.assertEqual(new_instance.score, 98.5)
        self.assertEqual(new_instance.created, datetime.datetime(2025, 1, 1))

    def test_from_frame(self):
        df = self.model.to_frame(self.instances)
        new_instances = self.model.from_frame(df)

        self.assertEqual(len(new_instances), 6)
        self.assertEqual(new_instances[0].name, 'Joey')
        self.assertEqual(new_instances[1].name, 'Chandler')
    
    def test_nan_to_none(self):
        df = pd.DataFrame([
            {'id' : 7, 'name' : None, 'score' : float('nan'), 'created' : None}
        ])

        instances = self.model.from_frame(df)
        instance = instances[0]

        self.assertEqual(instance.id, 7)
        self.assertIsNone(instance.name)
        self.assertIsNone(instance.score)
        self.assertIsInstance(instance.created, datetime.datetime) # 'default' invoked when DateTime val is None
    
    def test_datetime_string_coercion(self):
        df = pd.DataFrame([
            {'id' : 8, 'name' : 'Gunther', 'score' : 100., 'created' : '2026-11-25'}
        ])

        instance = self.model.from_frame(df)[0]

        self.assertIsInstance(instance.created, datetime.datetime)
        self.assertEqual(instance.created, datetime.datetime(2026, 11, 25))


# ==============================================================================
# QC Mixin Tests

class TestQCMixin(unittest.TestCase):
    
    def setUp(self):

        # Build schema & model dynamically
        self.schema = Schema('Test Schema').load(TEST_SCHEMA)

        class Record(self.schema.record):
            __tablename__ = 'record'
        
        self.model = Record

        self.instances = [
            self.model(1, 'Monica', 99.1, datetime.datetime(2025, 1, 1)),
            self.model(2, 'Phoebe', 84.3, datetime.datetime(2025, 1, 2)),
            self.model(3, 'Chandler', 87.9, datetime.datetime(2025, 1, 3)),
            self.model(4, 'Joey', 64.3, datetime.datetime(2025, 1, 3)),
            self.model(5, 'Rachel', 86.9, datetime.datetime(2025, 1, 3)),
            self.model(6, 'Ross', 90.2, datetime.datetime(2025, 1, 4))
        ]
    
    def test_structure_valid(self):
        report = self.model.qc(self.instances, self.schema)

        titles = [section[0] for section in report.sections]
        self.assertIn("Table 'record' Validation", titles)

        content = str(report.sections[0][1])
        self.assertIn("found as model 'record'", content)
    
    def test_structure_invalid_model(self):

        class BadRecord(self.schema.record):
            __tablename__ = 'bad_record'

            extra = sqlalchemy.Column(sqlalchemy.String())
        
        bad_instances = [BadRecord('extra', 1, 'Gunther', 99.5, datetime.datetime(2025, 1, 3))]

        report = BadRecord.qc(bad_instances, self.schema)

        content = str(report.sections[0][1])
        self.assertIn("not found as a valid model", content)
    
    def test_unique_constraint_violation(self):
        instances = [
            self.model(1, 'Chandler', 87.9, datetime.datetime(2025, 1, 3)),
            self.model(2, 'Chandler', 84.1, datetime.datetime(2025, 1, 4))
        ]

        report = self.model.qc(instances, self.schema)

        content = str(report.sections[0][1])
        self.assertIn("UQ violation", content)
    
    def test_primary_key_violation(self):
        instances = [
            self.model(1, 'Phoebe', 84.3, datetime.datetime(2025, 1, 2)),
            self.model(1, 'Phoebe', 86.1, datetime.datetime(2025, 1, 5))
        ]

        report = self.model.qc(instances, self.schema)

        content = str(report.sections[0][1])
        self.assertIn("PK violation", content)
    
    def test_value_rule_violation(self):
        instances = [self.model(-5, 'Gunther', 99.5, datetime.datetime(2025, 1, 3))]

        report = self.model.qc(instances, self.schema)

        content = str(report.sections[0][1])
        self.assertIn('1 rule violations', content)
    
    def test_no_rule_violations(self):
        report = self.model.qc(self.instances, self.schema)

        content = str(report.sections[0][1])
        self.assertIn("0 rule violations", content)
    
    def test_summary_generation(self):
        report = self.model.qc(
            self.instances,
            self.schema,
            summarize=True,
            summarize_n=2
        )

        section_items = report.sections[0][1]

        has_table = any(isinstance(item, Table) or hasattr(item, 'renderable')
                        for item in section_items)

        self.assertTrue(has_table)
    
    def test_render_to_file(self):

        report = self.model.qc(self.instances, self.schema)

        filepath = "test_qc_output.txt"

        try:
            report.render_to_file(filepath)

            self.assertTrue(os.path.exists(filepath))

            with open(filepath, 'r', encoding='utf-8') as f:
                contents = f.read()

            self.assertIn("record", contents)

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)


# ==============================================================================

if __name__ == '__main__':
    unittest.main()  
