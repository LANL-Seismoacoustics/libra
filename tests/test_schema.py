# ==============================================================================

import os
import unittest
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy import String
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint

from libra import (
    Schema, DictionarySettings, YAMLFileSettings, DatabaseSettings
)
from libra.util import TypeMap

# ==============================================================================

class SchemaLoad_Test_Dictionary(unittest.TestCase):
    """Test for loading a Schema object from a Python dictionary."""

    def setUp(self):
        """Initialize some common variables across tests."""

        self.dictionary = None

class SchemaLoad_Test_YAMLFile(unittest.TestCase):
    """Test for loading a Schema object from a YAML File."""

    def setUp(self):
        """Initialize some common variables across tests."""

        self.yaml_file = 'tests/resources/libra_test.yaml'

        self.yaml_settings = YAMLFileSettings(file = self.yaml_file)

        self.schema = Schema('Test Schema').load(self.yaml_settings)

    def test_models_exist(self):
        """Tests whether models are added as attributes to schema."""

        model1_exists = hasattr(self.schema, 'testmodel1')
        model2_exists = hasattr(self.schema, 'testmodel2')

        return self.assertTrue(model1_exists * model2_exists)

    def test_columns_in_models(self):
        """Tests whether columns are added as attributes to schema models."""

        c1_m1 = hasattr(self.schema.testmodel1, 'testcolumn1')
        c2_m1 = hasattr(self.schema.testmodel1, 'testcolumn2')
        c3_m1 = hasattr(self.schema.testmodel1, 'testcolumn3')
        c4_m1 = hasattr(self.schema.testmodel1, 'testcolumn4')

        c1_m2 = hasattr(self.schema.testmodel2, 'testcolumn1')
        c2_m2 = hasattr(self.schema.testmodel2, 'testcolumn2')
        c3_m2 = hasattr(self.schema.testmodel2, 'testcolumn3')

        return self.assertTrue(c1_m1 * c2_m1 * c3_m1 * c4_m1 * c1_m2 * c2_m2 * c3_m2)

    def test_tablename_declarations(self):
        """Tests whether models have the correct tablename applied."""

        new_schema = self.schema.assign_tablenames(prefix = 'test_', suffix = '_test')

        t1_bool = self.schema.testmodel1.__tablename__ == 'test_testmodel1_test'
        t2_bool = self.schema.testmodel2.__tablename__ == 'test_testmodel2_test'

        return self.assertTrue(t1_bool * t2_bool)

    def test_constraint_declarations(self):
        """Tests whether models have correct constraints applied."""

        self.schema.assign_tablenames()

        t1_args = self.schema.testmodel1.__table_args__
        t2_args = self.schema.testmodel2.__table_args__

        test_bool = isinstance(t1_args[0], PrimaryKeyConstraint) * \
            isinstance(t1_args[1], UniqueConstraint) * \
            isinstance(t2_args[0], PrimaryKeyConstraint)

        return self.assertTrue(test_bool)

class SchemaLoad_Test_Database(unittest.TestCase):
    """Test for loading a Schema object from database tables."""

    def setUp(self):
        """Initialize some common variables across tests."""

        self.connection_str = 'sqlite:///tests/resources/libra_test.db'

        self.engine = create_engine(self.connection_str)

        self.session = Session(self.engine)

        self.db_settings = DatabaseSettings(connection_str = self.connection_str)

        self.schema = Schema('Test Schema').load(self.db_settings)
    
    def test_models_exist(self):
        """Tests whether models are added as attributes to schema."""

        model1_exists = hasattr(self.schema, 'testmodel1')
        model2_exists = hasattr(self.schema, 'testmodel2')

        return self.assertTrue(model1_exists * model2_exists)

    def test_columns_in_models(self):
        """Tests whether columns are added as attributes to schema models."""

        c1_m1 = hasattr(self.schema.testmodel1, 'testcolumn1')
        c2_m1 = hasattr(self.schema.testmodel1, 'testcolumn2')
        c3_m1 = hasattr(self.schema.testmodel1, 'testcolumn3')
        c4_m1 = hasattr(self.schema.testmodel1, 'testcolumn4')

        c1_m2 = hasattr(self.schema.testmodel2, 'testcolumn1')
        c2_m2 = hasattr(self.schema.testmodel2, 'testcolumn2')
        c3_m2 = hasattr(self.schema.testmodel2, 'testcolumn3')

        return self.assertTrue(c1_m1 * c2_m1 * c3_m1 * c4_m1 * c1_m2 * c2_m2 * c3_m2)

    def test_tablename_declarations(self):
        """Tests whether models have the correct tablename applied."""

        new_schema = self.schema.assign_tablenames(prefix = 'test_', suffix = '_test')

        t1_bool = self.schema.testmodel1.__tablename__ == 'test_testmodel1_test'
        t2_bool = self.schema.testmodel2.__tablename__ == 'test_testmodel2_test'

        return self.assertTrue(t1_bool * t2_bool)

    def test_constraint_declarations(self):
        """Tests whether models have correct constraints applied."""

        self.schema.assign_tablenames()

        t1_args = self.schema.testmodel1.__table_args__
        t2_args = self.schema.testmodel2.__table_args__

        test_bool = isinstance(t1_args[0], PrimaryKeyConstraint) * \
            isinstance(t1_args[1], UniqueConstraint) * \
            isinstance(t2_args[0], PrimaryKeyConstraint)

        return self.assertTrue(test_bool)

# ==============================================================================

if __name__ == '__main__':
    unittest.main() 
