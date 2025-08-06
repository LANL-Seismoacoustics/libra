"""
Brady Spears
7/17/25

Contains the various children of `SchemaSettings`. Each child of 
`SchemaSettings` maps to one of the three built-in load/write strategies 
(`DictionaryTransferStrategy`, `YAMLFileTransferStrategy`, & 
`DatabaseTransferStrategy`). Each transfer strategy requires different input 
variables, and those differences are communicated via the appropriate 
`SchemaSettings` polymorphism. Inheriting from Pydantic's `BaseSettings` 
object, additional functionality is also provided for reading these settings in 
from environment files rather than defining them in-line.
"""

# ==============================================================================

from __future__ import annotations
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# ==============================================================================

class _SchemaSettings(BaseSettings):
    """Parent class with common settings variables across all children"""

    model_config = SettingsConfigDict(env_prefix = 'libra')


class DictionarySettings(_SchemaSettings):
    """Settings variables specific to DictionaryTransferStrategy"""

    dictionary : dict[str, dict | str] | None = None


class YAMLFileSettings(_SchemaSettings):
    """Settings variables specific to YAMLFileTransferStrategy"""

    file : str | os.PathLike | None = None


class DatabaseSettings(_SchemaSettings):
    """Settings variables specific to DatabaseTransferStrategy"""

    # Database connection string (e.g. 'oracle://scott:tiger@my.url.com:1500/mydb')
    connection_str : str | None = None

    # Table owner or "schema" ('othernamespace.tablename')
    namespace : str | None = None

    # Tablenames for Libra's self-describing schema
    schemadescript     : str = 'schemadescript'
    modeldescript      : str = 'modeldescript'
    columnassoc        : str = 'columnassoc'
    columndescript     : str = 'columndescript'
    constraintdescript : str = 'constraintdescript'

    # Optional Author Field
    author : str | None = None
