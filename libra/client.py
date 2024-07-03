import os
import glob
import getpass
from abc import ABC, abstractmethod
from typing import TypedDict, Unpack
from typing import Optional, Union

from sqlalchemy.orm import Session
import pdb

# ==============================================================================

class Client_Connect_Strategy(ABC):
    """
    Abstract Base class with a method to establish a database connection from a
    variety of connection options.
    """

    @abstractmethod
    def connect(self) -> Session:
        pass

# ==============================================================================

class Session_Strategy(Client_Connect_Strategy):
    """Pass an SQLAlchemy database session through"""

    def connect(session : Session) -> Session:
        """
        Connect to a database by simply passing the SQLAlchemy.orm.Session 
        object through the Libra.Client object.

        Parameter
        ---------
        session : SQLAlchemy.orm.Session
            Input database connection object
        
        Returns
        -------
        session : SQLAlchemy.orm.Session
            Database connection object
        """
        
        return session

class Connection_String_Strategy(Client_Connect_Strategy):
    """Create an SQLAlchemy session object from a connection string"""

    def connect(connection : str) -> Session:
        """
        Connect to a database by passing a correctly-formatted connection string
        through the Libra.Client object.

        Parameter
        ---------
        connection : str
            Database connection string

        Returns
        -------
        SQLAlchemy.orm.Session
            Database connection object unaltered
        """
        
        return Session(connection)

class Config_File_Strategy(Client_Connect_Strategy):
    """Create an SQLAlchemy session object using the 'DATABASE' section of a config file"""

    def connect(config_file : Union[str, os.PathLike], section : Optional[str] = 'DATABASE') -> Session:
        """
        Connect to a database through a configuration file, which contains 
        parameters needed to format a connection string.

        Parameter
        ---------
        config_file : Union[str, os.PathLike]
            Path to the desired configuration file
        section : Optional[str] = 'DATABASE'
            Section that contains database connection parameters. Default is 
            'DATABASE'.
        
        Returns
        -------
        SQLAlchemy.orm.Session
            Database connection object
        """
        
        #TODO: Consider taking all variables in 'DATABASE' section and calling _direct_inputs recursively, so user can provide optionally provide 'connection' instead of 'backend', 'username', etc.
        import configparser

        config = configparser.ConfigParser()
        config.read(config_file)

        db_params = {key : config[section].get(key, None) for key in config[section].keys()}

        return Explicit_Strategy.connect(**db_params)
 
class Explicit_Strategy(Client_Connect_Strategy):
    """Create an SQLAlchemy session object using explicit declaration of connection string variables"""

    def connect(backend : str, username : Optional[str] = None, password : Optional[str] = None, server : Optional[str] = None, port : Optional[str] = None, instance : Optional[str] = None) -> Session:
        """
        Connect to a database using explicit declaration of connection string
        parameters. Method will correctly structure connection string of the
        form: {backend}://{username}:{password}@{server}:{port}/{instance}


        Parameters
        ----------
        backend : str
            Database server backend. Examples include 'postgres', 'oracle', 
            'myssql', 'sqlite', etc.
        username : Optional[str] = None
            Database server username. If not provided, and backend is not 
            'sqlite', the user is prompted for manual input.
        password : Optional[str] = None
            Database server password. If not provided and backend is not 
            'sqlite', the user is prompted for manual input. 
        server   : Optional[str] = None
            Database server address
        port     : Optioanl[Union[str, int]] = None
            Database connection port
        instance : Optional[str] = ''
            Database instance

        Returns
        -------
        SQLAlchemy.orm.Session
            Database connection object
        """

        userpass, serverport = '', ''

        if not backend == 'sqlite':
            if not username:
                username = str(input('Please enter username : '))
            if not password:
                password = str(getpass.getpass('Please enter password : '))
            userpass = f'{username}:{password}'
        
        if server and port:
            serverport = f'@{server}:{port}'
        
        if server and not port:
            serverport = f'@{server}'
        
        connection_str = f'{backend}://{userpass}{serverport}/{instance}'

        return Connection_String_Strategy.connect(connection_str)
   
class Search_Config_Strategy(Client_Connect_Strategy):
    """Search for a configuration file"""

    def _search_for_config(search_dir : Union[str, os.PathLike], extension : str) -> os.PathLike:
        """
        Returns the path to a configuration file found in specified dir

        Parameters
        ----------
        search_dir : Union[str, os.PathLike]
            Directory to search for files.
        extension : str
            File extension to search for.
        
        Returns
        -------
        os.PathLike
            Path to a selected configuration file within search_dir and having 
            a matching extension.
        
        Raises
        ------
        FileNotFoundError
            Raised if no file is found in the specified directory with the 
            specified extension.
        """

        config_files = glob.glob(os.path.join(search_dir, f'*.{extension}'))

        if len(config_files) == 1:
            return config_files[0]
        
        if len(config_files) > 1:
            print('Please select a configuration file : \n')
            print([f'{i} : {f}\n'for i, f in enumerate(config_files)])
            
            index = int(input(''))
            return config_files[index - 1]
        
        if not config_files:
            raise FileNotFoundError

    def connect(search_dir : Optional[Union[str, os.PathLike]] = '.', extension : Optional[str] = 'cnf', section : Optional[str] = 'DATABASE') -> Session:
        """
        Connect to a database automatically from just a path to a directory. 
        This connection strategy will search in the passed 'search_dir' to find
        all files of a specified extension. If one matching file is found, it 
        will be passed as the configuration file. If multiple are found, the 
        user is prompted to select the appropriate file. 

        Parameters
        ----------
        search_dir : Optional[Union[str, os.PathLike]] = '.'
            Directory to search for files. Default is the current directory.
        extension : Optional[str] = 'cnf'
            File extension to search for.
        section : Optional[str] = 'DATABASE'
            Configuration file heading for parsing of database parameters
        
        Returns
        -------
        SQLAlchemy.orm.Session
            Database connection object
        """

        config_file = Search_Config_Strategy._search_for_config(search_dir, extension)
        
        return Config_File_Strategy.connect(config_file, section)

# ==============================================================================

class ClientParams(TypedDict):
    """Acceptable keyword arguments to the Client class"""

    session     : Optional[Session]
    connection  : Optional[str]
    config_file : Optional[Union[str, os.PathLike]]
    section     : Optional[str]
    backend     : Optional[str]
    username    : Optional[str]
    password    : Optional[str]
    server      : Optional[str]
    port        : Optional[str]
    instance    : Optional[str]
    search_dir  : Optional[Union[str, os.PathLike]]
    extension   : Optional[str]

    strategy : Optional[Client_Connect_Strategy]

# ==============================================================================

class Client:
    def __init__(self, **kwargs : Unpack[ClientParams]) -> None:
        """
        Initialize an SQLAlchemy.orm.Session object, which is responsible for 
        establishing a connection to the database and executing database 
        transactions. Libra's Client class is intended to add support for the
        initialization of the Session object outside of explicitly passing the 
        connection string to SQLAlchemy. 

        Parameters
        ----------
        **kwargs : dict, optional
            See ClientParams Typed Dictionary for a description of all accepted
            keyword parameters for the Client.__init__() method.
        
        Returns
        -------
        SQLAlchemy.orm.Session object
            Object responsible for executing database transactions
        """

        connect_strategy = self._direct_params(self, **kwargs)

        if kwargs.get('strategy'):
            del kwargs['strategy']
        
        self.session = connect_strategy.connect(**kwargs)
    
    def __call__(self) -> Session:
        """
        Call method for the Client object returns an SQLAlchemy.orm.Session.

        Returns
        -------
        SQLAlchemy.orm.Session
            SQLAclhemy session object used to interact with a database.
        """

        if self.session:
            return self.session
        
        return None

    @staticmethod
    def _direct_params(self, **kwargs : Unpack[ClientParams]) -> Client_Connect_Strategy:
        """
        Maps keyword inputs of the __init__ method to Client connection 
        strategies. Certain keywords trigger certain connection strategies. 
        Keyword mappings are as follows:
            - 'strategy'    -> Client_Connect_Strategy subclass
            - 'session'     -> Session_Strategy
            - 'connection'  -> Connection_String_Strategy
            - 'config_file' -> Config_File_Strategy
            - 'backend'     -> Explicit Strategy
            - No input or other keywords -> Search_Config_Strategy

        Parameters
        ----------
        **kwargs : dict, optional
            See ClientParams Typed Dictionary for a description of all accepted
            keyword parameters for the Client.__init__() method.
        
        Returns
        -------
        Client_Connect_Strategy
            Subclass of abstract base class Client_Connect_Strategy. The called
            strategy subclass must have a 'connect' method specified.
        """

        if kwargs.get('strategy'):
            return kwargs['strategy']

        if kwargs.get('session'):
            return Session_Strategy
        
        if kwargs.get('connection'):
            return Connection_String_Strategy
        
        if kwargs.get('config_file'):
            return Config_File_Strategy
        
        if kwargs.get('backend'):
            return Explicit_Strategy
        
        return Search_Config_Strategy
        
# ==============================================================================