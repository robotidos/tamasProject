import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class LinkCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.termekek_links = set()

    def _get_session_with_retries(self):
        """
        Creates a requests session with retry logic.
        """
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

    def crawl_links(self, url):
        """
        Recursively visits the given URL and finds all links under the same base URL.
        """
        url, _ = urldefrag(url)

        if url in self.visited:
            return

        session = self._get_session_with_retries()

        try:
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            print(f"Visiting: {url}")
            self.visited.add(url)

            container = soup.find(id="container")
            if container:
                for a_tag in container.find_all('a', href=True):
                    href = urljoin(url, a_tag['href'])
                    clean_href, _ = urldefrag(href)

                    if clean_href.startswith("https://www.hikoki-powertools.hu/hu/termekek"):
                        self.termekek_links.add(clean_href)
                        continue

                    if clean_href.startswith("https://www.hikoki-powertools.hu/hu/") and clean_href not in self.visited:
                        self.crawl_links(clean_href)

        except Exception as e:
            print(f"Error visiting {url}: {e}")

    def save_to_tsv(self, output_file, category):
        """
        Saves the links to a TSV file with the specified category.
        """
        try:
            data = pd.DataFrame({"url": sorted(self.termekek_links), "cikkcsoport": category})
            data.to_csv(output_file, sep='\t', index=False, encoding='utf-8', mode='a', header=not pd.io.common.file_exists(output_file))
            print(f"Links saved to {output_file} under category {category}")
        except Exception as e:
            print(f"Error saving links to {output_file}: {e}")

    @staticmethod
    def update_category_from_products(machine_file, product_file):
        """
        Updates or creates the "cikkcsoport" column in the machine_file based on the product_file.
        """
        try:
            machine_data = pd.read_csv(machine_file, sep='\t')
            product_data = pd.read_csv(product_file, sep='\t')

            if 'cikkcsoport' not in machine_data.columns:
                machine_data['cikkcsoport'] = ''

            # Create a dictionary of links and categories from the product_file
            product_links = product_data.set_index('url')['cikkcsoport'].to_dict()

            # Update the machine categories
            machine_data['cikkcsoport'] = machine_data['url'].map(product_links)

            # Save the updated machine file
            machine_data.to_csv(machine_file, sep='\t', index=False, encoding='utf-8')
            print(f"Updated 'cikkcsoport' in {machine_file}")

        except Exception as e:
            print(f"Error updating category: {e}")

if __name__ == "__main__":
    print("Starting: Crawling machine links")
    gepek_crawler = LinkCrawler("https://www.hikoki-powertools.hu/hu/gepek")
    gepek_crawler.crawl_links(gepek_crawler.base_url)

    print("\nStarting: Crawling accessory links")
    tartozekok_crawler = LinkCrawler("https://www.hikoki-powertools.hu/hu/tartozekok")
    tartozekok_crawler.crawl_links(tartozekok_crawler.base_url)

    # Save the machine and accessory links
    output_file = "data/machine_or_accessory.tsv"
    gepek_crawler.save_to_tsv(output_file, "Gép")
    tartozekok_crawler.save_to_tsv(output_file, "Tartozék")

    # Update categories in the hikoki_products file
    product_file = "data/hikoki_products.tsv"
    LinkCrawler.update_category_from_products(product_file, output_file)

    print(f"\nLinks saved: {output_file}")
