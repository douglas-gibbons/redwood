import os
import yaml
from munch import Munch


# Reads in the configuration file and provides access to its parameters
# in dot notation
#
# e.g.
#
# ``` 
# c = Config("/path/to/config.yaml")
# n = c.model.name
# ```
class Config:

    def __init__(self, config_file: str = None):
        
        with open(config_file, "r") as f:
            self._config = yaml.safe_load(f)
        self._munch = Munch.fromDict(self._config)
    
    def __getattr__(self, name):
        if name in self._munch:
            return self._munch[name]
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def exists(self, path: str) -> bool:
        parts = path.split(".")
        current = self._munch
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return False
        return True
