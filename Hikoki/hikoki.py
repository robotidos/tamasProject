import os
import sys
import re
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import error_log
from common_args import ArgumentParser
from config_loader import ConfigLoader


class SitemapReader:
    def __init__(self, sitemap_url, product_url_prefix):
        self.sitemap_url = sitemap_url
        self.product_url_prefix = product_url_prefix

    def read_sitemap(self):
        response = requests.get(self.sitemap_url)
        if response.status_code == 200:
            xml_content = response.content
            root = ET.fromstring(xml_content)
            links = []
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for loc in root.findall('.//ns:loc', namespace):
                url = loc.text
                if url.startswith(self.product_url_prefix):
                    links.append(url)
            return links
        else:
            raise Exception(f"Hiba történt az XML letöltésekor: {response.status_code}")


class ProductSaver:
    @staticmethod
    def save(data, file_path, file_format="tsv"):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df = pd.DataFrame(data)
        if file_format == "tsv":
            df.to_csv(file_path, sep='\t', index=False, quoting=3, escapechar='\\', doublequote=False)
        elif file_format == "xlsx":
            df.to_excel(file_path, index=False)
        else:
            raise ValueError("Támogatott formátumok: 'tsv', 'xlsx'")


class ProductScraper:
    @staticmethod
    def clean_html_content(html_content):
        return re.sub(r'[\r\n\t]', ' ', html_content).replace("<br>", " ").strip()

    @staticmethod
    def extract_section(soup, section_title, next_element_tag):
        section = soup.find('h3', class_='a-ttl_h3 a-ttl_border a-ttl_main',
                            string=lambda s: s and section_title in s.strip())
        if section:
            next_element = section.find_next(next_element_tag)
            if next_element:
                return ProductScraper.clean_html_content(next_element.decode_contents())
        return ""

    @staticmethod
    def collect_product_data(**kwargs):
        return {key: value for key, value in kwargs.items() if value}

    @staticmethod
    def get_image(sku, soup):
        image_url = ""
        image_tag = soup.find('img', {'src': True, 'alt': sku})
        if not image_tag:
            product_image_div = soup.find('div', class_='product-image')
            if product_image_div:
                image_tag = product_image_div.find('img', {'src': True})
        if image_tag:
            image_url = image_tag['src']
        return image_url

    @staticmethod
    def scrape_product_data(link, error_logger=None):
        try:
            response = requests.get(link)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            sku = link.split("/")[-1]

            name_tag = soup.find('h2', class_='a-ttl_h2')
            product_name = name_tag.find('span', class_='a-ttl_txt').get_text(strip=True) if name_tag else ""

            ean_code = ProductScraper.extract_section(soup, "EAN-kód:", 'p')
            gross_mass = ProductScraper.extract_section(soup, "Bruttó tömeg:", 'p')
            vtsz = ProductScraper.extract_section(soup, "VTSZ:", 'p')

            features = ProductScraper.extract_section(soup, "További jellemzők", 'ul')
            specifications = ProductScraper.extract_section(soup, "Műszaki adatok", 'table')
            included_accessories = ProductScraper.extract_section(soup, "Leszállított tartozékok", 'ul')

            image_url = ProductScraper.get_image(sku, soup)

            if not product_name or not image_url or soup.find('span', class_='a-label a-label_new',
                                                              string="Nem rendelhető"):
                return None

            return {
                "sku": sku,
                "url": link,
                "product_name": product_name,
                "ean_code": ean_code,
                "gross_mass": gross_mass,
                "vtsz": vtsz,
                "features": features,
                "specifications": specifications,
                "included_accessories": included_accessories,
                "image_url": image_url,
            }
        except Exception as e:
            if error_logger:
                error_logger.add_error(link, str(e))
            raise


class ProductProcessor:
    @staticmethod
    def scrape_with_retry(link, error_logger, max_retries=3):
        for attempt in range(max_retries):
            try:
                return ProductScraper.scrape_product_data(link)
            except Exception as e:
                error_logger.add_error(link, str(e))
                if attempt == max_retries - 1:
                    raise

    @staticmethod
    def process_links_parallel(links, output_file, output_format="tsv", max_workers=5):
        product_data = []
        error_logger = error_log.ErrorLogger()
        total_links = len(links)

        # ThreadPoolExecutor párhuzamos feldolgozásra
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Linkek feldolgozása párhuzamosan
            future_to_url = {executor.submit(ProductProcessor.scrape_with_retry, link, error_logger, 3):
                                 link for link in links}

            # Eredmények feldolgozása, ahogy elkészülnek
            for i, future in enumerate(future_to_url, 1):
                link = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        product_data.append(result)
                    ProductSaver.save(product_data, output_file, file_format=output_format)
                    sys.stdout.write(f"\rFeldolgozott linkek: {i}/{total_links}")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"\nHiba történt a következő link feldolgozásakor: {link} - {e}")

        error_logger.log_errors()


    @staticmethod
    def process_sku_or_all_links(args, sitemap_reader, output_file):
        try:
            if args.sku:
                product_links = sitemap_reader.read_sitemap()
                product_url = next((link for link in product_links if args.sku in link), None)
                if product_url:
                    print(f"Adatok feldolgozása az SKU alapján: {args.sku}")
                    product_data = [ProductScraper.scrape_product_data(product_url)]
                    ProductSaver.save(product_data, output_file, file_format=args.format)
                else:
                    print(f"Nem található az SKU a sitemap-ben: {args.sku}")
            else:
                product_links = sitemap_reader.read_sitemap()
                ProductProcessor.process_links_parallel(product_links, output_file, args.format)
        except Exception as e:
            print(f"Hiba történt a feldolgozás során: {e}")


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    args = arg_parser.parse()

    config_loader = ConfigLoader("data/config.json")
    settings = config_loader.get_supplier_settings(args.supplier, args.format)

    sitemap_reader = SitemapReader(settings["sitemap_url"], settings["product_url_prefix"])
    output_file = settings["output_file"]

    ProductProcessor.process_sku_or_all_links(args, sitemap_reader, output_file)
