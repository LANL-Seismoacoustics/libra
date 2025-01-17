import os
import unittest
import datetime

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base

from libra import Schema
from test.resources.test_dict_decl import SCHEMA_TEST_DICTIONARY_1

# ==============================================================================
# Dictionary Transfer Strategy

class SchemaLoadDict(unittest.TestCase):
    """Testing Schema.load() method on schemas defined in Python dict format"""

    def test_load_dict_base(self) -> None:
        """Test Schema.load() method with default values"""

        schema = Schema('Libra Test Schema 1').load(
            schema_dict = SCHEMA_TEST_DICTIONARY_1
        )

        pass

# ==============================================================================
# YAML File Transfer Strategy

class SchemaLoadYAML(unittest.TestCase):
    """Testing Schema.load() method on schemas defined in YAML file format"""

    def test_load_yaml_base(self) -> None:
        """Test Schema.load() method with default values"""
        
        schema = Schema('Libra Test Schema 1').load(
            file = './test/resources/test_schema.yaml'
        )
        
        pass

# ==============================================================================
# Database File Transfer Strategy

class SchemaLoadDatabase(unittest.TestCase):
    """Testing Schema.load() method on schemas defined in database format"""

    engine = create_engine('sqlite:///test/resources/test_sqlite.db')
    session = Session(engine)

    def test_load_database_base(self) -> None:
        """Test Schema.load() method with default values"""

        schema = Schema('doc').load(
            session = SchemaLoadDatabase.session,
            colassoc = 'colassoc',
            coldescript = 'coldescript',
            tabdescript = 'tabdescript'
        )

        pass

# ==============================================================================
# Custom Transfer Strategy

class SchemaLoadCustom(unittest.TestCase):
    """Testing Schema.load() method on schemas defined in a custom format"""

# ==============================================================================

if __name__ == '__main__':
    unittest.main()
