from urllib3 import Retry
from requests.adapters import HTTPAdapter
import requests
from urllib.parse import urlparse, parse_qs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

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

    @staticmethod
    def get_table_data(row, index, multiple=False):
        td_tags = row.find_all("td")
        if len(td_tags) > index:
            text = td_tags[index].text.strip()
            return text.split(",") if multiple else text
        return ["N/A"] if multiple else "N/A"

    @staticmethod
    def click_button(driver, by_method, identifier, wait_time=10):
        """
        Általános metódus egy kattintható elem megtalálására és kattintására.
        :param driver: Selenium WebDriver objektum.
        :param by_method: A keresési metódus (By.CLASS_NAME, By.CSS_SELECTOR stb.).
        :param identifier: Az elem azonosítója.
        :param wait_time: Várakozási idő másodpercben (alapértelmezett: 10).
        """
        try:
            wait = WebDriverWait(driver, wait_time)
            button = wait.until(EC.element_to_be_clickable((by_method, identifier)))
            button.click()
        except Exception as e:
            print(f"Hiba történt a gombra kattintás során: {e}")

    @staticmethod
    def clean_html_content(html_content):
        return re.sub(r'[\r\n\t]', ' ', html_content).strip()
