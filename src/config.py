import os
import sys
import json
from pathlib import Path
from typing import TypedDict

class LoggingConfig(TypedDict):
  enabled: bool
  overwrite: bool
  level: str

class Config(TypedDict):
  owners: set[int]
  guilds: list[int]
  global_sync: bool
  logging: LoggingConfig

def load_config():
  """
  Loads the bot configuration file.

  Returns
  -------
  A `dict` containing data parsed from the JSON file.
  """
  parent_dir = Path(os.path.dirname(__file__)).parent
  filename = "config.json"
  path = os.path.join(parent_dir, filename)

  if not os.path.isfile(f"{path}"):
    sys.exit(f"Cannot find {path}!")

  with open(f"{path}") as file:
    config = json.load(file)
  return Config(config)