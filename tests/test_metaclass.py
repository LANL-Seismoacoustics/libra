"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Test suite for the Libra custom Metaclass instance
"""

# ==============================================================================

import pdb
import unittest
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.oracle import FLOAT as Float

from libra import LibraMetaClass

# ==============================================================================

BASE = declarative_base(metaclass = LibraMetaClass, constructor = None)

# ==============================================================================
# Abstract Table Instances

class TestModel1(BASE):
    __abstract__ = True

    @declared_attr
    def __table_args__(cls):
        return (
            PrimaryKeyConstraint('column1'),
            UniqueConstraint('column3'),
        )
    
    column1 = Column(Integer, nullable = False)
    column2 = Column(Float(53))
    column3 = Column(String(36))
    column4 = Column(DateTime, default = datetime.now(), onupdate = datetime.now())

class TestModel2(BASE):
    __abstract__ = True

    @declared_attr
    def __table_args__(cls):
        return (
            PrimaryKeyConstraint('column5'),
        )

    column5 = Column(Integer, nullable = False)
    column1 = Column(Integer, nullable = False)
    column6 = Column(DateTime, default = datetime.now(), onupdate = datetime.now())

class TestModel3(BASE):
    __abstract__ = True

    @declared_attr
    def __table_args__(cls):
        return (
            PrimaryKeyConstraint('column7'),
            CheckConstraint("column8 IN ('y', 'n')"),
        )

    column7 = Column(Integer, nullable = False)
    column8 = Column(String(1), nullable = False)
    column5 = Column(Integer, nullable = False)
    column1 = Column(Integer, nullable = False)
    column9 = Column(DateTime, default = datetime.now())

# ==============================================================================
# Concrete Table Instances

class TestTable1(TestModel1):
    __tablename__ = 'table1'

class TestTable2(TestModel2):
    __tablename__ = 'table2'

class TestTable3(TestModel3):
    __tablename__ = 'table3'

# ==============================================================================

class Metaclass(unittest.TestCase):
    """Testing methods for metaclass instance"""

    def setUp(self):
        _setup(self)

    def test_positional_init(self):
        """Testing positional instantiation"""

        test_table_1 = TestTable1(1, 1.0, str(uuid.uuid4()), datetime(2025, 10, 7, 12, 0, 0))
        test_table_2 = TestTable2(1, 1, datetime(2025, 10, 7, 1, 15, 0))
        test_table_3 = TestTable3(1, 'y', 1, 1, None)
        test_table_4 = TestTable3(2, 'n', 2, 1, None)
        
        # Add data to the database
        self.session.add(test_table_1)
        self.session.add(test_table_2)
        self.session.add(test_table_3)
        self.session.add(test_table_4)

        self.session.commit()

        # Query the data back
        test_query_1 = self.session.query(TestTable1).all()
        test_query_2 = self.session.query(TestTable2).all()
        test_query_3 = self.session.query(TestTable3).all()

        self.assertEqual([x for x in test_query_1[0]], [x for x in test_table_1])
        self.assertEqual([x for x in test_query_2[0]], [x for x in test_table_2])
        self.assertEqual([x for x in test_query_3[0]], [x for x in test_table_3])
        self.assertEqual([x for x in test_query_3[1]], [x for x in test_table_4])
    
    def test_keyword_init(self):
        """Testing keyword instantiation"""

        test_table_1 = TestTable1(column1 = 1, column2 = 1.0, column3 = str(uuid.uuid4()), column4 = datetime(2025, 10, 7, 12, 0, 0))
        test_table_2 = TestTable2(column5 = 1, column1 = 1, column6 = datetime(2025, 10, 7, 1, 15, 0))
        test_table_3 = TestTable3(column7 = 1, column8 = 'y', column5 = 1, column1 = 1)
        test_table_4 = TestTable3(column7 = 2, column8 = 'n', column5 = 2, column1 = 1)

        # Add data to the database
        self.session.add(test_table_1)
        self.session.add(test_table_2)
        self.session.add(test_table_3)
        self.session.add(test_table_4)

        # Query the data back
        test_query_1 = self.session.query(TestTable1).all()
        test_query_2 = self.session.query(TestTable2).all()
        test_query_3 = self.session.query(TestTable3).all()

        self.assertEqual([x for x in test_query_1[0]], [x for x in test_table_1])
        self.assertEqual([x for x in test_query_2[0]], [x for x in test_table_2])
        self.assertEqual([x for x in test_query_3[0]], [x for x in test_table_3])
        self.assertEqual([x for x in test_query_3[1]], [x for x in test_table_4])
    
    def test_class_str(self):
        """Test __str__ method for an ORM instance"""

        test_table = TestTable2(1, 1, datetime(2025, 10, 7, 1, 15, 0))

        self.assertEqual(test_table.__str__(), 'TestTable2(column5=1, column1=1, column6=2025-10-07 01:15:00)')
    
    def test_class_repr(self):
        """Test __repr__ method for an ORM instance"""

        test_table = TestTable2(1, 1, datetime(2025, 10, 7, 1, 15, 0))

        self.assertEqual(test_table.__repr__(), 'TestTable2(column5=1)')
    
    def test_class_getitem(self):
        """Test __getitem__ method for an ORM instance"""

        test_table = TestTable1(1, 1.0, 'testing', datetime(2025, 10, 7, 1, 15, 0))

        self.assertEqual(test_table[2], 'testing')

    def test_class_setitem(self):
        """Test __setitem__ method for an ORM instance"""

        test_table = TestTable1()
        test_table[0] = 1

        self.assertEqual(test_table[0], 1)
    
    def test_class_len(self):
        """Test __len__ method for an ORM instance"""

        test_table = TestTable1()

        self.assertEqual(len(test_table), 4)
    
    def test_class_eq(self):
        """Test __eq__ method for an ORM instance"""

        test_table_1 = TestTable1(1, 1.0, 'test', None)
        test_table_2 = TestTable1(1, 2.0, 'testing', None)

        self.assertTrue(test_table_1 == test_table_2)
    
    def test_class_keys(self):
        """Test keys() method for an ORM instance"""

        test_table = TestTable1()

        self.assertEqual(test_table.keys(), ['column1', 'column2', 'column3', 'column4'])
    
    def test_class_values(self):
        """Test values() method for an ORM instance"""

        test_table = TestTable1(1, 1.0, 'test', datetime(2025, 10, 7, 12, 0, 0))

        self.assertEqual(test_table.values(), [1, 1.0, 'test', datetime(2025, 10, 7, 12, 0, 0)])

    def test_class_items(self):
        """Test items() method for an ORM instance"""

        test_table = TestTable1(1, 1.0, 'test', datetime(2025, 10, 7, 12, 0, 0))
        
        self.assertEqual({k : v for k, v in test_table.items()}, {k : v for k, v in zip(test_table.keys(), test_table.values())})

    def tearDown(self):
        _teardown(self)

# ==============================================================================

def _setup(self):
    """Set up a local SQLite database connection for testing"""

    self.connection = 'sqlite:///:memory:'
    self.engine = create_engine(self.connection, echo = False)
    self.session = Session(self.engine)

    BASE.metadata.create_all(self.engine)

def _teardown(self):
    """Remove tables and reset local SQLite database for testing"""

    TestTable3.__table__.drop(self.engine)
    TestTable2.__table__.drop(self.engine)
    TestTable1.__table__.drop(self.engine)

# ==============================================================================

if __name__ == '__main__':
    unittest.main()