import os
import yaml
from munch import Munch
import sys
from rich.console import Console



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
        
        if config_file is None:
            config_file = os.path.expanduser("~/.config/redwood.yaml")
        
        if not os.path.exists(config_file):
            self.create_config(config_file)

        with open(config_file, "r") as f:
            self._config = yaml.safe_load(f)
        self._munch = Munch.fromDict(self._config)
    
    def __getattr__(self, name):
        try:
            if name in self._munch:
                return self._munch[name]
            else:
                return None
        except (KeyError, AttributeError):
            return None

    def exists(self, path: str) -> bool:
        parts = path.split(".")
        current = self._munch
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return False
        return True
    
    def create_config(self, config_file: str):
        example_config = os.path.join(os.path.dirname(__file__), "..", "..", "redwood.example.yaml")
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(example_config, "r") as src, open(config_file, "w") as dst:
            dst.write(src.read())
        
        
        console = Console()
        console.print("[bold yellow]No configuration file found.[/bold yellow]")
        console.print(f"I created an example config file at {config_file}. Please edit it with your settings and restart the application.")
        sys.exit(0)
