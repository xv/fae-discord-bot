from typing import TypedDict
from scraper.search_base import NameSearch, GameRegion, SearchType
from common.date_tools import clean_date

class GuildInfo(TypedDict):
  name: str
  profile_url : str
  master: str
  master_profile_url: str
  creation_date: str
  member_count: int

class GuildSearch(NameSearch):
  def __init__(
    self, 
    region: GameRegion, 
    search_text: str):
    """
    Initializes the `GuildSearch` class.

    Parameters
    ----------
    region:
      The game's geographical region.
    search_text:
      The name to search.
    """
    if region == GameRegion.ASIA:
      params = f"_searchText={search_text}"
    else:
      params = f"searchText={search_text}"
      if region in {GameRegion.NA, GameRegion.EU}:
        params += f"&region={region}"
        
    super().__init__(region, SearchType.GUILD, params)

    self.search_result = self._scrape_search_result()

  def _scrape_search_result(self) -> GuildInfo | None:
    """
    Scrapes the Guild search result page for available information.

    Returns
    -------
    If the guild is not found, function returns `None`; otherwise, a `GuildInfo`
    object containing key-value pairs is returned.
    """
    row = self._get_search_result_html()

    if row.attributes.get("class") == "no_result":
      # Guild not found
      return None

    data : GuildInfo = {
      "name" : "",
      "profile_url" : "",
      "master" : "",
      "master_profile_url" : "",
      "creation_date" : "",
      "member_count" : 0
    }

    def scrape_name():
      """
      Scrapes the guild's name and profile URL. The following keys are set:
        * `name`
        * `profile_url`
      """
      guild_name = row.css_first("span.text a")
      profile_url = str(guild_name.attributes.get("href", ""))

      # The developers chose to use a relative URL only in the Guild search page
      if profile_url.startswith("/"):
        profile_url = self.search_url.split(".com")[0] + ".com" + profile_url

      data["name"] = guild_name.text()
      data["profile_url"] = profile_url
    
    def scrape_master():
      """
      Scrapes the guild master's Family name and profile URL. The following keys
      are set:
        * `master`
        * `master_profile_url`
      """
      guild_master = row.css_first("div.guild_info a")
      data["master"] = guild_master.text()

      master_prof_url = str(guild_master.attributes.get("href", ""))
      data["master_profile_url"] = master_prof_url

    def scrape_creation_date():
      """
      Scrapes the guild's creation date. The following keys are set:
        * `creation_date`
      """
      raw_date = row.css_first("div.date").text()
      data["creation_date"] = clean_date(raw_date)
      
    def scrape_member_count():
      """
      Scrapes the guild's member count. The following keys are set:
        * `member_count`
      """
      data["member_count"] = int(row.css_first("div.member").text())

    scrape_name()
    scrape_master()
    scrape_creation_date()
    scrape_member_count()
    return data
  
  @property
  def name(self) -> str | None:
    """
    The name of the Guild.
    """
    if self.search_result:
      return self.search_result["name"]
  
  @property
  def creation_date(self) -> str | None:
    """
    The creation date of the guild.
    """
    if self.search_result:
      return self.search_result["creation_date"]
  
  @property
  def profile_url(self) -> str | None:
    """
    The profile URL of the guild.
    """
    if self.search_result:
      return self.search_result["profile_url"]

  @property
  def master(self) -> str | None:
    """
    The guild master's Family name.
    """
    if self.search_result:
      return self.search_result["master"]
  
  @property
  def master_profile_url(self) -> str | None:
    """
    The guild master's profile URL.
    """
    if self.search_result:
      return self.search_result["master_profile_url"]
  
  @property
  def member_count(self) -> int | None:
    """
    The member count of the guild.
    """
    if self.search_result:
      return self.search_result["member_count"]