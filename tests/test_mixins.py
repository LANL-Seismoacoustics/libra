# ==============================================================================

import os
import unittest
import pdb
from datetime import datetime, timezone

import pandas as pd
from pandas.testing import assert_frame_equal
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import Column
from sqlalchemy import DateTime, Float, Integer, String

from libra import Schema
from libra.mixins.flatfile import string_formatter
from libra.func import (
    from_string, to_string, to_dframe, simple_qc
)

# ==============================================================================
# Test Model Instance added to a Schema

schema = Schema('FlatFile Test Schema')

@schema.add_model
class mymodel01:
    column01 = Column(Integer, info = {'format' : '9d'})
    column02 = Column(Float(precision = 53), info = {'format' : '17.5f'})
    column03 = Column(String(12), info = {'format' : '15.15s'})
    column04 = Column(DateTime, info = {'format' : '%Y-%m-%d %H:%M:%S'})

    pk = ['column01']

@schema.add_model
class mymodel02:
    column05 = Column(Integer, info = {'format' : '9d'})
    column06 = Column(Float(precision = 53), info = {'format' : '17.5f'})
    column07 = Column(String(12)) # Column07 formatted as '{2:None}'
    column08 = Column(DateTime, info = {'format' : '%Y-%m-%d %H:%M:%S'})

    pk = ['column05']

class MyModel01(schema.mymodel01): __tablename__ = 'Test_MyModel01'
class MyModel02(schema.mymodel02): __tablename__ = 'Test_MyModel02'
# ==============================================================================

class TestSuper:
    """Parent class to handle setup/teardown operations of child classes."""

    def setUp(self):
        """Initialize a database connection and tables."""

        super().setUp()

        connection = 'sqlite:///tests/resources/libra_test.db'

        # Get connection and create tables
        self.engine = create_engine(connection)
        self.session = Session(self.engine)
        schema.base.metadata.create_all(self.engine)

        # Test FlatFile
        self.ffile = 'tests/resources/ff_write.out'

        # Add data to tables
        self.session.add(MyModel01(1, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 10)))
        self.session.add(MyModel01(2, 1000.0, 'testing schema', datetime(2025, 10, 31, 12, 15, 11)))
        self.session.add(MyModel01(3, 999.1, 'testing', datetime(2025, 10, 31, 12, 15, 12)))
        self.session.add(MyModel01(4, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 13)))
        self.session.add(MyModel02(1, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 10)))
        self.session.add(MyModel02(2, 1000.0, 'testing schema', datetime(2025, 10, 31, 12, 15, 11)))
        self.session.add(MyModel02(3, 999.1, 'testing', datetime(2025, 10, 31, 12, 15, 12)))
        self.session.add(MyModel02(4, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 13)))

        self.session.commit()

    def tearDown(self):
        """Remove created tables and test files written"""

        MyModel01.__table__.drop(self.engine)
        MyModel02.__table__.drop(self.engine)

        self.session.commit()

        try:
            os.remove(self.ffile)
        except OSError:
            pass
            
        super().tearDown()

# ==============================================================================
# Classes to test FlatFile Mixin functionality

class Test_StringFormatter(TestSuper, unittest.TestCase):
    """Class to test the string_formatter function"""

    def setUp(self):
        super().setUp()

    def test_stringformatter_ormprop_defined(self):
        """Ensure _format_string for ORM is defined if all info format keys defined"""

        mod = MyModel01(1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 12))

        return self.assertEqual(mod._format_string, '{0:9d} {1:17.5f} {2:15.15s} {3:%Y-%m-%d %H:%M:%S}\n')

    def test_stringformatter_ormprop_undefined(self):
        """Ensure _format_string for ORM is None if all info format keys undefined"""

        mod = MyModel02(1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 12))

        return self.assertEqual(mod._format_string, '{0:9d} {1:17.5f} {2:None} {3:%Y-%m-%d %H:%M:%S}\n')

    def test_stringformatter_dbquery_whole(self):
        """Test string_formatter on a database query that returns a whole ORM"""

        recs = self.session.query(MyModel01).all()

        truth = ['        1        1000.00000 testing         2025-10-31 12:15:10\n', '        2        1000.00000 testing schema  2025-10-31 12:15:11\n', '        3         999.10000 testing         2025-10-31 12:15:12\n', '        4        1000.00000 testing         2025-10-31 12:15:13\n']

        [self.assertEqual(rec._format_string.format(*rec), t) for rec, t in zip(recs, truth)]

    def test_stringformatter_dbquery_partial(self):
        """Test string_formatter on a database query that returns a partial ORM"""

        recs = self.session.query(MyModel01.column01, MyModel01.column04).all()
        fmt = string_formatter(schema.base.metadata, ['column01', 'column04'])

        truth = ['        1 2025-10-31 12:15:10\n', '        2 2025-10-31 12:15:11\n', '        3 2025-10-31 12:15:12\n', '        4 2025-10-31 12:15:13\n']

        [self.assertEqual(fmt.format(*rec), t) for rec, t in zip(recs, truth)]

    def test_stringformatter_dbquery_undefined_whole(self):
        """Test stringformatter from a db query where column format undefined"""

        rec = self.session.query(MyModel02).first()
        
        with self.assertRaises(ValueError):
            rec._format_string.format(*rec)

    def test_stringformatter_dbquery_undefined_partial_good(self):
        """Test string_formatter on dbquery where partial column formatting has format defined"""

        rec = self.session.query(MyModel02.column05, MyModel02.column06).first() # column05, column06 have format defined
        fmt = string_formatter(schema.base.metadata, ['column05', 'column06'])

        truth = '        1        1000.00000\n'

        self.assertEqual(fmt.format(*rec), truth)
    
    def test_stringformatter_dbquery_undefined_partial_bad(self):
        """Test string_formatter on dbquery where partial column formatting does not have format defined"""

        rec = self.session.query(MyModel02.column05, MyModel02.column07).first() # column07 does not have format defined
        fmt = string_formatter(schema.base.metadata, ['column05', 'column07'])

        with self.assertRaises(ValueError):
            fmt.format(*rec)

    def tearDown(self):
        super().tearDown()

class Test_FromString(TestSuper, unittest.TestCase):
    """Test from_string() function"""

    def setUp(self):
        super().setUp()

    def test_fromstring_singleline(self):
        """Test from_string() function on a single line."""

        line : str = '        1        1000.00000 testing         2025-10-31 12:15:10\n'

        mod = from_string(MyModel01, [line])[0]

        self.assertEqual(mod.column01, 1)
        self.assertEqual(mod.column02, 1000.0)
        self.assertEqual(mod.column03, 'testing')
        self.assertEqual(mod.column04, datetime(2025, 10, 31, 12, 15, 10))

    def tearDown(self):
        super().tearDown()

class Test_ToString(TestSuper, unittest.TestCase):
    """Test to_string() function"""

    def setUp(self):
        super().setUp()
    
    def test_fromstring_singleline(self):
        """Test from_string() function on a single line."""

        line : str = '        1        1000.00000 testing         2025-10-31 12:15:10\n'

        mod = MyModel01(1, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 10))

        string = to_string([mod])[0]

        self.assertEqual(string, line)
    
    def tearDown(self):
        super().tearDown()

# ==============================================================================
# Classes to test Pandas Mixin functionality

class Test_ToDataFrame(TestSuper, unittest.TestCase):
    """Class to test ORM to Pandas DataFrame conversion."""

    def setUp(self):
        super().setUp()

    def test_todframe_single_declared_orm(self):
        """Test to_dframe function on a single OOP declared ORM"""

        mod1 = MyModel01(1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 12))

        dframe_test = to_dframe([mod1])
        dframe_true = pd.DataFrame(
            data = [[1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 12)]],
            columns = ['column01', 'column02', 'column03', 'column04']
        )

        self.assertIsNone(assert_frame_equal(dframe_test, dframe_true))
    
    def test_todframe_multiple_declared_orms(self):
        """Test to_dframe function on multiple OOP declared ORMs"""

        mod1 = MyModel01(1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 12))
        mod2 = MyModel01(2, 1000.0, 'testing to_dframe()', datetime(2025, 10, 31, 12, 15, 13))
        mod3 = MyModel01(3, 100., 'testing to_dframe()', datetime(2025, 10, 31, 12, 15, 14))

        dframe_test = to_dframe([mod1, mod2, mod3])
        dframe_true = pd.DataFrame(
            data = [
                [1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 12)],
                [2, 1000.0, 'testing to_dframe()', datetime(2025, 10, 31, 12, 15, 13)],
                [3, 100., 'testing to_dframe()', datetime(2025, 10, 31, 12, 15, 14)]
            ],
            columns = ['column01', 'column02', 'column03', 'column04']
        )

        self.assertIsNone(assert_frame_equal(dframe_test, dframe_true))

    def test_todframe_single_queried_orm(self):
        """Test to_dframe() on a single-line ORM queried from a database."""

        mod1 = self.session.query(MyModel01).filter(MyModel01.column01 == 1)[0]

        dframe_test = to_dframe([mod1])
        dframe_true = pd.DataFrame(
            data = [[1, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 10)]],
            columns = ['column01', 'column02', 'column03', 'column04']
        )

        self.assertIsNone(assert_frame_equal(dframe_test, dframe_true))

    def test_todframe_multiple_queried_orms(self):
        """Test to_dframe() on a multi-line ORM query from a database."""

        mod = self.session.query(MyModel01).all()

        dframe_test = to_dframe(mod)
        dframe_true = pd.DataFrame(
            data = [
                [1, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 10)],
                [2, 1000.0, 'testing schema', datetime(2025, 10, 31, 12, 15, 11)],
                [3, 999.1, 'testing', datetime(2025, 10, 31, 12, 15, 12)],
                [4, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 13)]
            ],
            columns = ['column01', 'column02', 'column03', 'column04']
        )

        self.assertIsNone(assert_frame_equal(dframe_test, dframe_true))

    def tearDown(self):
        super().tearDown()

class Test_FromDataFrame(TestSuper, unittest.TestCase):
    """Class to test Pandas DataFrame to ORM conversion."""

    def setUp(self):
        super().setUp()
    
    def tearDown(self):
        super().tearDown()

# ==============================================================================
# Classes to test QC functionality

class Test_QC(TestSuper, unittest.TestCase):
    """Class to test quality control functionality for ORMs."""

    def setUp(self):
        super().setUp()

    def test_qc_initialization(self):
        mod1 = MyModel01(1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 12))

        simple_qc([mod1], schema)
    
    def tearDown(self):
        super().tearDown()

# ==============================================================================

if __name__ == '__main__':
    unittest.main()