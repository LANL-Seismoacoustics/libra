"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Test Suite for Libra Registry class.
"""

# ==============================================================================

import unittest
from unittest.mock import MagicMock

from libra.registry import Registry
from libra.util import ColumnNotFoundError, ModelNotFoundError

# ==============================================================================

class TestRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = Registry()

        self.registry.columnhandler.deserialize = MagicMock(
            side_effect = lambda d: f'DESERIALIZED({next(iter(d.values()))['type']})'
        )

    # ------------------------
    # Successful Creation Case
    # ------------------------

    def test_create_model_success(self):
        self.registry.columns = {
            'id' : {'type' : 'Integer'},
            'name' : {'type' : 'String(length = 12)'}
        }

        self.registry.models = {
            'User' : {
                'columns' : ['id', 'name'],
                'constraints' : [
                    {'pk' : {'columns' : ['id']}}
                ],
                'extra_attr' : 'test'
            }
        }

        UserClass = self.registry._create('User')

        # Class name
        self.assertEqual(UserClass.__name__, 'User')

        # Type Structure
        self.assertTrue(isinstance(UserClass, type))

        # No unexpected attributes leak
        self.assertFalse(hasattr(UserClass, '__table__'))

        # Column attributes exist
        self.assertIn('id', UserClass.columns)
        self.assertIn('name', UserClass.columns)

        # Ensure deserialize was called
        self.assertEqual(
            UserClass.columns['id'],
            'DESERIALIZED(Integer)'
        )

        self.assertEqual(
            UserClass.columns['name'],
            'DESERIALIZED(String(length = 12))'
        )

        # Constraints preserved
        self.assertEqual(UserClass.constraints, [{'pk' : {'columns' : ['id']}}])

        # Extra attributes preserved
        self.assertEqual(UserClass.extra_attr, 'test')

    # -----------
    # Error Cases
    # -----------

    def test_model_not_found(self):
        with self.assertRaises(ModelNotFoundError):
            self.registry._create('DoesNotExist')
    
    def test_column_not_found(self):

        self.registry.models = {
            'User' : {
                'columns' : ['missing_col'],
                'constraints' : []
            }
        }

        with self.assertRaises(ColumnNotFoundError):
            self.registry._create('User')
    
    # -------------------
    # Deep Copy Isolation
    # -------------------

    def test_registry_data_not_mutated(self):
        self.registry.columns = {
            'id' : {'type' : 'Integer()'}
        }

        original_model_dict = {
            'columns' : ['id'],
            'constraints' : [],
            'meta' : 'data'
        }

        self.registry.models = {'User' : original_model_dict}

        _ = self.registry._create('User')

        # Ensure original model dict was not modified
        self.assertIn('columns', self.registry.models['User'])
        self.assertIn('constraints', self.registry.models['User'])

    # -----------------------------------------
    # Multiple Calls Create Independent Classes
    # -----------------------------------------

    def test_multiple_create_calls_independent(self):

        self.registry.columns = {
            'id' : {'type' : 'Integer()'}
        }

        self.registry.models = {
            'User' : {
                'columns' : ['id'],
                'constraints' : []
            }
        }

        User1 = self.registry._create('User')
        User2 = self.registry._create('User')

        self.assertIsNot(User1, User2)
        self.assertIsNot(User1.columns, User2.columns)

    # -------------------------------------
    # Ensure Deserialized Called Per Column
    # -------------------------------------

    def test_deserialize_called_per_column(self):

        self.registry.columns = {
            'id' : {'type' : 'Integer()'},
            'age' : {'type' : 'Integer()'},
            'name' : {'type' : 'String(length = 128)'},
            'email' : {'type' : 'String(length = 32)'}
        }

        self.registry.models = {
            'User' : {
                'columns' : ['id', 'age', 'name', 'email'],
                'constraints' : [
                    {'pk' : {'columns' : ['id']}},
                    {'uq' : {'columns' : ['email']}}
                ]
            }
        }

        self.registry._create('User')

        self.assertEqual(self.registry.columnhandler.deserialize.call_count, 4)

    # ----------
    # Edge Cases
    # ----------
    
    def test_empty_model(self):
        self.registry.models = {
            'Empty' : {'columns' : [], 'constraints' : []}
        }

        Empty = self.registry._create('Empty')

        self.assertEqual(Empty.columns, {})
        self.assertEqual(Empty.constraints, [])

# ==============================================================================

if __name__ == '__main__':
    unittest.main()