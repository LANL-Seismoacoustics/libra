"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Test Suite for Libra Schema class.
"""

# ==============================================================================

import os
import time
import yaml
import unittest
import tempfile
from unittest.mock import MagicMock

import sqlalchemy

from libra.schema import Schema
from libra.util import DatabaseSettings
from libra.util import SchemaNotFoundError

# ==============================================================================
# Global Valid Schema Definitions

SCHEMA_NAME = 'Test Schema'
VALID_DICT  = {
    SCHEMA_NAME : {
        'description' : 'Example test schema',
        'columns' : {
            'userid' : {'type' : 'Integer()', 'nullable' : False},
            'orderid' : {'type' : 'Uuid()', 'nullable' : False},
            'name' : {'type' : 'String(length = 32)', 'nullable' : False},
            'email' : {'type' : 'String(length = 32)', 'nullable' : True, 'default' : '-'},
            'user_status' : {'type' : 'String(length = 12)', 'nullable' : False, 'default' : 'active', 'info' : {'format' : '12.12s', 'width' : 12}},
            'order_status' : {'type' : 'String(length = 12)', 'nullable' : False, 'default' : 'opened'},
            'order_placed' : {'type' : 'DateTime()', 'nullable' : False, 'default' : {'$ref' : 'datetime.now'}},
            'moddate' : {'type' : 'DateTime()', 'nullable' : False, 'onupdate' : {'$ref' : 'datetime.now'}, 'default' : {'$ref' : 'datetime.now'}},
            'loaddate' : {'type' : 'DateTime()', 'nullable' : False, 'default' : {'$ref' : 'datetime.now'}}
        },
        'models' : {
            'User' : {
                'columns' : ['userid', 'name', 'email', 'user_status', 'moddate', 'loaddate'],
                'constraints' : [{'pk' : {'columns' : ['userid']}}, {'uq' : {'columns' : ['name']}}, {'ix' : {'columns' : ['email']}}, {'ck' : {'sqltext' : "column('user_status').in_(['active', 'inactive'])"}}]
            },
            'Order' : {
                'columns' : ['orderid', 'userid', 'order_placed', 'order_status', 'moddate', 'loaddate'],
                'constraints' : [{'pk' : {'columns' : ['orderid']}}, {'uq' : {'columns' : ['orderid', 'userid']}}, {'ck' : {'sqltext' : "column('order_status').in_(['opened', 'in process', 'closed'])"}}]
            }
        }
    }
}

# ==============================================================================
# Schema Initialization Tests

class TestSchemaInitialization(unittest.TestCase):

    def test_basic_initialization(self):
        schema = Schema(SCHEMA_NAME)

        self.assertEqual(schema.name, SCHEMA_NAME)
        self.assertIsNone(schema.description)
        self.assertEqual(schema._registry.columns, {})
        self.assertEqual(schema._registry.models, {})
        self.assertEqual(schema._model_cache, {})
    
    def test_initialization_with_description(self):
        schema = Schema(SCHEMA_NAME, description = 'DESC')

        self.assertEqual(schema.description, 'DESC')


# ==============================================================================
# Dict Transfer Strategy Tests

class TestSchemaDictTransfer(unittest.TestCase):
    
    def setUp(self):
        self.schema = Schema(SCHEMA_NAME).load(VALID_DICT)
    
    def test_dict_load_populates_registry(self):
        self.assertIn('userid', self.schema._registry.columns)
        self.assertIn('User', self.schema._registry.models)
        self.assertEqual(self.schema.description, 'Example test schema')
    
    def test_lazy_model_construction(self):
        self.assertNotIn('User', self.schema._model_cache)

        user_model = self.schema.User

        self.assertIn('User', self.schema._model_cache)
        self.assertTrue(hasattr(user_model, '__abstract__'))
    
    def test_column_types_construct(self):
        user_model = self.schema.User

        self.assertIsInstance(user_model.userid.type, sqlalchemy.Integer)
        self.assertIsInstance(user_model.name.type, sqlalchemy.String)
        self.assertEqual(user_model.name.type.length, 32)
    
    def test_callable_defaults(self):
        user_model = self.schema.User

        self.assertTrue(callable(user_model.moddate.default.arg))
        self.assertTrue(callable(user_model.loaddate.default.arg))
        self.assertTrue(callable(user_model.moddate.onupdate.arg))
    
    def test_unique_constraints(self):
        user_model = self.schema.User

        uniques = [c for c in user_model.__table_args__ if isinstance(c, sqlalchemy.UniqueConstraint)]

        self.assertTrue(any('name' in [col for col in u._pending_colargs] for u in uniques))
    
    def test_check_constraints(self):
        user_model = self.schema.User

        checks = [c for c in user_model.__table_args__ if isinstance(c, sqlalchemy.CheckConstraint)]

        self.assertTrue(len(checks) > 0)
    
    def test_dict_dump_round_trip(self):
        dumped = self.schema.dump()

        self.assertEqual(dumped, VALID_DICT)
    
    def test_dump_after_lazy_load(self):
        _ = self.schema.User
        _ = self.schema.Order

        dumped = self.schema.dump()
        self.assertEqual(dumped, VALID_DICT)


# ==============================================================================
# YAML File Transfer Strategy Tests

class TestSchemaYAMLTransfer(unittest.TestCase):
    
    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode = 'w', suffix = '.yaml', delete = False)

        yaml.safe_dump(VALID_DICT, self.tempfile)
    
    def tearDown(self):
        os.remove(self.tempfile.name)
    
    def test_yaml_load(self):
        schema = Schema(SCHEMA_NAME).load(self.tempfile.name)

        self.assertIn('User', schema._registry.models)
        self.assertEqual(schema.description, 'Example test schema')
    
    def test_yaml_dump(self):
        schema = Schema(SCHEMA_NAME).load(VALID_DICT)

        schema.dump(self.tempfile.name)

        with open(self.tempfile.name, 'r', encoding = 'utf-8') as f:
            loaded = yaml.safe_load(f)
        
        self.assertEqual(loaded, VALID_DICT)
    
    def test_yaml_round_trip(self):
        schema = Schema(SCHEMA_NAME).load(self.tempfile.name)

        dumped = schema.dump()

        new_schema = Schema(SCHEMA_NAME).load(dumped)

        self.assertEqual(new_schema.dump(), VALID_DICT)


# ==============================================================================
# Database Transfer Strategy Tests

class TestSchemaDBTransfer(unittest.TestCase):

    def setUp(self):
        # In-memory SQLite DB
        self.engine = sqlalchemy.create_engine('sqlite:///:memory:')

        self.db_settings = DatabaseSettings(
            engine = self.engine,
            author = 'tester',
            create_tables = True,
            overwrite = True
        )

        self.schema = Schema(SCHEMA_NAME).load(VALID_DICT)
    
    def test_db_dump_creates_tables(self):
        self.schema.dump(self.db_settings)

        inspector = sqlalchemy.inspect(self.engine)
        tables = inspector.get_table_names()

        expected_tables = {
            self.db_settings.schemadescript,
            self.db_settings.modeldescript,
            self.db_settings.columndescript,
            self.db_settings.columnassoc,
            self.db_settings.columninfo,
            self.db_settings.constraintdescript
        }

        self.assertTrue(expected_tables.issubset(set(tables)))
    
    def test_db_dump_prevents_overwrite(self):
        self.schema.dump(self.db_settings)

        no_overwrite = DatabaseSettings(
            engine = self.engine,
            author = 'tester',
            create_tables = False,
            overwrite = False
        )

        with self.assertRaises(ValueError):
            self.schema.dump(no_overwrite)
    
    def test_db_dump_overwrite_true(self):
        self.schema.dump(self.db_settings)

        overwrite_settings = DatabaseSettings(
            engine=self.engine,
            author="tester",
            create_tables=False,
            overwrite=True
        )

        # Should not raise
        self.schema.dump(overwrite_settings)
    
    def test_db_load_schema_not_found(self):
        empty_settings = DatabaseSettings(
            engine=self.engine,
            author="tester",
            create_tables=True,
            overwrite=True
        )

        with self.assertRaises(SchemaNotFoundError):
            Schema(SCHEMA_NAME).load(empty_settings)
    
    def test_db_round_trip(self):
        # Dump to DB
        self.schema.dump(self.db_settings)

        # Load into fresh schema
        loaded = Schema(SCHEMA_NAME).load(self.db_settings)
        dumped = loaded.dump()

        self.assertEqual(dumped, VALID_DICT)
    
    def test_db_round_trip_after_lazy_model_build(self):
        self.schema.dump(self.db_settings)

        loaded = Schema(SCHEMA_NAME).load(self.db_settings)

        # Trigger lazy load
        _ = loaded.User
        _ = loaded.Order

        self.assertEqual(loaded.dump(), VALID_DICT)


# ==============================================================================
# Stress test (200 models, with 1000 columns each, deserialized in under 5 sec)

class TestSchemaPerformance(unittest.TestCase):

    def setUp(self):
        from libra.registry import Registry  # adjust import
        self.registry = Registry()

        # Fast mock to avoid heavy deserialization cost
        self.registry.columnhandler.deserialize = MagicMock(
            side_effect=lambda d: list(d.values())[0]
        )

    def test_performance_stress(self):
        NUM_MODELS = 200
        NUM_COLUMNS = 1000
        MAX_DURATION = 5 # seconds

        self.registry.columns = {
            f'col_{i}' : {
                'type' : 'String(length = 32)',
                'nullable' : True
            } for i in range(NUM_COLUMNS)
        }

        self.registry.models = {
            f'model_{m}' : {
                'columns' : [f'col_{i}' for i in range(NUM_COLUMNS)],
                'constraints' : []
            } for m in range(NUM_MODELS)
        }

        start = time.time()
        
        for m in range(NUM_MODELS):
            self.registry._create(f'model_{m}')

        duration = time.time() - start

        # Basic structural validation
        self.assertEqual(len(self.registry.models.keys()), NUM_MODELS)
        self.assertEqual(len(self.registry.columns.keys()), NUM_COLUMNS)

        # # Sanity threshold (adjust if needed)
        self.assertLess(duration, MAX_DURATION, 
            f"Stress test timing over maximum duration of {MAX_DURATION:.2f}s; took {duration:.2f}s")


# ==============================================================================

if __name__ == '__main__':
    unittest.main()
