import disnake
from disnake.ext import commands
from scraper.guild_search import GuildSearch
from scraper.search_base import GameRegion

class GuildCog(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.cooldown(1, 5)
  @commands.slash_command(name="gld")
  async def get_guild_info(
    self,
    inter: disnake.ApplicationCommandInteraction,
    name: commands.String[str, 2, 16],
    region: GameRegion=GameRegion.NA):
    """
    Obtain info about a Black Desert guild.

    Parameters
    ----------
    name:
      The name of the guild to search for.
    region:
      Specifies the game region.
    """
    await inter.response.defer()

    guild = GuildSearch(region=region, search_text=name)
    
    if guild.search_result is None:
      await inter.followup.send("Could not find a guild by that name.")
      return
    
    embed = disnake.Embed(
      url=guild.profile_url,
      title=guild.name,
      description=f"Guild created on {guild.creation_date}",
      color=disnake.Color(0x3498db))

    embed.add_field(
      name="Master",
      value=f"[{guild.master}]({guild.master_profile_url})",
      inline=True)

    embed.add_field(
      name="Members",
      value=str(guild.member_count),
      inline=True)

    await inter.followup.send(embed=embed)

def setup(bot: commands.Bot):
  bot.add_cog(GuildCog(bot))