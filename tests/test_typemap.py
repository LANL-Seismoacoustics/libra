# ==============================================================================

import unittest

from sqlalchemy import String, VARCHAR
from sqlalchemy.dialects.oracle import VARCHAR2

from libra.util import TypeMap

# ==============================================================================

class Test_TypeMap(unittest.TestCase):

    def test_initialize_no_override(self):
        typemap = TypeMap()

    def test_initialize_w_override(self):
        typemap = TypeMap({'String' : VARCHAR2})

        return self.assertEqual(typemap['String'], VARCHAR2)

    def test_get(self):
        typemap = TypeMap()

        return self.assertEqual(typemap['String'], String)
    
    def test_set_new_key_new_type(self):
        typemap = TypeMap()

        typemap['VARCHAR2'] = VARCHAR2

        return self.assertEqual(typemap['VARCHAR2'], VARCHAR2)

    def test_set_existing_key_new_type(self):
        typemap = TypeMap()

        typemap['String'] = VARCHAR2

        return self.assertEqual(typemap['String'], VARCHAR2)
    
    def test_set_new_key_existing_type(self):
        typemap = TypeMap()

        typemap['VARCHAR2'] = String

        return self.assertEqual(typemap['VARCHAR2'], String)

    def test_set_existing_key_existing_type(self):
        typemap = TypeMap()

        typemap['String'] = VARCHAR

        return self.assertEqual(typemap['String'], VARCHAR)

# ==============================================================================

if __name__ == '__main__':
    unittest.main()
