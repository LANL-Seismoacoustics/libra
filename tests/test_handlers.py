"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Test Suite for libra.util.handler classes.
"""

# ==============================================================================

import uuid
import unittest

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy.dialects import oracle
from sqlalchemy.ext.compiler import compiles

from libra.util import TypeMap
from libra.util import TypeHandler
from libra.util import ColumnHandler
from libra.util import ConstraintHandler
from libra.util import DEFAULT_SAFE_EVAL_REGISTRY
from libra.util.handler import utcdatetime
from libra.util.handler import _serialize_expr, _deserialize_expr

# ==============================================================================
# TypeMap - unique hash map for Strings to SQLAlchemy Types & vice versa

class TestTypeMap(unittest.TestCase):

    def test_default_mapping_lookup_by_string(self):

        tm = TypeMap()

        self.assertIs(tm["String"], sqlalchemy.String)

    def test_reverse_lookup_by_type(self):

        tm = TypeMap()

        self.assertEqual(tm[sqlalchemy.Integer], "Integer")

    def test_override_existing_key(self):

        tm = TypeMap({"String": sqlalchemy.Text})

        self.assertIs(tm["String"], sqlalchemy.Text)

    def test_override_existing_value(self):

        tm = TypeMap({"VARCHAR2": sqlalchemy.String})

        self.assertNotIn("String", tm())
        self.assertEqual(tm[sqlalchemy.String], "VARCHAR2")

    def test_invalid_identifier_type(self):

        tm = TypeMap()

        with self.assertRaises(TypeError):
            tm[123]


# ==============================================================================
# TypeHandler - serializes & deserializes SQLAlchemy Type objects with params

class TestTypeHandler(unittest.TestCase):
    
    def setUp(self):
        """Create a default TypeHandler with a known typemap."""

        @compiles(oracle.VARCHAR2)
        def compile_byte_varchar2(type_, compiler, **kw):
            return 'VARCHAR2(%i BYTE)' % type_.length

        self.typemap = TypeMap({
            'VARCHAR2' : oracle.VARCHAR2,
            'number' : sqlalchemy.Numeric
        })

        self.handler = TypeHandler(self.typemap)

    # ---------------
    # Deserialization
    # ---------------

    def test_deserialize_no_params(self):
        result = self.handler.deserialize('Integer')
        self.assertIsInstance(result, sqlalchemy.Integer)
    
    def test_deserialize_with_positional_params(self):
        result = self.handler.deserialize('String(12)')
        self.assertIsInstance(result, sqlalchemy.String)
        self.assertEqual(result.length, 12)
    
    def test_deserialize_with_keyword_params(self):
        result = self.handler.deserialize('Float(precision = 53)')
        self.assertIsInstance(result, sqlalchemy.Float)
        self.assertEqual(result.precision, 53)

    def test_deserialize_multiple_params(self):
        result = self.handler.deserialize("String(length = 32, collation = 'utf8')")
        self.assertIsInstance(result, sqlalchemy.String)
        self.assertEqual(result.length, 32)
        self.assertEqual(result.collation, 'utf8')
    
    def test_deserialize_unknown_type_raises(self):
        with self.assertRaises(KeyError):
            self.handler.deserialize('DoesNotExist')
    
    def test_deserialize_custom_type_params(self):
        result = self.handler.deserialize("VARCHAR2(8)")
        self.assertIsInstance(result, oracle.VARCHAR2)
        self.assertEqual(result.length, 8)
        self.assertEqual(result.compile(), 'VARCHAR2(8 BYTE)')
    
    # -------------
    # Serialization
    # -------------

    def test_serialize_type_instance_no_params(self):
        result = self.handler.serialize(sqlalchemy.Integer())
        self.assertEqual(result, 'Integer()')
    
    def test_serialize_type_instance_with_params(self):
        result = self.handler.serialize(sqlalchemy.String(64))
        self.assertEqual(result, 'String(length = 64)')
    
    def test_serialize_type_instance_with_keyword_param(self):
        result = self.handler.serialize(sqlalchemy.Float(precision=53))
        self.assertEqual(result, 'Float(precision = 53)')
    
    def test_serialize_omits_default_params(self):
        result = self.handler.serialize(sqlalchemy.String())
        self.assertEqual(result, 'String()')
    
    def test_serialize_class_reference(self):
        """Non-instantiated types (Integer vs Integer())"""
        result = self.handler.serialize(sqlalchemy.Integer)
    
    def test_serialize_custom_type(self):
        result = self.handler.serialize(sqlalchemy.Numeric(8, 0))
        self.assertEqual(result, 'number(precision = 8, scale = 0)')
    
    # ----------------
    # Round-trip Tests
    # ----------------

    def test_round_trip_simple(self):
        original = 'Integer'
        sa_type = self.handler.deserialize(original)
        serialized = self.handler.serialize(sa_type)
        self.assertEqual(serialized, 'Integer()')
    
    def test_round_trip_with_params(self):
        original = 'String(128)'
        sa_type = self.handler.deserialize(original)
        serialized = self.handler.serialize(sa_type)
        self.assertEqual(serialized, 'String(length = 128)')
    
    def test_round_trip_keyword_params(self):
        original = 'Float(precision = 53, asdecimal = True)'
        sa_type = self.handler.deserialize(original)
        serialized = self.handler.serialize(sa_type)
        self.assertEqual(serialized, 'Float(precision = 53, asdecimal = True)')
    
    def test_round_trip_custom_type(self):
        original = 'VARCHAR2(6)'
        sa_type = self.handler.deserialize(original)
        serialized = self.handler.serialize(sa_type)
        self.assertEqual(serialized, 'VARCHAR2(length = 6)')


# # ==============================================================================
# # ColumnHandler - serializes & deserializes SQLAlchemy Column objects

class TestColumHandler(unittest.TestCase):
    
    def setUp(self):

        def uuid_(_):
            return uuid.uuid4()

        self.typehandler = TypeHandler()
        self.uuid_ = uuid_

        DEFAULT_SAFE_EVAL_REGISTRY.update({'uuid' : uuid_})

        self.handler = ColumnHandler(
            typehandler = self.typehandler
        )
    
    # ---------------
    # Deserialization
    # ---------------

    def test_deserialize_simple_column(self):
        
        coldict = {
            'age' : {
                'type' : 'Integer()',
                'nullable' : False
            }
        }

        col = self.handler.deserialize(coldict)

        self.assertEqual(col.name, 'age')
        self.assertIsInstance(col.type, sqlalchemy.Integer)
        self.assertFalse(col.nullable)

    def test_deserialize_callable_default(self):

        coldict = {
            'created_at' : {
                'type' : 'DateTime()',
                'default' : {'$ref' : 'datetime.now'}
            }
        }

        col = self.handler.deserialize(coldict)

        self.assertEqual(col.name, 'created_at')
        self.assertIsInstance(col.type, sqlalchemy.DateTime)
        self.assertTrue(callable(col.default.arg))
        self.assertEqual(col.default.arg, utcdatetime)

    def test_deserialize_callable_onupdate(self):
        
        coldict = {
            'updated_at' : {
                'type' : 'DateTime()',
                'onupdate' : {'$ref' : 'datetime.now'}
            }
        }

        col = self.handler.deserialize(coldict)

        self.assertTrue(callable(col.onupdate.arg))
        self.assertEqual(col.onupdate.arg, utcdatetime)
        # self.assertTrue(inspect.isfunction(col.onupdate.arg))
        # self.assertEqual(inspect.signature(col.onupdate.arg), inspect.signature(utcdatetime))
    
    def test_deserialize_unknown_ref_raises(self):

        coldict = {
            'bad' : {
                'type' : 'Integer()',
                'default' : {'$ref' : 'os.system'}
            }
        }

        with self.assertRaises(KeyError):
            self.handler.deserialize(coldict)

    def test_deserialize_callable_on_invalid_kwarg_raises(self):

        coldict = {
            'bad' : {
                'type' : 'Integer()',
                'nullable' : {'$ref' : 'datetime.now'}
            }
        }

        with self.assertRaises(ValueError):
            self.handler.deserialize(coldict)
    
    def test_deserialize_requires_single_column(self):
        
        coldict = {
            'a' : {'type' : 'Integer()'},
            'b' : {'type' : 'Integer()'}
        }

        with self.assertRaises(ValueError):
            self.handler.deserialize(coldict)

    def test_deserialize_custom_callable_default(self):

        coldict = {
            'id' : {
                'type' : 'String(length = 36)',
                'default' : {'$ref' : 'uuid'}
            }
        }

        col = self.handler.deserialize(coldict)

        self.assertTrue(callable(col.default.arg))
        self.assertIs(col.default.arg, self.uuid_)

    # -------------
    # Serialization
    # -------------

    def test_serialize_simple_column(self):

        age = Column(sqlalchemy.Integer, nullable = False)

        result = self.handler.serialize('age', age)

        self.assertEqual(
            result,
            {
                'age' : {
                    'type' : 'Integer()',
                    'nullable' : False
                }
            }
        )

    def test_serilaize_with_info(self):
        
        username = Column(sqlalchemy.String(32), info = {'source' : 'user'})

        result = self.handler.serialize('username', username)

        self.assertEqual(
            result,
            {
                'username' : {
                    'type' : 'String(length = 32)',
                    'info' : {'source' : 'user'}
                }
            }
        )
    
    def test_serialize_callable_default(self):

        created_at = Column(sqlalchemy.DateTime(), default = utcdatetime)

        result = self.handler.serialize('created_at', created_at)

        self.assertEqual(
            result,
            {
                'created_at' : {
                    'type' : 'DateTime()',
                    'default' : {'$ref' : 'datetime.now'}
                }
            }
        )
    
    def test_serialize_callable_onupdate(self):

        updated_at = Column(sqlalchemy.DateTime(), onupdate = utcdatetime)

        result = self.handler.serialize('updated_at', updated_at)

        self.assertEqual(
            result,
            {
                'updated_at' : {
                    'type' : 'DateTime()',
                    'onupdate' : {'$ref' : 'datetime.now'}
                }
            }
        )

    def test_serialize_unregistered_callable_raises(self):

        def not_safe(_):
            return 1
        
        bad = Column(sqlalchemy.Integer, default = not_safe)

        with self.assertRaises(ValueError):
            self.handler.serialize('bad', bad)

    def test_serialize_callable_on_invalid_kwarg_raises(self):

        weird = Column(sqlalchemy.Integer, nullable = lambda _: True)
        
        with self.assertRaises(ValueError):
            self.handler.serialize('weird', weird)
    
    def test_serialize_custom_callable_default(self):

        id = Column(sqlalchemy.String(length = 36), default = self.uuid_)

        result = self.handler.serialize('id', id)

        self.assertEqual(
            result,
            {
                'id' : {
                    'type' : 'String(length = 36)',
                    'default' : {'$ref' : 'uuid'}
                }
            }
        )

    # ----------------
    # Round-Trip Tests
    # ----------------

    def test_round_trip_simple(self):

        original = {
            'score' : {
                'type' : 'Float()',
                'nullable' : False
            }
        }

        column = self.handler.deserialize(original)
        serialized = self.handler.serialize('score', column)

        self.assertEqual(serialized, original)

    def test_round_trip_default_callable(self):

        original = {
            'created_at' : {
                'type' : 'DateTime()',
                'default' : {'$ref' : 'datetime.now'}
            }
        }

        column = self.handler.deserialize(original)

        serialized = self.handler.serialize('created_at', column)

        self.assertEqual(serialized, original)

    def test_round_trip_custom_callable(self):
        
        original = {
            'userid' : {
                'type' : 'String(length = 36)',
                'default' : {'$ref' : 'uuid'}
            }
        }

        column = self.handler.deserialize(original)
        serialized = self.handler.serialize('userid', column)

        self.assertEqual(serialized, original)


# ==============================================================================
# ConstraintHandler - serialized & deserialized SQLAlchemy Constraint objects

class TestConstraintHandler(unittest.TestCase):
    
    def setUp(self):
        self.handler = ConstraintHandler()

    # --------------------
    # PrimaryKeyConstraint
    # --------------------

    def test_deserialize_primarykey(self):

        condict = {
            'pk' : {
                'columns' : ['id', 'version'],
                'name' : 'pk_test'
            }
        }

        constraint = self.handler.deserialize(condict)

        self.assertIsInstance(constraint, sqlalchemy.PrimaryKeyConstraint)
        self.assertEqual(constraint._pending_colargs, ['id', 'version'])
        self.assertEqual(constraint.name, 'pk_test')

    def test_round_trip_primarykey(self):

        original = {
            'pk' : {
                'columns' : ['id', 'version'],
                'name' : 'pk_test'
            }
        }

        constraint = self.handler.deserialize(original)
        serialized = self.handler.serialize(constraint)

        self.assertEqual(serialized, original)
    
    # ----------------
    # UniqueConstraint
    # ----------------

    def test_deserialize_uniqueconstraint(self):

        condict = {
            'uq' : {
                'columns' : ['email'],
                'name' : 'uq_email',
                'deferrable' : True
            }
        }

        constraint = self.handler.deserialize(condict)

        self.assertIsInstance(constraint, sqlalchemy.UniqueConstraint)
        self.assertEqual(constraint._pending_colargs, ['email'])
        self.assertEqual(constraint.name, 'uq_email')
        self.assertTrue(constraint.deferrable)
    
    def test_round_trip_uniqueconstraint(self):

        original = {
            'uq' : {
                'columns' : ['email'],
                'name' : 'uq_email',
                'deferrable' : True
            }
        }

        constraint = self.handler.deserialize(original)
        serialized = self.handler.serialize(constraint)

        self.assertEqual(serialized, original)

    # -----
    # Index
    # -----

    def test_deserialize_index(self):

        indict = {
            'ix' : {
                'columns' : ['username'],
                'name' : 'ix_username',
                'unique' : True
            }
        }

        index = self.handler.deserialize(indict)

        self.assertIsInstance(index, sqlalchemy.Index)
        self.assertEqual(index.name, 'ix_username')
        self.assertTrue(index.unique)
        self.assertEqual([c.name for c in index.expressions], ['username'])

    def test_round_trip_index(self):

        original = {
            'ix' : {
                'columns' : ['username'],
                'name' : 'ix_username',
                'unique' : True
            }
        }

        index = self.handler.deserialize(original)
        serialized = self.handler.serialize(index)

        self.assertEqual(serialized, original)
    
    # -------------
    # Failure Cases
    # -------------

    def test_unsupported_constraint_type(self):
        
        condict = {
            'fk' : {
                'columns' : ['user_id'],
                'refcolumns' : ['user.id']
            }
        }

        with self.assertRaises(ValueError):
            self.handler.deserialize(condict)
    
    def test_serialize_unsupported_object(self):

        class FakeConstraint:
            pass

        with self.assertRaises(ValueError):
            self.handler.serialize(FakeConstraint())


# Check Constraint text serialization/deserialization
class TestCheckConstraintSerialization(unittest.TestCase):
    
    def assertRoundTrip(self, expr_str : str):
        
        expr = _deserialize_expr(expr_str)

        self.assertIsInstance(expr, sqlalchemy.sql.ClauseElement)

        serialized = _serialize_expr(expr)
        reparsed = _deserialize_expr(serialized)
        serialized2 = _serialize_expr(reparsed)

        self.assertEqual(serialized, serialized2)
    
    # -----------------
    # Valid Expressions
    # -----------------

    def test_text_clause(self):
        self.assertRoundTrip("text('col1 + col2 > 0')")
    
    def test_func_length(self):
        self.assertRoundTrip("func.length(column('username')) > 3")

    def test_column_in_list(self):
        self.assertRoundTrip("column('status').in_(['y', 'n'])")

    def test_boolean_and_or(self):
        self.assertRoundTrip("and_(column('age') > 18, column('active') == True)")
        self.assertRoundTrip("or_(column('admin') == True, column('superuser') == True)")
    
    def test_nested_boolean(self):
        self.assertRoundTrip("or_(and_(column('age') > 18, column('active') == True), column('admin') == True)")

    def test_func_with_multiple_args(self):
        self.assertRoundTrip("func.concat(column('first'), column('last')) == 'JohnDoe'")

    def test_comparison_operators(self):
        self.assertRoundTrip("column('a') == 1")
        self.assertRoundTrip("column('a') != 1")
        self.assertRoundTrip("column('a') < 5")
        self.assertRoundTrip("column('a') <= 5")
        self.assertRoundTrip("column('a') > 5")
        self.assertRoundTrip("column('a') >= 5")

    def test_arithmetic_operators(self):
        self.assertRoundTrip("column('a') + 5")
        self.assertRoundTrip("column('a') - 2")
        self.assertRoundTrip("column('a') * 3")
        self.assertRoundTrip("column('a') / 4")

    def test_arithmetic_with_comparison(self):
        self.assertRoundTrip("(column('a') + column('b')) > 10")
        self.assertRoundTrip("(column('a') * 2) == 20")
    
    def test_unary_negative(self):
        self.assertRoundTrip("-column('a') == -5")

    def test_unary_not(self):
        self.assertRoundTrip("not column('active')")
    
    def test_python_in_syntax(self):
        self.assertRoundTrip("column('status') in ['y', 'n']")

    def test_not_in(self):
        self.assertRoundTrip("column('status') not in ['x', 'z']")

    def test_python_boolean_syntax(self):
        self.assertRoundTrip("(column('a') > 1) and (column('b') < 5)")
        self.assertRoundTrip("(column('a') > 1) or (column('b') < 5)")

    def test_deep_nesting(self):
        self.assertRoundTrip("and_(column('a') > 1, or_(column('b') < 5, column('c') == 3))")

    def test_boolean_literals(self):
        self.assertRoundTrip("column('active') == True")
        self.assertRoundTrip("column('active') == False")
    
    def test_float_literals(self):
        self.assertRoundTrip("score > 1.5")
    
    def test_nested_functions(self):
        self.assertRoundTrip("func.length(func.trim(column('username'))) > 3")

    # -------------------
    # Invalid Expressions
    # -------------------

    def test_reject_lambda(self):
        with self.assertRaises(ValueError):
            _deserialize_expr("lambda x: x + 1")

    def test_reject_arbitrary_attribute(self):
        with self.assertRaises(ValueError):
            _deserialize_expr("column('a').__class__")

    def test_reject_chained_comparison(self):
        with self.assertRaises(ValueError):
            _deserialize_expr("column('a') < 5 < 10")

    def test_reject_unknown_function(self):
        with self.assertRaises(ValueError):
            _deserialize_expr("eval('1+1')")

    def test_reject_dict_literal(self):
        with self.assertRaises(ValueError):
            _deserialize_expr("{'a' : 1}")
    
    def test_reject_set_literal(self):
        with self.assertRaises(ValueError):
            _deserialize_expr("{1, 2, 3}")
    
    def test_reject_if_expression(self):
        with self.assertRaises(ValueError):
            _deserialize_expr("column('a') if True else column('b')")
    
    # ---------------
    # Stability Tests
    # ---------------

    def test_boolean_canonicalization(self):
        expr = _deserialize_expr("(column('a') > 1) and (column('b') > 2)")

        s1 = _serialize_expr(expr)
        
        expr2 = _deserialize_expr(s1)
        s2 = _serialize_expr(expr2)

        self.assertEqual(s1, s2)
    
    # ----------
    # Edge Cases
    # ----------

    def test_empty_in_list(self):
        self.assertRoundTrip("column('status').in_([])")

    # -----------
    # Other Tests
    # -----------

    def test_all_roundtrip_stability(self):
        expressions = [
            "column('a') == 1",
            "column('a') in [1, 2, 3]",
            "and_(column('a') > 1, column('b') < 5)",
            "func.length(column('name')) > 3",
            "column('a') + 5 > 10"
        ]

        for expr in expressions:
            with self.subTest(expr = expr):
                self.assertRoundTrip(expr)


# ==============================================================================

if __name__ == '__main__':
    unittest.main()
