# _Libra_ - Your Database Manager's Favorite Database Manager

> Brady Spears, Los Alamos National Laboratory

![libra_logo](/docs/pics/Libra_Logo.png)

## Table of Contents
- [About _Libra_](#about-libra)
- [Why use _Libra_?](#why-use-libra)
- [Installation](#installation)
- [Examples](#examples)
- [References](#references)

## About _Libra_
`Libra` is an open-source relational database schema serialization package built 
on [`SQLAlchemy`](https://www.sqlalchemy.org/). `Libra` allows you to easily 
serialize abstract object-relation-mapped (ORM) table instances into a number 
of different schema definition formats. These schema definition formats can be
subsequently de-serialized back into abstract ORM instances. Serialized schema 
definitions are stored in plain text, so they are easily transported, exported,  
and readable. `Libra` was adapted from the idea of the "schema-schema" (Carr et 
al., 2007), which aimed at encoding descriptiosn of relational database schemas 
into a set of self-describing database tables, allowing legacy software to 
dynamically construct SQL "CREATE TABLE ..." scripts on-the-fly.

## Why use _Libra_?
`Libra` serves as a developer's tool for data engineers interacting with 
multiple, highly varied, relational database schemas, which is often the case 
when working with multiple institutions, different phenomenologies, or even 
different database backends. Leveraging `SQLAlchemy's` backend-agnostic type 
system, `Libra` allows for not only the documentation of relational database 
schemas, but also the dynamic import of those abstract ORM objects into the 
object-oriented programming Python environment. Objects are then easily ported 
to more complex softwares, like custom APIs, data ingestion/analysis/curation 
packages, and more.

## Installation
### Required Dependencies
- [`SQLAlchemy`](https://www.sqlalchemy.org/) >= 2.0

### Optional Dependencies
- [`Pandas`](https://pandas.pydata.org/)
- [`Rich`](https://github.com/Textualize/rich)

(Used exclusively in mix-in classes)

### Getting Started
1. If you have not installed `Libra` previously, you can install it with `pip` 
via the command `pip install libra`. If you have an earlier version and would 
like to upgrade to the latest version, use `pip install libra --upgrade`.
2. Confirm that `Libra` has been installed/updated successfully by examining 
the last few lines of the text displayed in the console.

## Examples

### Schema import via YAML and basic querying
`Libra` has load and dump support for encoded schemas in a variety of formats, 
including [YAML](https://yaml.org/) - which boils `Schema` import down to a 
one-liner:

```python
from libra import Schema

kbcore = Schema('NNSA KB Core').load('kbcore.yaml')
```

Abstract ORM instances (SQL Tables without a name, A.K.A 'Models') are added 
as attributes of the `Schema` object, and through inheritance, can be cast to 
an existing or new SQL Table and interacted with via `SQLAlchemy's` native API:

```python
from libra import Schema
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

css = Schema('CSS 3.0').load('css30.yaml')

# Center for Seismic Studies 3.0 (CSS 3.0) 'Site'-style table
class Site(css.site):
    __tablename__ = 'my_custom_site'

# Create connection to SQL database (SQLite in-memory)
engine = create_engine('sqlite:///:memory:')
session = Session(engine)

# Query the Site table (filter on station code equal to 'ANMO')
query_results = session.query(Site).filter(Site.sta == 'ANMO').all()
```

### Schema import via Database and export to YAML
`Libra` provides native support for the serialization of schema definitions 
into a set of relational database tables - a "schema of schemas," which has been 
slightly modified from older works (Carr et al., 2007). Users can import in 
similar fashion to above:

```python
from libra import Schema
from libra.util import DatabaseSettings
from sqlalchemy import create_engine

# Create connection to SQL database
engine = create_engine('sqlite:///:memory:')

# Parameter class injectable to Libra's Schema object
settings = DatabaseSettings(engine)

# Loading in a Custom Schema
custom_schema = Schema('My Custom Schema 0.1').load(settings)

# Dump the Custom Schema into a YAML file
custom_schema.dump('customschema.yaml')
```

### Injectable Mixin packages!
Models can be be injected with custom mix-in classes to extend model OOP 
functionality. `Libra` provides three such classes natively, which extend the 
support of models to handle flat-file (delimited) file import and export, the 
conversion to and from `Pandas` DataFrame objects, and the generation of 
automated quality control reports to assess data integrity before database 
ingestion.
```python
from libra import Schema
from libra.ext import (
    FlatFileMixin,
    PandasMixin,
    QCMixin
)

kbcore = Schema('NNSA KB Core', mixins = (FlatFileMixin, PandasMixin, QCMixin,)).load('kbcore.yaml')

class Affiliation(kbcore.affiliation):
    __tablename__ = 'my_affiliation_table'

# Affiliation is just an object -> assign variables to create rows in a database
# NOTE: Positional or Keyword instantiation are both supported!
entries = [
    Affiliation(net = 'USGS', sta = 'ANMO', time = 144547200.),
    Affiliation('TX', 'BRDY', 1487116800., None, None),
    Affiliation(net = 'ISC', sta = 'WALT')
]
# NOTE: 'None' values default to a column's assigned 'default' value, if it exists

# Write 'entries' to a flat file
with open('flatfile.txt', 'w') as f:
    for entry in entries:
        f.write(entry.to_string())

# Convert 'entries' to a DataFrame object
df = Affiliation.to_frame(entries)

# Generate a quality control and summary report of data contained in 'entries'
report = Affiliation.qc(entries, kbcore, summarize = True)
report.render_to_file('my_affiliation_qc.out')
```

## References
> Carr, D. B., Lewis, J. E., Ballard, S., Martinez, E. M., Hampton, J. W., 
Merchant, B. J., Stead, R. J., Crown, M., Roman-Nieves, J., & Dwyer, J. J. 
(2007). *Advances in the Integration of Large Data Sets for Seismic Monitoring 
of Nuclear Explosions.* Paper presnted at the 29th Monitoring Research Review: 
Ground-Based Nuclear Explosion Monitoring Technologies, Denver, CO.