from sqlalchemy import Column
from sqlalchemy import String, Integer, JSON

from .. import Schema

# ==============================================================================

DOC = Schema('doc')

@DOC.add_model
class tabdescript:
    table_name  = Column(String(128))
    description = Column(String(1024))
    schema_name = Column(String(128))
    author      = Column(String(128))

    pk = ['table_name', 'schema_name']

@DOC.add_model
class colassoc:
    table_name      = Column(String(128))
    column_name     = Column(String(128))
    column_type     = Column(String(128))
    column_position = Column(Integer())
    schema_name     = Column(String(128))
    author          = Column(String(128))
    kwargs          = Column(JSON())

    pk = ['table_name', 'column_name', 'schema_name']

@DOC.add_model
class coldescript:
    column_name = Column(String(128))
    data_type   = Column(String(1024))
    description = Column(String(1024))
    schema_name = Column(String(128))
    author      = Column(String(128))
    kwargs      = Column(JSON())

    pk = ['column_name', 'data_type', 'schema_name']

# ==============================================================================
