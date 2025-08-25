from typing import TypedDict
from scraper.search_base import GameRegion, NameSearch, SearchType, AdventurerSearchType
from scraper.adventurer_profile import AdventurerProfile
from common.locale_tools import privacy_state_private

class AdventurerInfo(TypedDict):
  family_name: str
  profile_url: str
  avatar_url: str
  character_name : str
  character_level: str
  guild_name: str
  guild_url: str
  guild_is_private: bool

class AdventurerSearch(NameSearch):
  # The website does not link to the image directly in the HTML but rather uses
  # a CSS ::before pseudo-element to specify the URLs. We're mapping the CSS
  # classes to the filenames of the avatars so we can easily look them up
  css_avatar_classes = {
    "icn_character0": "character0.png",   # Warrior
    "icn_character1": "character1.png",   # Hashashin
    "icn_character2": "character2.png",   # Sage
    "icn_character3": "character3.png",   # Wukong
    "icn_character4": "character4.png",   # Ranger
    "icn_character5": "character5.png",   # Guardian
    "icn_character6": "character6.png",   # Scholar
    "icn_character7": "character7.png",   # Drakania
    "icn_character8": "character8.png",   # Nova
    "icn_character9": "character9.png",   # Sorceress 
    "icn_character10": "character10.png", # Corsair
    "icn_character11": "character11.png", # Lahn
    "icn_character12": "character12.png", # Berserker
    "icn_character15": "character15.png", # Maegu
    "icn_character16": "character16.png", # Tamer
    "icn_character17": "character17.png", # Shai
    "icn_character19": "character19.png", # Striker
    "icn_character20": "character20.png", # Musa
    "icn_character21": "character21.png", # Maehwa
    "icn_character23": "character23.png", # Mystic
    "icn_character24": "character24.png", # Valkyrie
    "icn_character25": "character25.png", # Kunoichi
    "icn_character26": "character26.png", # Ninja
    "icn_character27": "character27.png", # Dark Knight
    "icn_character28": "character28.png", # Wizard
    "icn_character29": "character29.png", # Archer
    "icn_character30": "character30.png", # Woosa
    "icn_character31": "character31.png", # Witch
    "icn_character33": "character33.png", # Dosa
    "icn_character34": "character34.png"  # Deadeye
  }

  def __init__(
    self, 
    region: GameRegion, 
    search_type: AdventurerSearchType,
    search_keyword: str):
    """
    Initializes the `AdventurerSearch` class.

    Parameters
    ----------
    region:
      The game's geographical region.
    search_type:
      The type of Adventurer name.
    search_keyword:
      The name to search.
    """
    if region == GameRegion.ASIA:
      params = f"_type={search_type}&" \
               f"_keyword={search_keyword}"
    else:
      params = f"searchType={search_type}&" \
               f"searchKeyword={search_keyword}"

      if region in {GameRegion.NA, GameRegion.EU}:
        params += f"&region={region}"

    super().__init__(region, SearchType.ADVENTURER, params)

    self.search_result = self._scrape_search_result()

    if not self.search_result:
      return
    
    profile_url = self.search_result["profile_url"]
    self.profile = AdventurerProfile(profile_url)

  def _get_avatar_url(self, css_class: str | None) -> str:
    """
    Retrieves the URL of the Adventurer's avatar based on the given CSS class.

    Parameters
    ----------
    css_class:
      The CSS class name of the avatar to look up. If this is `None`, the
      function will return a URL to a default/silhouette avatar.

    Returns
    -------
    A `str` containing the full URL to the avatar.
    """
    if self.region == GameRegion.ASIA:
      url = "https://s1.pearlcdn.com/bdo/brand/contents_bdo/img/character/"
    else:
      cdn_region = \
        "NAEU" \
        if self.region in {GameRegion.NA, GameRegion.EU} else \
        self.region.upper()
      url = f"https://s1.pearlcdn.com/{cdn_region}/contents/img/common/character/"
    
    avatar_filename = \
      "character_default.png" \
      if not css_class else \
      self.css_avatar_classes[css_class]
    return url + avatar_filename
  
  def _scrape_search_result(self) -> AdventurerInfo | None:
    """
    Scrapes the Adventurer search result page for available information.

    Returns
    -------
    On failure, the function returns `None`.

    If the adventurer is not found, function returns `None`; otherwise, an
    `AdventurerInfo` object containing key-value pairs is returned.
    """
    row = self._get_search_result_html()
    
    if row.attributes.get("class") == "no_result":
      # Adventurer not found
      return None
    
    data : AdventurerInfo = {
      "family_name": "",
      "profile_url": "",
      "avatar_url": "",
      "character_name": "",
      "character_level": "",
      "guild_name": "",
      "guild_url": "",
      "guild_is_private": False
    }
    
    def scrape_family_info():
      """
      Scrapes the Adventurer's Family name and profile URL. The following keys
      are set:
        * `family_name`
        * `profile_url`
      """
      element = row.css_first("div.title a")

      family_name = element.text()
      profile_url = str(element.attributes.get("href", ""))

      data["family_name"] = family_name
      data["profile_url"] = profile_url

    def scrape_character_info():
      """
      Scrapes the Adventurer's main character information. The following keys
      are set:
        * `avatar_url`
        * `character_name`
        * `character_level`
      """
      # If a main character is set, the first child element will be
      # <span class="character_desc">, otherwise just <span> and it will be the
      # only child
      element = row.css_first("div.user_info span")
      if not element.attributes.get("class"):
        # use the default silhouette avatar
        data["avatar_url"] = self._get_avatar_url(None)
        return
      
      avatar_css_class = element.css_first("span.img_area").attributes["class"]
      if avatar_css_class:
        avatar_css_class = avatar_css_class.split(" ")[2]
        data["avatar_url"] = self._get_avatar_url(avatar_css_class)

      level, name = element.css_first("span.text_area")\
        .text(separator=" ", strip=True)\
        .split()
      
      # The level string is in the format "Lv.#", or if private, "Lv.Private"
      # For localization purposes, we'll only grab the portion after the period
      if "." in level:
        level = level.split(".")[1]
      
      data["character_name"] = name

      if level.isdigit():
        data["character_level"] = level

    def scrape_guild_info():
      """
      Scrapes the Adventurer's guild information. The following keys are set:
        * `guild_name`
        * `guild_url`
        * `guild_is_private`
      """
      # If the Adventurer is in a guild AND the guild is NOT private, the child
      # element will be <a href="...">guild name here</a>
      #
      # If the Adventurer is NOT in a guild OR the guild is private, the child
      # element will be <span>state text here</span>
      element = row.css_first("div.state > :first-child")

      guild_name = ""
      guild_url = ""
      guild_is_private = False

      if element.tag == "a":
        # Guild name and url are public
        href = element.attributes.get("href")

        guild_name = element.text()
        if href: guild_url = href
      else:
        # Guild is private or not in a guild
        guild_is_private = element.text() == privacy_state_private.get(self.locale)

      data["guild_is_private"] = guild_is_private
      data["guild_name"] = guild_name
      data["guild_url"] = guild_url

    scrape_family_info()
    scrape_character_info()
    scrape_guild_info()
    return data
  
  @property
  def family_name(self) -> str | None:
    """
    The Family name of the adventurer.
    """
    if self.search_result:
      return self.search_result["family_name"]
  
  @property
  def profile_url(self) -> str | None:
    """
    The profile URL of the adventurer.
    """
    if self.search_result:
      return self.search_result["profile_url"]
  
  @property
  def avatar_url(self) -> str | None:
    """
    The avatar URL of the adventurer.
    """
    if self.search_result:
      return self.search_result["avatar_url"]
  
  @property
  def character_name(self) -> str | None:
    """
    The character name of the adventurer.
    """
    if self.search_result:
      return self.search_result["character_name"]
  
  @property
  def character_level(self) -> str | None:
    """
    The character level of the adventurer.
    """
    if self.search_result:
      return self.search_result["character_level"]
  
  @property
  def guild_name(self) -> str | None:
    """
    The adventurer's guild name.
    """
    if self.search_result:
      return self.search_result["guild_name"]
  
  @property
  def guild_url(self) -> str | None:
    """
    The adventurer's guild profile URL.
    """
    if self.search_result:
      return self.search_result["guild_url"]
  
  @property
  def guild_is_private(self) -> bool | None:
    """
    Whether the adventure's guild name is set to private.
    """
    if self.search_result:
      return self.search_result["guild_is_private"]