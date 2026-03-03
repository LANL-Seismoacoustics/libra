"""
Brady Spears, Los Alamos National Laboratory
10/7/2025

Contains various `Settings` objects which encode complex runtime configuration
variables for loading/dumping serialized schema definitions. 
"""

# ==============================================================================

from typing import TypeVar

from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase

from dataclasses import dataclass

# ==============================================================================

Schema = TypeVar('Schema')

# ==============================================================================

@dataclass
class DatabaseSettings:
    """
    Database Settings object to specify various database-specific parameters, 
    like table names and database connections.

    Attributes
    ----------
    engine : Engine
        SQLAlchemy Engine object, used to establish a connection to a database.
    schemadescript : str, Optional
        Tablename of the 'schemadescript' table. Default is 'schemadescript'
    modeldescript : str, Optional
        Tablename of the 'modeldescript' table. Default is 'modeldescript'
    columndescript : str, Optional
        Tablename of the 'columndescript' table. Default is 'columndescript'
    columnassoc : str, Optional
        Tablename of the 'columnassoc' table. Default is 'columnassoc'
    columninfo : str, Optional
        Tablename of the 'columninfo' table. Default is 'columninfo'
    glossary : str, Optional
        Tablename of the 'glossary' table. Default is 'glossary'
    create_tables : bool, Optional
        Flag to optionally create teables if they don't already exist. Default 
        is False.
    overwrite : bool, Optional
        Flag to overwrite schema definitions if they already exist. Default is 
        False.
    """

    engine             : Engine
    schemadescript     : str = 'schemadescript'
    modeldescript      : str = 'modeldescript'
    columndescript     : str = 'columndescript'
    columnassoc        : str = 'columnassoc'
    constraintdescript : str = 'constraintdescript'
    columninfo         : str = 'columninfo'
    glossary           : str = 'glossary'

    author             : str | None = None
    create_tables      : str = False
    overwrite          : str = False

    def _generate(self, schema : Schema) -> tuple[type[DeclarativeBase]]:

        class Schemadescript(schema.schemadescript):
            __tablename__ = self.schemadescript
        
        class Modeldescript(schema.modeldescript):
            __tablename__ = self.modeldescript
        
        class Columndescript(schema.columndescript):
            __tablename__ = self.columndescript
        
        class Columnassoc(schema.columnassoc):
            __tablename__ = self.columnassoc
        
        class Columninfo(schema.columninfo):
            __tablename__ = self.columninfo
        
        class Constraintdescript(schema.constraintdescript):
            __tablename__ = self.constraintdescript
        
        return (
            Schemadescript,
            Modeldescript,
            Columnassoc,
            Columndescript,
            Columninfo,
            Constraintdescript
        )

@dataclass
class SchemaSchemaSettings:
    """
    Database Settings object to support parameters pertinent to the legacy 
    schema-schema relational database schema encoding format.

    Attributes
    ----------
    engine : Engine
        QLAlchemy Engine object, used to establish a connection to a database.
        NOTE: The schema-schema only supports Oracle backends.
    tabdescript : str, Optional
        Tablename of the 'tabdescript' table. Default is 'doc.tabdescript'
    coldescript : str, Optional
        Tablename of the 'coldescript' table. Default is 'doc.coldescript'
    colassoc : str, Optional
        Tablename of the 'colassoc' table. Default is 'doc.coldescript'
    complexjoin : str, Optional
        Tablename of the 'complexjoin' table. Default is 'doc.complexjoin'
    glossary : str, Optional
        Tablename of the 'glossary' table. Default is 'doc.glossary'
    create_tables : bool, Optional
        Create schema-schema tables on dump. Default is False
    """

    engine      : Engine
    tabdescript : str = 'doc.tabdescript'
    coldescript : str = 'doc.coldescript'
    colassoc    : str = 'doc.colassoc'
    complexjoin : str = 'doc.complexjoin'
    glossary    : str = 'doc.glossary'

    create_tables : bool = False

    def _generate(self, schema : Schema) -> tuple[type[DeclarativeBase]]:
        
        class Tabdescript(schema.tabdescript):
            __tablename__ = self.tabdescript

        class Coldescript(schema.coldescript):
            __tablename__ = self.coldescript

        class Colassoc(schema.colassoc):
            __tablename__ = self.colassoc
        
        class Complexjoin(schema.complexjoin):
            __tablename__ = self.complexjoin
        
        class Glossary(schema.glossary):
            __tablename__ = self.glossary
        
        return (
            Tabdescript,
            Coldescript,
            Colassoc,
            Complexjoin,
            Glossary
        )
