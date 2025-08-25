import disnake
from disnake.ext import commands
from scraper.search_base import AdventurerSearchType, GameRegion
from scraper.adventurer_search import AdventurerSearch
from scraper.adventurer_profile import LifeSkill

class AdventurerCog(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.cooldown(1, 5)
  @commands.slash_command(name="adv")
  async def get_adventurer_info(
    self,
    inter: disnake.ApplicationCommandInteraction,
    name: commands.String[str, 1, 16],
    is_char_name: bool=False,
    region: GameRegion=GameRegion.NA,
    life_skill=commands.Param(
      default=None,
      choices=[name.value for name in LifeSkill])):
    """
    Obtain info about a Black Desert adventurer.

    Parameters
    ----------
    name:
      The Family name to search for.
    is_char_name:
      Searches for a character name instead if true.
    region:
      Specifies the game region.
    life_skill:
      Finds the level of the specified life skill.
    """
    await inter.response.defer()

    adventurer = AdventurerSearch(
      region=region,
      search_type= \
        AdventurerSearchType.CHARACTER_NAME \
        if is_char_name else \
        AdventurerSearchType.FAMILY_NAME,
      search_keyword=name)
    
    if adventurer.search_result is None:
      await inter.followup.send("Could not find an adventurer by that name.")
      return

    embed = disnake.Embed(
      url=adventurer.profile_url,
      title=adventurer.family_name,
      description=f"Family created on {adventurer.profile.family_creation_date}",
      color=disnake.Color(0x3498db))

    embed.set_thumbnail(url=adventurer.avatar_url)
   
    char_name = adventurer.character_name
    
    # It's possible that an Adventurer has never set a main character, so we
    # take that into account
    if char_name:
      char_level = adventurer.character_level
      embed.add_field(
        name="Character" if is_char_name else "Main Character",
        value=f"{char_name} (Lv. {char_level if char_level else 'Private'})",
        inline=True)

    guild_name = adventurer.guild_name
    guild_url = adventurer.guild_url

    if not guild_name:
      guild_name = "Private" if adventurer.guild_is_private else "Not in a guild"

    embed.add_field(
      name="Guild",
      value=f"[{guild_name}]({guild_url})" if guild_url else guild_name,
      inline=True)
    
    embed.add_field(
      name="Gear Score",
      value=adventurer.profile.gear_score,
      inline=False)
    
    if life_skill and adventurer.profile:
      life_skill_level = adventurer.profile.get_life_skill_level(life_skill)
      if not life_skill_level:
        life_skill_level = "Private"

      embed.add_field(
        name=f"{life_skill} Level",
        value=life_skill_level,
        inline=False)

    await inter.followup.send(embed=embed)

def setup(bot: commands.Bot):
  bot.add_cog(AdventurerCog(bot))