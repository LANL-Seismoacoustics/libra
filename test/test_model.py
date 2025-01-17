import unittest
import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy import Date, Float, Integer, String
from sqlalchemy.orm import DeclarativeMeta, declarative_base
from sqlalchemy.orm import mapped_column, Mapped

from libra import process_model
from libra import LibraMetaClass
from libra.util.typing import _PreprocessedORM

# ==============================================================================

class TestClassContainer:
    """Container for test classes"""

    classes = []

    def add_class(self, cls : _PreprocessedORM) -> None:
        self.classes.append(cls)

# Test Models
# Defined in various declarative mapping styles supported by SQLAlchemy
# ==============================================================================

test_models = TestClassContainer()

@test_models.add_class
class TestModel_01:
    column = Column(Integer, primary_key = True)

@test_models.add_class
class TestModel_02:
    column = Column(Integer, primary_key = True)

@test_models.add_class
class TestModel_03:
    column = mapped_column(Integer, primary_key = True)

@test_models.add_class
class TestModel_04:
    column_01 = mapped_column(Integer, primary_key = True)
    column_02 : Mapped[str]

@test_models.add_class
class TestModel_05:
    column_01 = mapped_column(Integer, primary_key = True)

class TestModel_06_Parent: ...
@test_models.add_class
class TestModel_06(TestModel_06_Parent):
    """TODO: Parent class thrown out, replaced with declarative base (feature or bug?)"""
    column_01 = mapped_column(Integer, primary_key = True)

@test_models.add_class
class TestModel_07:
    column_01 = Column(Integer)

    pk = ['column_01']

# ==============================================================================

class ModelCastTest(unittest.TestCase):
    """Testing the libra.process_model() function"""
    
    def test_recast_to_decbase(self) -> None:
        """Test assignment of unprocessed class to a child of declarative base class"""

        test_bool = True
        for model in test_models.classes:
            test_model = process_model(model)

            test_bool = test_bool * test_model.__bases__[0].__name__ == 'Base'

        return self.assertEqual(test_bool, True)
    
    def test_recast_w_mixins(self) -> None:
        """Test assignment of unprocessed class to dec base with custom mixin"""

        class Mixin_01: ...
        class Mixin_02: ...

        test_bool = True
        for model in test_models.classes:
            test_model = process_model(model, mixins = (Mixin_01, Mixin_02))

            test_bool = test_bool * test_model.__bases__ == ['Base', 'Mixin_01', 'Mixin_02']

# ==============================================================================

if __name__ == '__main__':
    unittest.main()