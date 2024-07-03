# _Client_ - Easy database connection support

> Brady Spears, Los Alamos National Laboratory

## About _Libra.Client_
The _Client_ class was added to `Libra` to provide an easier method of instantiating `SQLAlchemy` _Session_ objects. The _Session_ object establishes and contains all interactions with a database connection (Read more here: [Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)). _Libra.Client_ acts as a wrapper around the _Session_ object, and simply extends the support of database connection instantiation. Support for connection methods include the typical methods used by the _Session_ object in `SQLAlchemy`, as well as some new methods like configuration file parsing and explicit declaration of connection string variables. This document is intended to demonstrate all supported methods of instantiating the _Libra.Client_ object.

## Examples

### Connect using a correctly-formatted connection string
```python
from libra import Client

connection_str = 'postgres://scott:tiger@myserver.edu:22/mydb'

client = Client(connection = connection_str)
session = client()
```

### Connect using explicit declaration of variables
The user can explicitly declare parameters used to format a database connection string. These generally include the 'backend', 'username', 'password', 'server', 'port', and 'instance' variables contained within the connection string, which is formatted as: '{backend}://{username}:{password}@{server}:{port}/{instance}'. The user can explicitly pass each of these keyword variables to the _Client_ object. The only required input variable is the 'backend' parameter. If 'backend' is 'sqlite', the user will be connected to a locally-hosted SQLite database instance. Otherwise, the user has the option to provide their username and password, and will be prompted for manual input if either is not provided as a keyword in the _Client.\__init\__()_ method.

```python
from libra import Client

session_sqlite = Client(backend = 'sqlite')()

session_postgres = Client(
    backend = 'postgres',
    username = 'scott',
    password = 'tiger',
    server   = 'myserver.edu',
    port     = 22,
    instance = 'mydb' 
)()
```

### Connect using a configuration file
Using the `configparser` module, a user can optionally pass the path to a configuration file, which contains specific declarations of database connection variables. The _Client_ class will, by default, attempt to read parameters specified under the 'DATABASE' section of the configuration file, though this can be customized by passing a 'section' keyword into the initialization of the _Client_ object. 

We've made the use of the _Client_ object easier by providing support for the reading of a configuration file without the need to explicitly call the configuration file. By calling the _Client_ object with no input parameters at all, the _Client_ class will, by default, search the current directory for any _'cnf'_ files. If a single file is found, then an `SQLAlchemy` _Session_ will be instantiated based on the parameters contained in that configuration file. If multiple files are found, then the user is prompted via _input()_ to select the desired configuration file. If the configuration file is not stored in the current directory, the user can pass the 'search_dir' and 'extension' keyword(s) to the _Client.\__init\__()_ method to search a specific directory for a configuration file with the appropriate file extension.

#### path/to/db_connect1.cnf
```sh
[DATABASE]
backend  = 'postgres'
username = 'scott'
password = 'tiger'
server   = 'myserver.edu'
port     = 22
instance = 'mydb'
```

#### path/to/db_connect2.env
```sh
[CONNECT]
backend  = 'oracle'
username = 'scott'
server   = 'anotherserver.org'
port     = 22
instance = 'myotherdb'
```
---
```python
from libra import Client

session = Client(config_file = 'path/to/db_connect1.cnf')()
session = Client(search_dir = 'path/to', extension = 'env', section = 'CONNECT')
```

### Connect with a custom connection interface
`Libra` provides the support for custom database client connection strategies through an abstract base class with an abstract _connect()_ class method. In the case that the user stores database connection information in a format not consistent with any of the built-in methods, a custom connection protocol can be written and called by the user to initialize a _Libra.Client_ object, and subsequently, an _SQLAlchemy.orm.Session_ object. The following example uses a dictionary to store a user's username and password, and the connection strategy uses that dictionary to establish a connection to an organization's database. The strategy can then be passed to the _Client.\__init\__()_ method.

```python
from sqlalchemy.orm.session import Session

from libra import Client
from libra import Client_Connect_Strategy

profile = {'username' : 'scott', 'password' : 'tiger'}

class UserProfile_Connect_Strategy(Client_Connect_Strategy):
    def connect(user_profile : Dict[str, str]) -> Session:
        """Uses the dictionary definition of a user profile to connect to a database"""

        username = user_profile.get('username', '')
        password = user_profile.get('password', '')

        connection_str = f'oracle://{username}:{password}@orgserver.org:22/orgdb'

        return Session(connection_str)

session = Client(strategy = UserProfile_Connect_Strategy, user_profile = profile)()
```
