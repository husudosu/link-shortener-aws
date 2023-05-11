import re
from dataclasses import dataclass


# https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
URL_REGEX = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


@dataclass
class URLModel:
    apiKey: str
    shortLinkId: str
    url: str

    def __post_init__(self):
        if not re.match(URL_REGEX, self.url):
            raise ValueError("URL is not in correct format!")
