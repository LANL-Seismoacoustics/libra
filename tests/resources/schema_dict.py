"""
Brady Spears
7/18/25

Contains global dictionaries containing an example schema for testing purposes.
"""

# ==============================================================================

from sqlalchemy.types import (
    BigInteger, Boolean, Date, DateTime, Enum, Double, Float, Integer, Interval,
    LargeBinary, Numeric, PickleType, SmallInteger, String, Text, Time, Unicode,
    UnicodeText, Uuid
)
from sqlalchemy.types import (
    ARRAY, BIGINT, BINARY, BLOB, BOOLEAN, CHAR, CLOB, DATE, DATETIME, DECIMAL,
    DOUBLE, DOUBLE_PRECISION, FLOAT, INT, JSON, INTEGER, NCHAR, NVARCHAR, 
    NUMERIC, REAL, SMALLINT, TEXT, TIME, TIMESTAMP, UUID, VARBINARY, VARCHAR
)

# ==============================================================================

TEST_DICT_01 = {
    'Test Schema Dictionary 1' : {
        'description' : 'Schema for testing purposes.',
        'columns' : {
            'column01' : {
                'sa_coltype' : 'String(30)',
                'description' : ''
            }
        },
        'models' : {
            'model01' : {
                'description' : '',
                'columns' : ['column01'],
                'constraints' : [{'pk' : ['column01']}]
            }
        }
    },
    'Test Schema Dictionary 2' : {
        'description' : 'Additional schema for testing purposes',
        'columns' : {
            'column01' : {
                'sa_coltype' : 'String(30)',
                'nullable' : 'False'
            },
            'column02' : {
                'sa_coltype' : 'DateTime',
                'onupdate' : 'datetime.now(timezone.utc)',
                'default' : 'datetime.now(timezone.utc)'
            }
        },
        'models' : {
            'model01' : {
                'columns' : ['column01', 'column02'],
                'constraints' : [{'pk' : ['column01'], 'uq' : ['column02']}]
            }
        }
    }
}

# ==============================================================================