# _Libra_ - Your Database Manager's Favorite Database Manager

> Brady Spears, Los Alamos National Laboratory

![Libra_Logo](/docs/pics/Libra_Logo.png)

## Table of Contents
- [About _Libra_](#About-Libra)
- [Installation](#Installation)
- [Examples](#Examples)
- [References](#References)

## About _Libra_
`Libra` is a database management package built on [`SQLAlchemy`](https://www.sqlalchemy.org/) 
that allows you to easily and dynamically connect your relational database 
structures to the object-oriented Python development environment. `Libra` was 
conceptualized from the idea of the "schema-schema" (Carr et al., 2007), which 
aimed at encoding descriptions of elements of a relational database schema into 
database tables, allowing legacy software to dynamically construct SQL tables, 
columns, and constraints programmatically on-the-fly. This concept has proved 
particularly useful in data management practices that require data structures 
emanating from different institutions, different formats, or even custom 
augmentations of existing schemas.

`Libra` encodes a subset of information needed to create abstract `SQLAlchemy` 
object-relation-mapped (ORM) instances, hereafter referred to as "models," into 
a variety of plain-text definition formats, including regular Python 
dictionaries,YAML files, and a refined version of the "schema-schema." Using 
`Libra`'s **Schema** object, building models boils down to a one-liner, with 
optional support to customize the structure and behavior of your models both in 
the object-oriented programming space and the relational database space.

Support is also provided for reading/writing schemas to/from custom plain-text 
formats and for augmenting model behavior through "mix-in" classes, which 
introduce custom methods to all models deriving from a schema.

## Installation
Requires:
- [`SQLAlchemy`](https://www.sqlalchemy.org/) >= 2.0
- [`Pydantic`](https://docs.pydantic.dev/latest/)
- [`Pydantic-Settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

## Examples
Loading all "models" belonging to the **NNSA KB Core** schema and assiging 
tablenames to them to then query using standard `SQLAlchemy` query syntax:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from libra import Schema
from libra import DatabaseSettings

settings = DatabaseSettings(connection_str = 'sqlite:///kbcore_schema.db')

kbcore = Schema('NNSA KB Core').load(settings)
kbcore.assign_tablenames(prefix = 'new_')

session = Session(create_engine(settings.connection_str))

site_table_query = session.query(kbcore.site).all()
```
Executing this code will first construct all models belonging to the **NNSA KB Core** schema, a common schema used in the seismological sciences. Table names are assigned in the next step, structuring all models belonging to the **NNSA KB Core** schema with a prefix of "new_" (i.e. Models now become tables and are referred to by their tablenames, which resemble "new_site", "new_origin", etc.). The final few lines are concerned with setting up an `SQLAlchemy` **Session** and querying all rows of the "new_site" table in the relational database. 

## References
> Carr, D. B., Lewis, J. E., Ballard, S., Martinez, E. M., Hampton, J. W., Merchant, B. J., Stead, R. J., Crown, M., Roman-Nieves, J., & Dwyer, J. J. (2007). *Advances in the Integration of Large Data Sets for Seismic Monitoring of Nuclear Explosions.* Paper presnted at the 29th Monitoring Research Review: Ground-Based Nuclear Explosion Monitoring Technologies, Denver, CO.