from common_args import ArgumentParser
from config_loader import ConfigLoader
from file_save import FileSaver
from scraper_helper import ScraperHelper
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class WebCrawler:
    def __init__(self, config_loader, args):
        self.visited = set()
        self.product_links = set()
        self.session = ScraperHelper.get_session_with_retries()
        self.save_threshold = 100
        self.saved_link_count = 0
        self.config = config_loader.get_supplier_settings(args.supplier, args.format)
        self.webshop_url = self.config.get(f"webshop_url_{args.l}")
        self.output_file = self.config["product_links_template"].format(supplier=args.supplier, l=args.l,
                                                                        format=args.format)

    def extract_main_links(self, soup, base_url):
        main_links = set()
        nav_menu = soup.find('nav', id='menu_categories')
        if nav_menu:
            for a_tag in nav_menu.find_all('a', href=True, class_="nav-link"):
                if not a_tag.find_parent('ul', class_="navbar-subnav"):
                    full_url = urljoin(base_url, a_tag['href'])
                    print(full_url)
                    main_links.add(full_url)
        return main_links

    def crawl_page(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for a_tag in soup.find_all('a', href=True, class_="product__name"):
                full_url = urljoin(url, a_tag['href'])
                self.product_links.add(full_url)
        except requests.RequestException as e:
            print(f"Hiba történt az oldal bejárása közben: {url} - {e}")

    def crawl(self):
        start_url = self.webshop_url  # Az aktuális nyelvű webshop URL
        try:
            response = self.session.get(start_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            main_links = self.extract_main_links(soup, start_url)

            for link in main_links:
                if link in self.visited:
                    continue

                print(f"Feldolgozás: {link}")
                self.visited.add(link)

                try:
                    response = self.session.get(link, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    max_page = ScraperHelper.find_max_page(soup, link_class="pagination__link", query_param="counter")

                    for page in range(1, max_page + 1):
                        current_url = f"{link.split('?')[0]}?counter={page}"
                        if current_url in self.visited:
                            continue

                        print(f"Feldolgozás: {current_url}")
                        self.visited.add(current_url)
                        self.crawl_page(current_url)
                        data = [{"link": link} for link in self.product_links]
                        self.saved_link_count = FileSaver.save_line(
                            data,  # A mentendő adat
                            self.saved_link_count,  # Az eddig mentett adatok száma
                            self.save_threshold,  # A mentési küszöbérték
                            self.output_file,  # A fájl elérési útvonala
                            file_format=args.format  # A fájl formátuma (tsv vagy xlsx)
                        )

                except requests.RequestException as e:
                    print(f"Hiba a fő link feldolgozása közben: {link} - {e}")

        except requests.RequestException as e:
            print(f"Hiba a kezdő oldal feldolgozása során: {start_url} - {e}")


if __name__ == "__main__":
    args = ArgumentParser().parse()
    config_loader = ConfigLoader("../config.json")
    crawler = WebCrawler(config_loader, args)
    crawler.crawl()
