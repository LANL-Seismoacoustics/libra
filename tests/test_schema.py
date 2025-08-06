"""
Brady Spears
7/18/25

Test scripts for the `Schema` object, including load/write functionality.
"""

# ==============================================================================

import os
import pdb
import uuid
import unittest
import pickle
import sqlite3
from datetime import datetime, timedelta, timezone

import yaml
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Constraint, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import (
    DateTime, Integer, Float, String, VARCHAR
)

from libra import Schema
from libra.schema import LIBRA_YAML
from libra.schema import (
    DictionaryTransferStrategy,
    YAMLFileTransferStrategy,
    DatabaseTransferStrategy,
    TransferStrategy
)
from libra.metaclass import MetaClass
from libra.util import TypeMap
from libra.util.settings import _SchemaSettings
from libra.util import (
    DictionarySettings,
    YAMLFileSettings,
    DatabaseSettings
)
from resources.schema_dict import TEST_DICT

# ==============================================================================
# Classes to handle Schema Initialization

class Test_SchemaInit(unittest.TestCase):
    """Test Initialization of the Schema object"""

    schema_name : str = 'Test Schema'
    custom_var  : str = 'Custom Variable'
    builtin_typemap : TypeMap = TypeMap({String : VARCHAR})

    def test_name_init(self):
        """Test simplest form of initialization - just a name"""

        schema = Schema(self.schema_name)

        return self.assertEqual(schema.name, self.schema_name)
    
    def test_description_init(self):
        """Test initialization with a description."""

        description = 'My test schema'

        schema = Schema(self.schema_name, description = description)

        return self.assertEqual(schema.description, description)

    def test_custom_metaclass(self):
        """Test initialization with custom metaclass"""

        class CustomMetaclass(DeclarativeMeta):
            """Custom Metaclass to override Libra's built-in Metaclass"""

            def __init__(cls, clsname, parents, dct) -> None:
                """
                Execute sqlalchemy's declarative base __init__ function & add a
                'custom variable' to the base class after inherited __init__.
                """

                super(CustomMetaclass, cls).__init__(clsname, parents, dct)

                # Set a random variable or do other custom things
                cls.custom_variable = self.custom_var

        schema = Schema(self.schema_name, metaclass = CustomMetaclass)

        return self.assertEqual(schema.base.custom_variable, self.custom_var)

    def test_custom_typemap_builtin(self):
        """Test initialization with custom typemap using SQLA built-in types"""

        schema = Schema(self.schema_name, typemap = self.builtin_typemap)

        return self.assertEqual(schema.typemap, self.builtin_typemap)

    def test_custom_typemap_custom(self):
        """Test initialization with custom typemap using custom types"""

        class VARCHAR2Byte(String): 
            """Custom byte-encoded VARCHAR2 type specific to Oracle Dialect"""
            ...
        
        @compiles(VARCHAR2Byte)
        def compile_varchar2byte(_type, compiler, **kw):

            le = _type.length

            return 'VARCHAR(%i BYTE)' % len # Returns this string to DDL
        
        custom_typemap : TypeMap = {String : VARCHAR2Byte}

        schema = Schema(self.schema_name, typemap = custom_typemap)

        return self.assertEqual(schema.typemap, custom_typemap)
         
    def test_single_mixins(self):
        """Test schema initialization with a single mixin class"""

        class MyMixin01: 
            ...

        schema = Schema(self.schema_name, mixins = (MyMixin01,))

        return self.assertEqual(type(schema.mixins[0]), type(MyMixin01))
    
    def test_multiple_mixins(self):
        """Test schema initialization with multiple mixin classes"""

        class MyMixin01: ...
        class MyMixin02: ...
        class MyMixin03: ...

        schema = Schema(self.schema_name, mixins = (MyMixin01, MyMixin02, MyMixin03))

        return self.assertEqual(
            [type(schema.mixins[0]), type(schema.mixins[1]), type(schema.mixins[2])],
            [type(MyMixin01), type(MyMixin02), type(MyMixin03)]
        )

# ==============================================================================
# Classes to handle the propagation of Initialized Properties to Child classes

class Test_SchemaInitPropagation(unittest.TestCase):
    """Test propagation of initialized parameters to children of schema"""

    schema_name : str = 'Test Schema'
    custom_var  : str = 'Custom Variable'
    builtin_typemap : TypeMap = TypeMap({'String' : VARCHAR})

    class TestModel:
        column01 = Column(Integer)
        column02 = Column(Float(precision = 53))
        column03 = Column(String(30))
        column04 = Column(DateTime)

        pk = ['column01']
        uq = ['column02', 'column03']

    
    def test_name_init(self):
        """Simply ensure the schema name is initialized as expected"""

        schema = Schema(self.schema_name)
        
        schema.add_model(self.TestModel)

        return self.assertEqual(schema.name, self.schema_name)

    def test_description_init(self):
        """Test description initialization"""

        description ='Testing adding a description to the schema.'

        schema = Schema(self.schema_name, description = description)

        schema.add_model(self.TestModel)

        return self.assertEqual(schema.description, description)

    def test_custom_metaclass(self):
        """Test propagation of the metaclass onto attributes of schema"""

        class CustomMetaclass(DeclarativeMeta):
            """Custom Metaclass to override Libra's built-in Metaclass"""

            def __init__(cls, clsname, parents, dct) -> None:
                """
                Execute sqlalchemy's declarative base __init__ function & add a
                'custom variable' to the base class after inherited __init__.
                """

                super(CustomMetaclass, cls).__init__(clsname, parents, dct)

                # Set a random variable or do other custom things
                cls.custom_variable = self.custom_var
            
        schema = Schema(self.schema_name, metaclass = CustomMetaclass)

        schema.add_model(self.TestModel)

        return self.assertEqual(schema.TestModel.custom_variable, self.custom_var)

    def test_custom_typemap_builtin(self):
        """Test propagation of built-in SQLA types to children of schema"""

        schema = Schema(self.schema_name, typemap = self.builtin_typemap)

        schema.add_model(self.TestModel)
        
        test = schema.TestModel

        return self.assertEqual(type(test.column03.type), type(VARCHAR()))

    def test_custom_typemap_custom(self):
        """Test propagation of custom SQLA types to children of schema"""

        class VARCHAR2Byte(String): 
            """Custom byte-encoded VARCHAR2 type specific to Oracle Dialect"""
            ...
        
        @compiles(VARCHAR2Byte)
        def compile_varchar2byte(_type, compiler, **kw):

            len = _type.length

            return 'VARCHAR(%i BYTE)' % len # Returns this string to DDL
        
        custom_typemap : TypeMap = TypeMap({'String' : VARCHAR2Byte})

        schema = Schema(self.schema_name, typemap = custom_typemap)

        schema.add_model(self.TestModel)

        test = schema.TestModel

        return self.assertEqual(type(test.column03.type), type(VARCHAR2Byte()))

    def test_single_mixins(self):
        """Test propagation to models of a single mixin class"""

        class MyMixin01:
            def _message(self, message : str) -> str:
                return message
            
        schema = Schema(self.schema_name, mixins = (MyMixin01,))

        schema.add_model(self.TestModel)

        class Test(schema.TestModel):
            __tablename__ = 'test'

        test = Test(column01 = 1)

        self.assertEqual(test._message('Hello World'), 'Hello World')

    def test_multiple_mixins(self):
        """Test schema initialization with multiple mixin classes"""

        class MyMixin01:
            def _message(self, message : str) -> str:
                return message
            
        class MyMixin02:
            def _get_col4(self, format : str = '%Y/%m/%d %H:%M:%S') -> str:
                return datetime.strftime(self.column04, format)
            
        class MyMixin03:
            column05 = Column(String(length = 15), default = 'Default Text')

        schema = Schema(self.schema_name, mixins = (MyMixin01, MyMixin02, MyMixin03))
        schema.add_model(self.TestModel)

        class Test(schema.TestModel):
            __tablename__ = 'Test'

        test = Test(
            column01 = 1,
            column02 = 43.0, 
            column03 = 'testing', 
            column04 = datetime(2025, 1, 21, 14, 12, 1)
        )
        self.assertEqual(test._message('testing'), 'testing')
        self.assertEqual(test._get_col4(), '2025/01/21 14:12:01')
        self.assertEqual(test.column05, 'Default Text')

# ==============================================================================
# Classes to ensure appropriate Schema Dispatch Strategies

class Test_SchemaDispatchStrategy(unittest.TestCase):
    """Test that transfer strategies are appropriately mapped."""

    def test_dictionary_dispatch(self):
        """DictionarySettings maps to DictionaryTransferStrategy"""

        settings = DictionarySettings(dictionary = {})

        strategy = Schema('Test')._dispatch_strategy(settings)

        return self.assertEqual(strategy, DictionaryTransferStrategy)
    
    def test_yamlfile_dispatch(self):
        """YAMLFileSettings maps to YAMLFileStrategy"""

        settings = YAMLFileSettings(file = '')

        strategy = Schema('Test')._dispatch_strategy(settings)

        return self.assertEqual(strategy, YAMLFileTransferStrategy)
    
    def test_database_dispatch(self):
        """DatabaseSettings maps to YAMLFileStrategy"""

        settings = DatabaseSettings(connection_str = '')

        strategy = Schema('Test')._dispatch_strategy(settings)

        return self.assertEqual(strategy, DatabaseTransferStrategy)

    def test_custom_dispatch(self):
        """Custom Settings map to Custom Transfer Strategy"""

        class CustomTransferStrategy(TransferStrategy):
            def load(): ... # Required as TransferStrategy is ABC
            def write(): ...
        
        class CustomSettings(_SchemaSettings):
            custom_variable : str
            transfer_strategy : type[CustomTransferStrategy] = CustomTransferStrategy
        
        settings = CustomSettings(custom_variable = 'My custom variable')

        strategy = Schema('Test')._dispatch_strategy(settings)

        return self.assertEqual(strategy, CustomTransferStrategy)


# ==============================================================================
# Classes to handle Schema Loading

class Test_SchemaLoad_Dictionary(unittest.TestCase):
    """Test Schema Load functionality for Python Dictionaries"""

    schema_name : str = 'Test Schema 1'
    dictionary : dict = TEST_DICT
    settings : DictionarySettings = DictionarySettings(dictionary = dictionary)
    pickled_data = pickle.dumps({'name' : 'Testing'})

    def test_load_dictionary(self):
        """Test loading of schema definition dictionary"""

        schema = Schema(self.schema_name).load(self.settings)

        class Model01(schema.model01): __tablename__ = 'test1'
        class Model02(schema.model02): __tablename__ = 'test2'
        class Model03(schema.model03): __tablename__ = 'test3'

        vals_01 = {'column01' : 1, 'column14' : 'testing', 'column02' : True, 'column05' : 43.0, 'column06' : 'a', 'column16' : datetime(2025, 7, 28, 12, 0, 0), 'column04' : datetime(2025, 7, 28, 12, 0, 0)}
        vals_02 = {'column08' : 1, 'column09' : datetime(2025, 7, 28, 12, 0, 0), 'column09' : timedelta(4), 'column12' : self.pickled_data, 'column18' : 'testing', 'column04' : datetime(2025, 7, 28, 12, 0, 0)}
        vals_03 = {'column13' : 1, 'column11' : 9999.999, 'column19' : uuid.uuid4(), 'column17' : 'testing', 'column15' : 'testing2', 'column10' : 2, 'column07' : 43.0, 'column04' : datetime(2025, 7, 28, 12, 0, 0)}

        mod1 = Model01(**vals_01)
        mod2 = Model02(**vals_02)
        mod3 = Model03(**vals_03)

        for model, values in zip([mod1, mod2, mod3], [vals_01, vals_02, vals_03]):
            for key, val in values.items():
                self.assertEqual(getattr(model, key), val)


class Test_SchemaLoad_YAML(unittest.TestCase):
    """Test Schema Load functionality for YAML Files"""

    schema_name : str = 'Test Schema 1'
    file : str | os.PathLike = 'tests/resources/libra_test.yaml'
    settings : YAMLFileSettings = YAMLFileSettings(file = file)
    pickled_data = pickle.dumps({'name' : 'Testing'})

    def test_load_yamlfile(self):
        """Test loading of schema definition YAML file"""

        schema = Schema(self.schema_name).load(self.settings)

        class Model01(schema.model01): __tablename__ = 'test1'
        class Model02(schema.model02): __tablename__ = 'test2'
        class Model03(schema.model03): __tablename__ = 'test3'

        vals_01 = {'column01' : 1, 'column14' : 'testing', 'column02' : True, 'column05' : 43.0, 'column06' : 'a', 'column16' : datetime(2025, 7, 28, 12, 0, 0), 'column04' : datetime(2025, 7, 28, 12, 0, 0)}
        vals_02 = {'column08' : 1, 'column09' : datetime(2025, 7, 28, 12, 0, 0), 'column09' : timedelta(4), 'column12' : self.pickled_data, 'column18' : 'testing', 'column04' : datetime(2025, 7, 28, 12, 0, 0)}
        vals_03 = {'column13' : 1, 'column11' : 9999.999, 'column19' : uuid.uuid4(), 'column17' : 'testing', 'column15' : 'testing2', 'column10' : 2, 'column07' : 43.0, 'column04' : datetime(2025, 7, 28, 12, 0, 0)}

        mod1 = Model01(**vals_01)
        mod2 = Model02(**vals_02)
        mod3 = Model03(**vals_03)
        
        for model, values in zip([mod1, mod2, mod3], [vals_01, vals_02, vals_03]):
            for key, val in values.items():
                self.assertEqual(getattr(model, key), val)


class Test_SchemaLoad_Database(unittest.TestCase):
    """Test Schema Load functionality for Database tables"""

    schema_name : str = 'Test Schema 1'
    connection : str = 'sqlite:///tests/resources/libra_test.db'
    settings : DatabaseSettings = DatabaseSettings(connection_str = connection)
    pickled_data = pickle.dumps({'name' : 'Testing'})
    engine : sqlalchemy.Engine = create_engine(connection)
    session : Session = Session(bind = engine)

    def setUp(self):
        """Create & populate Libra schema definition tables"""

        with open('tests/resources/insert/test_schemas.sql', 'r') as sql_file:
            sql_script = sql_file.read()
        
        db =  sqlite3.connect(self.connection.replace('sqlite:///', ''))

        cursor = db.cursor()
        cursor.executescript(sql_script)

        db.commit()

        db.close()

    def test_load_database(self):
        """Test loading schema definition from database tables"""

        schema = Schema(self.schema_name).load(self.settings)

        class Model01(schema.model01): __tablename__ = 'test1'
        class Model02(schema.model02): __tablename__ = 'test2'
        class Model03(schema.model03): __tablename__ = 'test3'

        vals_01 = {'column01' : 1, 'column14' : 'testing', 'column02' : True, 'column05' : 43.0, 'column06' : 'a', 'column16' : datetime(2025, 7, 28, 12, 0, 0), 'column04' : datetime(2025, 7, 28, 12, 0, 0)}
        vals_02 = {'column08' : 1, 'column09' : datetime(2025, 7, 28, 12, 0, 0), 'column09' : timedelta(4), 'column12' : self.pickled_data, 'column18' : 'testing', 'column04' : datetime(2025, 7, 28, 12, 0, 0)}
        vals_03 = {'column13' : 1, 'column11' : 9999.999, 'column19' : uuid.uuid4(), 'column17' : 'testing', 'column15' : 'testing2', 'column10' : 2, 'column07' : 43.0, 'column04' : datetime(2025, 7, 28, 12, 0, 0)}

        mod1 = Model01(**vals_01)
        mod2 = Model02(**vals_02)
        mod3 = Model03(**vals_03)
        
        for model, values in zip([mod1, mod2, mod3], [vals_01, vals_02, vals_03]):
            for key, val in values.items():
                self.assertEqual(getattr(model, key), val)
    
    def tearDown(self):
        """Drop Libra schema definition tables and any information in them."""

        db = sqlite3.connect(self.connection.replace('sqlite:///', ''))

        cursor = db.cursor()
        for table in ['schemadescript', 'modeldescript', 'columnassoc', 'columndescript', 'constraintdescript']:
            cursor.execute(f'DROP TABLE IF EXISTS {getattr(self.settings, table)}')
        
        db.commit()

        db.close()

# ==============================================================================
# Classes to handle Schema Writing

class Test_SchemaWrite_Dictionary(unittest.TestCase):
    """Test Schema Write functionality for Python Dictionaries"""

    schema_name : str = 'Test Schema 1'
    dictionary : dict = TEST_DICT
    settings : DictionarySettings = DictionarySettings(dictionary = TEST_DICT)
    pickled_data = pickle.dumps({'name' : 'Testing'})

    def test_write_dictionary(self):
        """Test writing of schema definition dictionary"""

        schema = Schema(self.schema_name).load(self.settings)

        schema.name = 'Test Schema 2'
        schema.description = 'Schema #2 for testing purposes'

        schema_dict = schema.write(settings = self.settings)

        self.assertEqual(schema_dict['Test Schema 1']['columns'], schema_dict['Test Schema 2']['columns'])
        self.assertEqual(schema_dict['Test Schema 1']['models'], schema_dict['Test Schema 2']['models'])


class Test_SchemaWrite_YAMLFile(unittest.TestCase):
    """Test Schema Write functionality for YAML Files"""

    schema_name : str = 'Test Schema 1'
    infile : str | os.PathLike = 'tests/resources/libra_test.yaml'
    outfile : str | os.PathLike = 'tests/resources/libra_testwrite.yaml'
    insettings : YAMLFileSettings = YAMLFileSettings(file = infile)
    outsettings : YAMLFileSettings = YAMLFileSettings(file = outfile)
    pickled_data = pickle.dumps({'name' : 'Testing'})

    def test_write_yamlfile(self):
        """Test writing of a yaml file"""

        schema = Schema(self.schema_name).load(self.insettings)

        schema.name = 'Test Schema 2'
        schema.description = 'Schema #2 for testing purposes'

        schema.write(self.outsettings)

        with open(self.insettings.file, 'r') as f1, open(self.outsettings.file, 'r') as f2:
            schema1 = yaml.safe_load(f1)
            schema2 = yaml.safe_load(f2)
        
        self.assertEqual(schema1['Test Schema 1']['columns'], schema2['Test Schema 2']['columns'])
        self.assertEqual(schema1['Test Schema 1']['models'], schema2['Test Schema 2']['models'])

    def tearDown(self):
        if os.path.exists(self.outsettings.file):
            try:
                os.remove(self.outsettings.file)
            except OSError as e:
                print(f'Error deleting file \'{self.outsettings.file}\': {e}')
        else:
            print(f'File \'{self.outsettings.file}\' does not exist.')


class Test_SchemaWrite_Database(unittest.TestCase):
#     """Test Schema Write functionality for database tables"""

    schema_name : str = 'Test Schema 1'
    connection : str = 'sqlite:///tests/resources/libra_test.db'
    settings : DatabaseSettings = DatabaseSettings(connection_str = connection, author = 'bspears-LANL')
    pickled_data = pickle.dumps({'name' : 'Testing'})

    def setUp(self):
        """Create & populate Libra schema definition tables"""

        with open('tests/resources/insert/test_schemas.sql', 'r') as sql_file:
            sql_script = sql_file.read()
        
        db =  sqlite3.connect(self.connection.replace('sqlite:///', ''))

        cursor = db.cursor()
        cursor.executescript(sql_script)

        db.commit()

        db.close()

    def test_write_database(self):
        """Test writing of database tables"""
        
        schema = Schema(self.schema_name).load(self.settings)

        schema.name = 'Test Schema 2'
        schema.description = 'Schema #2 for testing purposes'

        schema.write(self.settings)

        pdb.set_trace()
    
    def tearDown(self):
        """Drop Libra schema definition tables and any information in them."""

        db = sqlite3.connect(self.connection.replace('sqlite:///', ''))

        cursor = db.cursor()
        for table in ['schemadescript', 'modeldescript', 'columnassoc', 'columndescript', 'constraintdescript']:
            cursor.execute(f'DROP TABLE IF EXISTS {getattr(self.settings, table)}')
        
        db.commit()

        db.close()

# ==============================================================================

if __name__ == '__main__':
    unittest.main()
