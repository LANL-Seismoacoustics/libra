# Using the `libra.Schema` object
> Brady Spears, Los Alamos National Laboratory

## Table of Contents
- [Instantiation](#instantiation)
- [Adding Models](#adding-models)
- [Loading Schemas](#loading-schemas)
- [Writing Schemas](#writing-schemas)
- [Customization](#customization)

## Instantiation
Only a name is needed to instantiate a `Schema` object:
```python
from libra import Schema

schema = Schema('My Schema')
```

## Adding Models
A `Schema` object functions to hold abstract object-relation-mapped (ORM) 
instances. These abstract ORM instances represent object-oriented analogs to 
tables that would exist in a relational SQL database. By assigning a tablename 
to the abstract ORM instance, you can then use SQLAlchemy's standard 
functionality to interact with the table and the data contained within it. 
`Libra` models are powered by `SQLAlchemy`, and relies on its components for 
datatyping. You can declare a model in `Libra` without the heavy boilerplate 
required when using `SQLAlchemy` alone:
```python
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime, Integer, String

from libra import Schema

networking_schema = Schema('Social Networking App Schema')

@networking_schema.add_model
class UsersModel:
    userid = Column(Integer)
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    email = Column(String(128), nullable = False)
    join_date = Column(DateTime(), nullable = False, default = datetime.now())

    pk = ['userid']
    uc = ['first_name', 'last_name', 'email']
```

To access the data contained in your database, under a table ~looking like~ 
the above **Users** class, re-cast the class with a table name defined:

```python
class Users(social_network.UserModel):
    __tablename__ = 'users'
```

Use traditional `SQLAlchemy` declarative ORM methods to query and manipulate 
the data contained in your database.

```python
from sqlalchemy import create_engine
from sqlalchemy import Session

engine = 'oracle://scott:tiger@127.0.0.1:1521/mydb'
session = Session(bind = engine)

session.query(Users).filter(and_(Users.first_name == 'Scott', Users.last_name == 'Tiger'))
```

## Loading Schemas
Coming Soon!

## Writing Schemas
Coming Soon!

## Customization
`Libra` adds functionality and useful features to get rid of boilerplate code 
inherent to the `SQLAlchemy` declarative mapping style, but retains the 
flexibility to customize functionality and operability of ORM instances. `Libra`
makes use of a custom metaclass - **LibraMetaClass** - which adds OOP-specific 
functionality to children of `SQLAlchemy's` **DeclarativeBase** class. To 
overwrite default inheritance of **LibraMetaClass**, you can simply:

```python
from datetime import datetime

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import DeclarativeMeta, declarative_base

from libra import process_model

class MyCustomMetaClass(DeclarativeMeta):
    ...

Base = declarative_base(metaclass = MyCustomMetaClass)

@process_model(Base)
class UsersModel:
    userid = mapped_column(Integer, primary_key = True)
    first_name : Mapped[str]
    last_name : Mapped[str]
    email : Mapped[str]
    join_date = mapped_column(DateTime, insert_default = datetime.now())
```

Defining this custom metaclass in the instantiation of a **Schema** object 
extends the metaclass's functionality to all models added to that schema.

```python
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime, Integer, String

from libra import Schema

class MyCustomMetaClass(DeclarativeMeta):
    ...

networking_schema = Schema('Social Networking App Schema', base = MyCustomMetaClass)

@networking_schema.add_model
class UsersModel:
    userid = mapped_column(Integer, primary_key = True)
    first_name : Mapped[str]
    last_name : Mapped[str]
    email : Mapped[str]
    join_date = mapped_column(DateTime, insert_default = datetime.now())
```

`Libra` extends the functionality of ORM models with optional "Mixin" classes. 
Mixin classes are intended to augment a model by adding OOP specialized or 
custom functionality. To add mixin package(s):

```python
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime, Integer, String

from libra import process_model

class MyFirstMixin: ...
class MySecondMixin: ...

@process_model(mixins = (MyFirstMixin, MySecondMixin,))
class UsersModel:
    userid = Column(Integer)
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    email = Column(String(128), nullable = False)
    join_date = Column(DateTime(), nullable = False, default = datetime.now())

    pk = ['userid']
    uc = ['first_name', 'last_name', 'email']
```

To add these mixins to all models belonging to a schema:

```python
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime, Integer, String

from libra import Schema

class MyFirstMixin: ...
class MySecondMixin: ...

@networking_schema.add_model(mixins = (MyFirstMixin, MySecondMixin,))
class UsersModel:
    userid = Column(Integer)
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    email = Column(String(128), nullable = False)
    join_date = Column(DateTime(), nullable = False, default = datetime.now())

    pk = ['userid']
    uc = ['first_name', 'last_name', 'email']
```
