import os
import sys
import logging
import disnake
from time import time
from pathlib import Path
from dotenv import load_dotenv
from disnake.ext import commands
from config import load_config

load_dotenv()
config = load_config()

class FaeBot(commands.InteractionBot):
  # Since we're only using slash commands, we don't really need any of the
  # events offered by enabling intents
  bot_intents = disnake.Intents.none()

  bot_sync_flags = commands.CommandSyncFlags.default()

  def __init__(self):
    """
    Initializes the `FaeBot` class.
    """
    guilds = None if config["global_sync"] else config["guilds"]

    super().__init__(
      application_id=int(os.environ["APPLICATION_ID"]),
      owner_ids=config["owners"],
      test_guilds=guilds,
      intents=self.bot_intents,
      command_sync_flags=self.bot_sync_flags)

    self._load_cogs()
  
  def setup_logging(self, name: str):
    """
    Sets up a logger.

    Parameters
    ----------
    name:
      The name of the logger.
    """
    logging_config = config["logging"]

    filename = f"logs/{name}.log" \
               if logging_config["overwrite"] else \
               f"logs/{name}_{int(time())}.log"

    logger = logging.getLogger(name)
    log_handler = logging.FileHandler(
      filename=filename,
      mode="w",
      encoding="utf-8")

    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
      "[{asctime}] [{levelname:<8}] {name}: {message}",
      date_format,
      style="{")
    
    log_handler.setFormatter(formatter)
    logger.setLevel(logging_config["level"].upper())
    logger.addHandler(log_handler)

  def _load_cogs(self):
    """
    Loads slash command cogs.
    """
    cogs_dir = os.path.join(Path(os.path.dirname(__file__)), "cogs")
    for file in os.listdir(cogs_dir):
      if not file.endswith(".py"):
        continue
      ext_name = file[:-3]
      try:
        self.load_extension(f"cogs.{ext_name}")
      except Exception as e:
        sys.exit(f"{type(e).__name__}: {e}")

  async def _delete_guild_commands_on_global_sync(self):
    """
    Deletes guild commands (if any) when global syncing is enabled.

    If slash commands exist on servers whose IDs are specified in `test_guilds`
    and global syncing was then turned on, it would result in duplicating each
    command, as one would be the old and outdated guild command, and the other
    would the newly synced global command. Disnake suggests simply executing
    the old out-of-sync guild command and it would get deleted right away, and
    that is indeed what happens; however, I find it rather annoying to see
    duplicate commands with the same name, not knowing which is which until I
    run it.
    
    This function fetches guild commands from servers whose IDs are specified
    in `test_guilds` and deletes them if global syncing is turned on.
    However, the approach is not exactly performance friendly (the more guilds
    specified, the slower it will be) and is probably subject to Discord's rate
    limits. I do not recommend calling this function if more than two guilds
    are specified in `test_guilds`.
    """
    if self._test_guilds:
      return
    
    for guild_id in config["guilds"]:
      cmd_ids = {
        cmd.id for cmd in await self.fetch_guild_commands(guild_id)
      }
      print(cmd_ids)
      
      if not len(cmd_ids): continue
      while cmd_ids:
        await self.delete_guild_command(guild_id, cmd_ids.pop())

  async def on_connect(self):
    print(f"Logged in as {self.user}.")

  async def on_ready(self):
    print(f"Bot is ready.")

bot = FaeBot()

if config["logging"]["enabled"]:
  bot.setup_logging("disnake")
  bot.setup_logging("fae")

bot.run(os.environ["AUTH_TOKEN"])