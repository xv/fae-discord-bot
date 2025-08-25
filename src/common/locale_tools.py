from enum import StrEnum

class LocaleCode(StrEnum):
  """
  Specifies website locales supported by Pearl Abyss.
  """
  EN_US = "en_US"
  DE_DE = "de_DE"
  FR_FR = "fr_FR"
  ES_ES = "es_ES"
  ES_MX = "es_MX"
  PT_BR = "pt_BR"
  TR_TR = "tr_TR"
  KO_KR = "ko_KR"
  JA_JP = "ja_JP"
  ZH_TW = "zh_TW"
  TH_TH = "th_TH"

# Unfortunately, when scraping a guild name, there is no clear semantic way of
# distinguishing between the states "guild is private" and "not in a guild"
# because both simply use <span>text</span>. So, checking what the string inside
# <span> actually says according to the page's locale is the only reliable way
# to tell the state
#
# If the HTML element containing the state text is <span> and its value is not
# found in this dictionary, that means the state is "not in a guild"
#
# The values in this dictionary apply not only to guild names, but also other
# things that can be set to private. This includes the character level and
# life skill levels
privacy_state_private = {
  LocaleCode.EN_US : "Private",
  LocaleCode.DE_DE : "Privat",
  LocaleCode.FR_FR : "Privé",
  LocaleCode.ES_ES : "Privado",
  LocaleCode.ES_MX : "Privado",
  LocaleCode.PT_BR : "Privado",
  LocaleCode.TR_TR : "Gizli",
  LocaleCode.KO_KR : "비공개",
  LocaleCode.JA_JP : "非公開",
  LocaleCode.ZH_TW : "非公開",
  LocaleCode.TH_TH : "ไม่เปิดเผย"
}