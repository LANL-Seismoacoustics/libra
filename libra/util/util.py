"""
Brady Spears
5/5/25

Utility functions to the Libra package.
"""
# ==============================================================================

import re
import ast
from datetime import datetime, timezone
from typing import Any

# ==============================================================================

REGEX_MAP : dict[re.Pattern, Any] = {
    r'None' : None,
    r'datetime\.now\(timezone\.utc\)' : datetime.now(timezone.utc)
}

# ==============================================================================

class Evaluator:
    """
    Class with functions to evaluate Python code encoded as strings.
    """

    def __init__(self, regex_map : dict[re.Pattern, Any] = REGEX_MAP) -> None:
        """
        Creates an instance of evaluator by assigning a regex_map, which maps a 
        regex pattern to a value. 

        Paramters
        ---------
        regex_map : dict
            Dictionary mapping regex string patterns to specific Python scalars 
            or callables.
        """

        self.regex_map = regex_map

    def __call__(self, _input : Any) -> Any:
        """
        Evaluate an input string by checking first if the string maps to a key 
        in regex_map. If so, the value associated with that key is returned. 
        If not, the string is evaluated using the ast.literal_eval() function.
        If the input is not a string, the value will just be returned.

        Parameters
        ----------
        _input : Any
            Any value to evaluate. 
        
        Returns
        -------
        object
            The evaluated value of _input as a member of the regex_map, as the 
            return value of ast.literal_eval(), or as _input untouched.
        """

        if isinstance(_input, str):
            for key in self.regex_map.keys():
                if bool(re.fullmatch(key, _input)):
                    return self.regex_map[key]
            
            return ast.literal_eval(_input)

        return _input

# ==============================================================================
