import requests
from enum import StrEnum
from selectolax.parser import HTMLParser, Node
from common.date_tools import clean_date
from scraper.exceptions import ScrapingError

class LifeSkill(StrEnum):
  """
  Specifies the names of different life skills in the game.
  """
  ALCHEMY = "Alchemy"
  BARTER = "Barter"
  COOKING = "Cooking"
  FARMING = "Farming"
  FISHING = "Fishing"
  GATHERING = "Gathering"
  HUNTING = "Hunting"
  PROCESSING = "Processing"
  SAILING = "Sailing"
  TRADE = "Trade"
  TRAINING = "Training"

class AdventurerProfile():
  life_skill_css_classes = {
    "Gathering" : "icn_spec01",
    "Fishing" : "icn_spec02",
    "Hunting" : "icn_spec03",
    "Cooking" : "icn_spec04",
    "Alchemy" : "icn_spec05",
    "Processing" : "icn_spec06",
    "Training" : "icn_spec07",
    "Trade" : "icn_spec08",
    "Farming" : "icn_spec09",
    "Sailing" : "icn_spec10",
    "Barter" : "icn_spec11"
  }

  def __init__(self, url: str):
    """
    Initializes the `AdventurerProfile` class.

    Parameters
    ----------
    url:
      The URL to the Adventurer's profile page.
    """
    self.url = url
    self.html = self._get_profile_html()

  def _get_profile_html(self) -> Node:
    page = requests.get(self.url, allow_redirects=True)

    if page.status_code != 200:
      raise ScrapingError(f"The request resulted in status code {page.status_code}")
    
    self.url = page.url

    content = HTMLParser(page.content).css_first("div.container")
    if not content:
      raise ScrapingError("The profile container node does not exist.")
    
    return content
  
  @property
  def family_creation_date(self) -> str:
    """
    Retrieves the Adventurer's family creation date.

    Returns
    -------
    A `str` containing the date the family was created.
    """
    creation_date = self.html.css_first(
      "div.profile_detail li:first-child span:last-of-type").text()
    return clean_date(creation_date)

  @property
  def gear_score(self) -> str:
    """
    Retrieves the Adventurer's gear score.

    Returns
    -------
    A `str` containing the gear score value.
    """
    score = self.html.css_first(
      "div.profile_detail li:nth-child(3) span:nth-child(2)").text()
    return score

  def get_life_skill_level(self, skill: LifeSkill) -> str:
    """
    Finds the level of the specified life skill.

    Parameters
    ----------
    skill:
      The life skill to lookup.

    Returns
    -------
    A `str` containing the level of the specified life skill is returned.
    However, if life skills are private, an empty `str` is returned.
    """
    life_box = self.html.css_first(".character_data_box")
    
    # Levels are private
    attr = life_box.attributes.get("class")
    if attr and "lock" in attr:
      return ""

    css_class = self.life_skill_css_classes[skill]
    level = life_box.css_first(f"span.{css_class}")\
                    .parent.parent.css_first("span.spec_level")\
                    .text(separator=" ", strip=True)
    return level