from urllib3 import Retry
from requests.adapters import HTTPAdapter
import requests
from urllib.parse import urlparse, parse_qs

class ScraperHelper:
    @staticmethod
    def get_session_with_retries():
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def find_max_page(soup, link_class, query_param):
        """
        Meghatározza a maximális oldalszámot egy oldalon belül.
        :param soup: A BeautifulSoup objektum, amely tartalmazza a weboldal HTML-jét.
        :param link_class: Az a linkosztály, amely tartalmazza az oldalszámokat.
        :param query_param: Az URL lekérdezési paramétere, amely az oldalszámot tárolja.
        :return: A maximális oldalszám.
        """
        max_page = 1
        a_tags = soup.find_all('a', href=True, class_=link_class)

        for a_tag in a_tags:
            try:
                query = parse_qs(urlparse(a_tag['href']).query)
                if query_param in query:
                    page_number = int(query[query_param][0])
                    max_page = max(max_page, page_number)
            except (ValueError, KeyError, IndexError):
                continue

        return max_page
