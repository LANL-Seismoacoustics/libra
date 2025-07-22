"""
Brady Spears
7/18/25

Test scripts for the `Schema` object, including load/write functionality.
"""

# ==============================================================================

import os
import pdb
import unittest
from datetime import datetime, timezone

from sqlalchemy import Column
from sqlalchemy import Constraint, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import (
    DateTime, Integer, Float, String, VARCHAR
)

from libra import Schema
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
from resources.schema_dict import (
    TEST_DICT_01
)

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
    """Test Schema Load functionality for Python Dictionaries."""

    schema_name : str = 'Test Schema Dictionary 1'
    dictionary : dict = TEST_DICT_01
    typemap : TypeMap = TypeMap({'String' : VARCHAR})
    settings = DictionarySettings(dictionary = dictionary)

    def test_load_dictionary(self):
        
        schema = Schema(self.schema_name).load(self.settings)

        class Model01(schema.model01):
            __tablename__ = 'model01'

        model = Model01('testing')

        return self.assertEqual(model.column01, 'testing')

    def test_load_dictionary_w_typemap(self):

        schema = Schema(self.schema_name, typemap = self.typemap).load(self.settings)

        class Model01(schema.model01):
            __tablename__ = 'model01'

        return self.assertEqual(type(Model01.column01.type), type(VARCHAR()))

    def test_load_dictionary_w_mixins(self):
        pass

# ==============================================================================
# Classes to handle Schema Writing

# ==============================================================================

if __name__ == '__main__':
    unittest.main()
