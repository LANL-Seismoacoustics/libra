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
database tables, thus allowing software to dynamically construct SQL tables, 
columns, and constraints programmatically on-the-fly. The concept of dynamically 
loading relational database structures in the object-oriented environment has 
proved particularly useful in dealing with schemas from mulitple institutions, 
varying schema formats, and even in augmenting the functionality or structure 
of object-relation mapped (ORM) instances.

`Libra` encodes a subset of information needed to create abstract `SQLAlchemy` 
object-relation-mapped (ORM) instances, hereafter referred to as "models," into 
a variety of plain-text definition formats, including regular Python 
dictionaries, YAML files, and a refined version of the "schema-schema" - a 
set of relational database tables that are used to create other tables. Using 
`Libra`'s **Schema** object, building models boils down to a one-liner, with 
optional support to customize the structure and behavior of your models both in 
the object-oriented programming space and the relational database space.

Support is also provided for reading/writing schemas to/from custom plain-text 
formats and for augmenting model behavior through "mix-in" classes, which 
introduce custom methods to all models belonging to a schema.

## Installation
### Dependencies
- [`SQLAlchemy`](https://www.sqlalchemy.org/) >= 2.0
- [`Pydantic`](https://docs.pydantic.dev/latest/)
- [`Pydantic-Settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

### Getting Started
1. If you have not installed `Libra` previously, you can install it with `pip` 
via the the command `pip install libra`. If you have an earlier version and 
would like to upgrade to the latest version of `Libra`, use `pip install 
libra --upgrade`.
2. Confirm that `Libra` has installed/updated successfully by examining the 
last few lines of the text displayed in the console.

### Using *Libra*
1. Download the contents of the [docs/examples](/docs/examples) directory to a 
location of your choice.
2. Launch the `libra_intro.ipynb` Jupyter notebook for an introduction to the 
basics of `Libra`.
3. Continue exploration of the [docs/examples](/docs/examples) directory to 
highlight additional features and customizations provided by `Libra`.

## Example
Loading all "models" belonging to the **NNSA KB Core** schema, and mapping the
"Site" model to a table within an `SQLite` database.
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from libra import Schema
from libra import DatabaseSettings

settings = DatabaseSettings(connection_str = 'sqlite:///kbcore_schema.db')

kbcore = Schema('NNSA KB Core').load(settings)

class Site(kbcore.site):
    __tablename__ = 'new_site'

session = Session(create_engine(settings.connection_str))

site_table_query = session.query(Site).all()
```
Executing this code will first construct all models belonging to the 
**NNSA KB Core** schema, a common set of tables used in the seismological 
sciences. A new class is created that inherits from the "Site" model and is  
mapped back to the relational database using the `__tablename__` attribute.
With a `Session` object, `SQLAlchemy` formulates and passes Data Definition 
Language (DDL) onto the database backend, allowing for standard SQL 
functionality, including the ability to query all rows of the "new_site" table 
as shown above.

## References
> Carr, D. B., Lewis, J. E., Ballard, S., Martinez, E. M., Hampton, J. W., Merchant, B. J., Stead, R. J., Crown, M., Roman-Nieves, J., & Dwyer, J. J. (2007). *Advances in the Integration of Large Data Sets for Seismic Monitoring of Nuclear Explosions.* Paper presnted at the 29th Monitoring Research Review: Ground-Based Nuclear Explosion Monitoring Technologies, Denver, CO.