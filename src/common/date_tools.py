import re
import locale
import babel.dates
from datetime import datetime
from common.locale_tools import LocaleCode

def _get_date_format(locale: LocaleCode) -> str:
  """
  Returns a date format according to the specified locale.
  
  Parameters
  ----------
  locale:
    The locale to retrieve a date format for.

  Returns
  -------
  A `str` containing format codes for use in `strptime()`.
  """
  format: str

  match locale:
    case LocaleCode.FR_FR | LocaleCode.ES_ES:
      format = "%d %b %Y"
    case LocaleCode.DE_DE:
      format = "%d. %b %Y"
    case LocaleCode.PT_BR | LocaleCode.ES_MX | LocaleCode.TH_TH:
      format = "%d/%m/%Y"
    case LocaleCode.TR_TR:
      format = "%d.%m.%Y"
    case LocaleCode.KO_KR:
      format = "%Y.%m.%d"
    case LocaleCode.JA_JP | LocaleCode.ZH_TW:
      format = "%Y-%m-%d"
    case _: # en_US
      format = "%b %d, %Y"
  return format

def reformat_date(
  date_string: str, 
  src_locale: LocaleCode, dest_locale: LocaleCode) -> str:
  """
  Reformats a given date string from one locale to another.

  Parameters
  ----------
  date_string:
    The string representation of the date to reformat.
  src_locale:
    The locale of the date string.
  dest_locale:
    The locale to reformat the date string as.

  Returns
  -------
  A `str` containing the reformatted date string.
  """
  locale.setlocale(locale.LC_TIME, src_locale)

  fmt = _get_date_format(src_locale)
  dt = datetime.strptime(date_string, fmt)
  
  return babel.dates.format_date(dt.date(), locale=dest_locale)

def clean_date(date_string: str) -> str:
  """
  Simplifies a given date string by removing time and time zone information
  if present, keeping only the date portion.

  Parameters
  ----------
  date_string:
    The date string to format.

  Returns
  -------
  A `str` containing a modified version of the original string.

  If the date specified in `input_date_str` does not match a date pattern on a
  Pearl Abyss webpage, the original, unmodified string will be returned. 
  """
  # See doc/i18n/date-formats.md for date formats used in various locales
  patterns = [
    r"(\w{3} \d{1,2}, \d{4})", # en-US
    r"(\d{2}. \w{3} \d{4})", # de-DE
    r"(\d{1,2} [a-zA-ZÀ-ÿ]{3,4}.? \d{4})", # fr-FR, es-ES
    r"(\d{4}[-.]\d{2}[-.]\d{2})", # ko-KR, ja-JP, zh-TW
    r"(\d{2}[\/.]\d{2}[\/.]\d{4})", # tr-TR, pt-BR, es-MX, th-TH
  ]

  for pattern in patterns:
    match = re.search(pattern, date_string)
    if match: return match.group(0)
  return date_string