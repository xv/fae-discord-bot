class ScrapingError(Exception):
  """Raised when there is an error in the scraping process."""
  def __init__(self, message: str):
    self.message = message
    super().__init__(self.message)