# _Libra_ - Dynamic Schema support in Python

> Brady Spears, Los Alamos National Laboratory

![Libra Logo](/docs/pics/Libra_Logo.png)

## Table of Contents

-   [About _Libra_](#About-libra)
-   [Features](#Features)
-   [Getting Started](#Getting-started)

## About _Libra_
`Libra` is a database management package built on [`SQLAlchemy`](https://www.sqlalchemy.org/) to easily and dynamically connect your relational SQL database to the object-oriented Python development environment. Developed by Brady Spears at Los Alamos National Laboratory (LANL), `Libra` absorbs much of the boilerplate code and developer overhead in creating and defining `SQLAlchemy` object-relation mapped (ORM) instances. `Libra` is maintained and developed under the LANL Seismoacoustic Team's Python Geophysical Suite (PyGS). 

## Features
`Libra` extends `SQLAlchemy's` ORM to support:
- An extension of the **sqlalchemy.orm.Session** class to allow more connection methods, including instantiation of a database connection via environment variables or config files.
- The loading/writing of database tables and columns from user-defined schema to/from a variety of plain-text, built-in formats, as well as extendable support for any other desired format.
- Dynamic SQL datatype handling, where dialect-specific SQL datatypes can be effectively mapped for the same schema on different database backends.
- A plugin architecture connecting ORM models belonging to your schema to custom-built functionality. Built-in plugins included with the `Libra` package include:
    - Flatfile read/write support
    - Conversion of ORM instances to [`Pandas`](https://pandas.pydata.org/) **DataFrame** objects
    - Column- and table-specific data quality control methods
- Flexibility to derive ORM instance methods from the provided metaclass or a custom metaclass implementation.
- Flexibility to design, define, and digest your schema in a way that makes sense for your needs.

## Getting Started

