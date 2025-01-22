import unittest
import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

from libra import Schema
from libra.util import ColumnHandler

# ==============================================================================

class SchemaInitializationTests(unittest.TestCase):
    """Testing Schema initialization method"""

    def test_schema_init_simple(self) -> None:
        """Test creating an empty schema with a name"""

        schema = Schema('Test Schema')

        return self.assertEqual(schema.name, 'Test Schema')

    def test_schema_init_with_custom_declarative_base(self) -> None:
        """Test creating an empty schema with a non-default declarative base"""

        custom_base = declarative_base()

        schema = Schema('Test Schema', base = custom_base)

        return self.assertEqual(schema.base, custom_base)

    def test_schema_init_with_single_mixin(self) -> None:
        """Test creating an empty schema with one added mixin class"""

        class CustomMixin: ...

        schema = Schema('Test Schema', mixins = CustomMixin)

        return self.assertEqual(schema.mixins[0].__name__, 'CustomMixin')

    def test_schema_init_with_multiple_mixin(self) -> None:
        """Test creating an empty schema with one added mixin class"""

        class CustomMixin1: ...
        class CustomMixin2: ...

        schema = Schema('Test Schema', mixins = (CustomMixin1, CustomMixin2))

        mixin_test = *(mixin.__name__ for mixin in schema.mixins),
        mixin_true = ('CustomMixin1', 'CustomMixin2')

        return self.assertEqual(mixin_test, mixin_true)

    def test_schema_init_with_nondefault_colhandler(self) -> None:
        """Test creating empty schema with custom ColumnHandler"""

        class CustomColumnHandler(ColumnHandler):
            # Required methods of ColumnHandler subclass
            def construct() : ...
            def deconstruct() : ...

        schema = Schema('Test Schema', columnhandler = CustomColumnHandler)

        return self.assertEqual(schema.columnhandler.__name__, 'CustomColumnHandler')
    
    def test_schema_init_with_different_typemap(self) -> None:
        """Test to ensure type_map is passed to ColumnHandler object correctly"""
        from sqlalchemy import String, VARCHAR

        type_map = {String : VARCHAR}

        schema = Schema('Test Schema', type_map = type_map)

        return self.assertEqual(schema.columnhandler.type_map, type_map)

    def test_schema_init_nondefault_colhandler_w_custom_type_map(self) -> None:
        """Test to ensure a nondefault type_map can be included with a custom ColumnHandler object"""
        from sqlalchemy import Float, FLOAT

        type_map_true = {Float : FLOAT}

        class CustomColumnHandler(ColumnHandler):
            type_map = type_map_true
            def construct() : ...
            def deconstruct() : ...

        schema = Schema('Test Schema', columnhandler = CustomColumnHandler)

        return self.assertEqual(schema.columnhandler.type_map, type_map_true)

# ==============================================================================

class SchemaRepresentationTests(unittest.TestCase):
    """Testing the Schema representation method"""

    def test_schem_repr(self) -> None:
        """Test Schema.__repr__() method"""

        schema = Schema('My Schema')

        self.assertEqual(str(schema), 'Schema(\'My Schema\')')

# ==============================================================================

class SchemaAddModelTests(unittest.TestCase):
    """Testing the Schema add_model() method"""

    def test_schema_add_model_1(self) -> None:
        """Model defined with 'pk' field defined only"""

        schema = Schema('Test') # Empty Schema object

        @schema.add_model
        class Test_Class:
            column1 = Column(Integer, autoincrement = True)
            column2 = Column(String, nullable = False)
            column3 = Column(Float, default = 1.0)
            column4 = Column(DateTime, default = datetime.datetime.now())

            pk = {'columns' : ['column1', 'column2'], 'name' : 'test_class_pk'}
        
        class Test(schema.Test_Class): 
            __tablename__ = 'Test'

        t = Test(
            column1 = 1, 
            column2 = 'testing', 
            column4 = datetime.datetime(1970, 1, 1, 0, 0, 0)
        )
        
        test_bool = [
            t.column1 == 1,
            t.column2 == 'testing',
            t.column3.arg == 1.0,
            t.column4 == datetime.datetime(1970, 1, 1, 0, 0, 0)
        ]
        
        return self.assertTrue(all(test_bool))
    
# ==============================================================================

if __name__ == '__main__':
    unittest.main()