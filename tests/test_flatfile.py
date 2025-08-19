# ==============================================================================

import unittest
import pdb
from datetime import datetime, timezone

from sqlalchemy import Column
from sqlalchemy import DateTime, Float, Integer, String

from libra import Schema

# ==============================================================================
# Class to handle flat file reading (from_string())

class Test_FromString(unittest.TestCase):
    """Test `from_string()` method for an ORM on a single string"""

    line : str = '1 9999999999.999 "testing my schema" "2025-10-31 12:15:10"'
    lines : list[str] = '1 9999999999.999 "testing my schema" "2025-10-31 12:15:10"\n' \
        '2 9999999999.999 "testing my schema again!" "2025-10-31 12:15:11"\n' \
        '3 1000.0 testing "2025-10-31 12:15:12"'
    linedel : str = '1, 9999999999.999, "testing my schema", "2025-10-31 12:15:10"'

    def test_fromstring(self):
        """Test from_string() with no additional parameters on a single line"""

        schema = Schema('FlatFile Schema')

        @schema.add_model
        class mymodel:
            column01 = Column(Integer)
            column02 = Column(Float(precision = 53))
            column03 = Column(String(length = 12))
            column04 = Column(DateTime, onupdate = datetime.now(timezone.utc))

            pk = ['column01']

        class MyModel(schema.mymodel): 
            __tablename__ = 'mytable'

        mod = MyModel().from_string(self.line)

        self.assertEqual(mod.column01, 1)
        self.assertEqual(mod.column02, 9999999999.999)
        self.assertEqual(mod.column03, 'testing my schema')
        self.assertEqual(mod.column04, datetime(2025, 10, 31, 12, 15, 10))

    def test_fromstring_multilines(self):
        """Test from_string() with no additional parameters on multiple lines"""

        schema = Schema('FlatFile Schema')

        @schema.add_model
        class mymodel:
            column01 = Column(Integer)
            column02 = Column(Float(precision = 53))
            column03 = Column(String(length = 12))
            column04 = Column(DateTime, onupdate = datetime.now(timezone.utc))

            pk = ['column01']

        class MyModel(schema.mymodel): 
            __tablename__ = 'mytable'

        modlist = [MyModel().from_string(l) for l in self.lines.splitlines()]

        self.assertEqual(modlist[0].column01, 1)
        self.assertEqual(modlist[0].column02, 9999999999.999)
        self.assertEqual(modlist[0].column03, "testing my schema")
        self.assertEqual(modlist[0].column04, datetime(2025, 10, 31, 12, 15, 10))
        self.assertEqual(modlist[1].column01, 2)
        self.assertEqual(modlist[1].column02, 9999999999.999)
        self.assertEqual(modlist[1].column03, "testing my schema again!")
        self.assertEqual(modlist[1].column04, datetime(2025, 10, 31, 12, 15, 11))
        self.assertEqual(modlist[2].column01, 3)
        self.assertEqual(modlist[2].column02, 1000.0)
        self.assertEqual(modlist[2].column03, "testing")
        self.assertEqual(modlist[2].column04, datetime(2025, 10, 31, 12, 15, 12))

    def test_fromstring_customdelimiter(self):
        """Test from_string() with a comma as delimiter"""

        schema = Schema('FlatFile Schema')

        @schema.add_model
        class mymodel:
            column01 = Column(Integer)
            column02 = Column(Float(precision = 53))
            column03 = Column(String(length = 12))
            column04 = Column(DateTime, onupdate = datetime.now(timezone.utc))

            pk = ['column01']

        class MyModel(schema.mymodel): 
            __tablename__ = 'mytable'

        mod = MyModel().from_string(self.linedel, delimiter = ',')

        self.assertEqual(mod.column01, 1)
        self.assertEqual(mod.column02, 9999999999.999)
        self.assertEqual(mod.column03, 'testing my schema')
        self.assertEqual(mod.column04, datetime(2025, 10, 31, 12, 15, 10))

# ==============================================================================
# Class to handle flat file writing (to_string())

class Test_ToString(unittest.TestCase):
    """Test `to_string()` method for an ORM on a single string"""

    def test_tostring(self):
        """Test to_string() with no additional parameters on a single ORM"""

        schema = Schema('FlatFile Schema')

        @schema.add_model
        class mymodel:
            column01 = Column(Integer)
            column02 = Column(Float(precision = 53))
            column03 = Column(String(length = 12))
            column04 = Column(DateTime, onupdate = datetime.now(timezone.utc))

            pk = ['column01']

        class MyModel(schema.mymodel): 
            __tablename__ = 'mytable'
        
        mod = MyModel(1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 10))

        string = mod.to_string()

        self.assertEqual(string, '1 9999999999.999 "testing my schema" "2025-10-31 12:15:10"\n')
    
    def test_tostring_multilines(self):
        """Test to_string() with no additional parameters on multiple lines"""

        schema = Schema('FlatFile Schema')

        @schema.add_model
        class mymodel:
            column01 = Column(Integer)
            column02 = Column(Float(precision = 53))
            column03 = Column(String(length = 12))
            column04 = Column(DateTime, onupdate = datetime.now(timezone.utc))

            pk = ['column01']

        class MyModel(schema.mymodel): 
            __tablename__ = 'mytable'
        
        modlist = [
            MyModel(1, 9999999999.999, "testing my schema", datetime(2025, 10, 31, 12, 15, 10)),
            MyModel(2, 9999999999.999, "testing my schema again!", datetime(2025, 10, 31, 12, 15, 11)),
            MyModel(3, 1000.0, 'testing', datetime(2025, 10, 31, 12, 15, 12))
        ]

        stringlist = [mod.to_string() for mod in modlist]

        self.assertEqual(stringlist[0], '1 9999999999.999 "testing my schema" "2025-10-31 12:15:10"\n')
        self.assertEqual(stringlist[1], '2 9999999999.999 "testing my schema again!" "2025-10-31 12:15:11"\n')
        self.assertEqual(stringlist[2], '3 1000.0 testing "2025-10-31 12:15:12"\n')

    def test_tostring_customdelimiter(self):
        """Test to_string() with a comma as delimiter"""

        schema = Schema('FlatFile Schema')

        @schema.add_model
        class mymodel:
            column01 = Column(Integer)
            column02 = Column(Float(precision = 53))
            column03 = Column(String(length = 12))
            column04 = Column(DateTime, onupdate = datetime.now(timezone.utc))

            pk = ['column01']

        class MyModel(schema.mymodel): 
            __tablename__ = 'mytable'
        
        mod = MyModel(1, 9999999999.999, 'testing my schema', datetime(2025, 10, 31, 12, 15, 10))

        string = mod.to_string(delimiter = ',')

        self.assertEqual(string, '1,9999999999.999,"testing my schema","2025-10-31 12:15:10"\n')

# ==============================================================================

if __name__ == '__main__':
    unittest.main()