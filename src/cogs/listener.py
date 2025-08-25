import logging
import disnake
from disnake.ext import commands

logger = logging.getLogger("fae")

class CommandEventHandler(commands.Cog):
  def get_command_string(self, cmd_name: str, cmd_options: dict) -> str:
    """
    Gets a full command with its option as a single string.

    Parameters
    ----------
    cmd_name:
      The name of the slash command.
    cmd_options:
      The options of the slash command.
    
    Returns
    -------
    A `str` containing the full command as it was entered in Discord.
    """
    return f"/{cmd_name} " + \
           " ".join([f"{k}: {v}" for k, v in cmd_options.items()])

  @commands.Cog.listener("on_slash_command_error")
  async def handle_command_error(
    self,
    inter: disnake.ApplicationCommandInteraction,
    error: commands.CommandError):

    if isinstance(error, commands.CommandOnCooldown):
      await inter.send(str(error), ephemeral=True)
      return

    cmd_name = inter.application_command.name
    message = f"Oh my! Command `/{cmd_name}` experienced an error.\n" \
              "The details will be conveyed to my master through logs (✿◠‿◠)"

    await inter.send(message)

    message = self.get_command_string(cmd_name, inter.filled_options)
    logger.error(message, exc_info=error)

  @commands.Cog.listener("on_slash_command_completion")
  async def handle_command_success(
    self,
    inter: disnake.ApplicationCommandInteraction):

    author = inter.author.id
    guild = inter.guild.id if inter.guild else None

    command = self.get_command_string(
      inter.application_command.name, inter.filled_options)
    
    logger.info(
      f"User {author} in {guild} executed command {command}" 
      if guild else 
      f"User {author} executed command {command}")

def setup(bot: commands.Bot):
  bot.add_cog(CommandEventHandler(bot))