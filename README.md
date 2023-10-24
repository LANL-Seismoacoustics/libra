# `Libra` - A tool for dynamic schema support in Python

> Brady Spears, Los Alamos National Laboratory

## Table of Contents

- [About Libra](#about-libra)
- [Features](#features)
- [Getting Started](#getting-started)
- [Examples](#examples)

## About Libra
`Libra` is a Python packaged designed to dynamically create SQLAlchemy Object-
Relation Mapped (ORM) objects from pre-defined schema definitions, also known as "schema-schema". `Libra` allows the user to forego the time-consuming and 
laborious task of hard-coding SQLAlchemy ORM classes with Column and Table 
objects by passing schema information through one of the supported file formats. 
From these user-provided schema definitions, SQLAlchemy ORM classes are built 
on-the-fly and can be tied to more schema- and table-specific code bases. 
Additional to read and write support for user-defined schemas, `Libra` also 
provides functionality for the quality control (QC) of data contained in 
SQLAlchemy tables.

## Features
* Reading/writing of custom schema to/from databases and a variety of file formats
    - Supported formats include TOML, JSON, CSV, and Database tables
* Dynamic creation of SQLAlchemy ORM classes from user-built schema definitions
* Method support for the reading and writing of flat files
* Functional support for the dynamic Quality Control (QC) of data in schema tables

## Getting started
### Dependencies
- [SQLAlchemy >= 2.0.0](https://www.sqlalchemy.org/)

### Installation
```sh
# TODO: Add install instructions
```

## Examples

### Loading in all CSS 3.0 -styled ORM classes from a TOML file:
```python
from libra.schema import Schema

css = Schema('CSS3.0').load(file = 'library/toml/css3.toml')
```

### Loading in NNSA KB Core -styled *site*, *sitechan*, & *instrument* ORM classes from `Coldescript` & `Colassoc` "schema-schema" database tables:
```python
import sqlalchemy as sa
from sqlalchemy.orm import Session

engine = create_engine("oracle://scott:tiger@127.0.0.1:1521/sidname")
session = Session(engine)

kbcore = Schema('NNSA KB Core').load(session = session, coldescript = 'coldescript',
                                     colassoc = 'colassoc', 
                                     tableforms = ['site', 'sitechan', 'instrument'])
```