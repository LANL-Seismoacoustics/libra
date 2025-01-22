import datetime

# Camel-Case SQLAlchemy Datatypes (Generic Types)
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    Double,
    Float,
    Integer,
    Interval,
    LargeBinary,
    Numeric,
    PickleType,
    SmallInteger,
    String,
    Text,
    Time,
    Unicode,
    UnicodeText,
    Uuid
)

# UPPERCASE SQLAlchemy Datatypes (SQL-standard & Multiple Vendor Types)
from sqlalchemy import (
    ARRAY,
    BIGINT,
    BINARY,
    BLOB,
    BOOLEAN,
    CHAR,
    CLOB,
    DATE,
    DATETIME,
    DECIMAL,
    DOUBLE,
    DOUBLE_PRECISION,
    FLOAT,
    INT,
    JSON,
    INTEGER,
    NCHAR,
    NVARCHAR,
    NUMERIC,
    REAL,
    SMALLINT,
    TEXT,
    TIME,
    TIMESTAMP,
    UUID,
    VARBINARY,
    VARCHAR
)

# ==============================================================================

# No plugin-specific keyword arguments
SCHEMA_TEST_DICTIONARY_1 = {
    'Libra Test Schema 1' : {
        'columns' : {
            'column_01' : {
                'data_type' : BigInteger()
            },
            'column_02' : {
                'data_type' : Boolean()
            },
            'column_03' : {
                'data_type' : Date()
            },
            'column_04' : {
                'data_type' : DateTime()
            },
            'column_05' : {
                'data_type' : Enum()
            },
            'column_06' : {
                'data_type' : Double()
            },
            'column_07' : {
                'data_type' : Float()
            },
            'column_08' : {
                'data_type' : Integer()
            },
            'column_09' : {
                'data_type' : Interval()
            },
            'column_10' : {
                'data_type' : LargeBinary()
            },
            'column_11' : {
                'data_type' : Numeric()
            },
            'column_12' : {
                'data_type' : PickleType()
            },
            'column_13' : {
                'data_type' : SmallInteger()
            },
            'column_14' : {
                'data_type' : String()
            },
            'column_15' : {
                'data_type' : Text()
            },
            'column_16' : {
                'data_type' : Time()
            },
            'column_17' : {
                'data_type' : Unicode()
            },
            'column_18' : {
                'data_type' : UnicodeText()
            },
            'column_19' : {
                'data_type' : Uuid()
            }
        },
        
        'models' : {
            'model_01' : {
                'columns' : [
                    'column_01',
                    'column_02',
                    'column_03',
                    'column_04',
                    'column_05',
                    'column_06',
                    'column_07',
                    'column_08',
                    'column_09',
                    'column_10',
                    'column_11',
                    'column_12',
                    'column_13',
                    'column_14',
                    'column_15',
                    'column_16',
                    'column_17',
                    'column_18',
                    'column_19'
                ],
                'pk' : {'columns' : ['column_08']},
                'uc' : {'columns' : ['column_03', 'column_16']},
                'fk' : {}
            }

        }
    },
    'Libra Test Schema 2' : {
        'columns' : {
            'column_01' : {
                'data_type' : Integer()
            },
            'column_02' : {
                'data_type' : String(6)
            },
            'column_03' : {
                'data_type' : String(8)
            },
            'column_04' : {
                'data_type' : Float(53)
            },
            'column_05' : {
                'data_type' : DateTime(),
                'nullable' : False,
                'default' : datetime.datetime.now()
            }
        },
        'models' : {
            'model_01' : {
                'columns' : [
                    'column_01',
                    'column_02',
                    'column_05'
                ],
                'pk' : {'name' : 'model_01_pk', 'columns' : ['column_01']},
                'uc' : {'name' : 'model_01_uc', 'columns' : ['column_01', 'column_02']}
            },
            'model_02' : {
                'columns' : [
                    'column_01',
                    'column_03',
                    'column_04',
                    'column_05'
                ],
                'pk' : {'name' : 'model_02_pk', 'columns' : ['column_01']},
                'uc' : {'name' : 'model_02_uc', 'columns' : ['column_01', 'column_03', 'column_04']}
            }
        }
    }
}

# ==============================================================================
