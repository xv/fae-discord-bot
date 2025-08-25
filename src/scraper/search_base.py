import requests
from enum import IntEnum, StrEnum
from selectolax.parser import HTMLParser, Node
from common.locale_tools import LocaleCode
from scraper.exceptions import ScrapingError

class SearchType(IntEnum):
  """
  Enum containing values specifying whether to search for an
  Adventurer or Guild.
  """
  ADVENTURER = 0
  GUILD = 1

class AdventurerSearchType(IntEnum):
  """
  Enum containing values specifying whether the Adventurer search is
  conducted via Family or Character name.
  """
  CHARACTER_NAME = 1
  FAMILY_NAME = 2

class GameRegion(StrEnum):
  """
  Enum containing values specifying the region of the game served.
  """
  ASIA = "ASIA"
  EU = "EU"
  NA = "NA"

class NameSearch:
  def __init__(
    self,
    region: GameRegion,
    search_type: SearchType,
    search_params: str):
    """
    Initializes the `NameSearch` class.

    Parameters
    ----------
    search_type:
      Specifies whether to search for an Adventurer or a Guild.
    search_params:
      URL parameters for the search result.
    """
    self.region = region
    self.locale : LocaleCode

    # We're not going to bother with specifying locale (e.g., en-US) in the URL;
    # let it redirect on its own
    if region == GameRegion.ASIA:
      self.search_url = "https://blackdesert.pearlabyss.com/ASIA/Game"
      self.search_url += \
        f"/Profile/Search?{search_params}" \
        if search_type == SearchType.ADVENTURER else \
        f"/Guild?{search_params}"
    else:
      subdomain = \
        "naeu" \
        if region in {GameRegion.NA, GameRegion.EU} else \
        region.lower()
      
      self.search_url = f"https://www.{subdomain}.playblackdesert.com/Adventure"
      self.search_url += \
        f"?{search_params}" \
        if search_type == SearchType.ADVENTURER else \
        f"/Guild?{search_params}"
    
  def _get_search_result_html(self) -> Node:
    """
    Sends a web request to the URL specified in `search_url`.

    Returns
    -------
    On failure, a `ScrapingError` exception is raised.

    On success, the function returns a Selectolax `Node` containing the HTML of
    the element representing the search result row.
    """
    page = requests.get(self.search_url, allow_redirects=True)

    if page.status_code != 200:
      raise ScrapingError(f"The request resulted in status code {page.status_code}")
    elif "/shutdown/" in page.url:
      # When the game is under weekly maintenance, any URL on the domain would
      # redirect to something like this: playblackdesert.com/en-US/shutdown/
      raise ScrapingError("The website is down for maintenance.")
    
    # Update our original URL to the one redirected to through the web request
    # This would add the page locale, if any
    self.search_url = page.url

    parser = HTMLParser(page.content)

    if parser.body.child.tag == "iframe":
      raise ScrapingError("hCaptcha authentication is required!")

    locale = parser.root.attributes.get("lang")
    if locale:
      # The webpage returns locale codes in hyphenated form (e.g., en-US) but
      # we work with underscored versions here
      self.locale = LocaleCode(locale.replace("-", "_"))
    
    row = parser.css_first("div.box_list_area li")
    if not row:
      raise ScrapingError("The search result node does not exist.")

    return row