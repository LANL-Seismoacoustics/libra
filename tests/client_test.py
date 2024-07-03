import os
import unittest
from typing import Dict

from sqlalchemy.orm import Session
import pdb

from libra import Client
from libra import Client_Connect_Strategy

class Client_Connection_Tests(unittest.TestCase):
    backend, username, password, server, port, instance = 'postgres', 'scott', 'tiger', 'myserver.edu', 22, 'mydb'
    test_config_file = 'tests/supplement/config_test.cnf'
    connection_str   = 'postgres://scott:tiger@myserver.edu:22/mydb'

    test_session = Session(connection_str)

    def test_session_connect(self):
        """Simply a Session object through"""

        session = Client(session = self.test_session)()

        return self.assertEqual(session.bind, self.test_session.bind)
    
    def test_connection_str_connect(self):
        """Pass a connection string through"""

        session = Client(connection = self.connection_str)()

        return self.assertEqual(session.bind, self.test_session.bind)

    def test_config_file_connect(self):
        """Call on a config file"""

        session = Client(config_file = self.test_config_file)()

        return self.assertEqual(session.bind, self.test_session.bind)

    def test_explicit_connect(self):
        """Test explicit declaration of attributes of connection string"""

        session = Client(
            backend  = self.backend,
            username = self.username,
            password = self.password,
            server   = self.server,
            port     = self.port,
            instance = self.instance
        )()
        
        return self.assertEqual(session.bind, self.test_session.bind)

    def test_config_search_connect(self):
        """
        Looks for config file in specified directory and automatically calls 
        that config file to splice together a connection string.
        """

        session = Client(search_dir = 'tests/supplement')()

        return self.assertEqual(session.bind, self.test_session.bind)
    
    def test_config_search_nondefault_extension(self):
        """Test config file search where a non-default file extension is passed."""

        session = Client(search_dir = 'tests/supplement', extension = 'env')()

        return self.assertEqual(session.bind, self.test_session.bind)
    
    def test_custom_strategy(self):
        """Test the process of adding a custom connection strategy"""

        user_profile = {'username' : 'scott', 'password' : 'tiger'}
        class UserProfile_Connect_Strategy(Client_Connect_Strategy):
            def connect(user_profile : Dict[str, str]) -> Session:
                
                username = user_profile.get('username', '')
                password = user_profile.get('password', '')

                conn_str = f'postgres://{username}:{password}@myserver.edu:22/mydb'

                return Session(conn_str)
        
        session = Client(strategy = UserProfile_Connect_Strategy, user_profile = user_profile)()

        return self.assertEqual(session.bind, self.test_session.bind)


if __name__ == "__main__":
    unittest.main()