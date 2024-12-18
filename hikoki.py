from concurrent.futures import ThreadPoolExecutor

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from bs4 import BeautifulSoup
import sys
import path
import re
import argparse

# --supplier Hikoki --format tsv


class SitemapReader:
    """
    Ez már újrahasználható, konfigurálható. Nem ebben a fájlban lesz, hanem majd importálom
    """
    def __init__(self, sitemap_url, product_url_prefix):
        """
        :param sitemap_url: A sitemap.xml elérési útja.
        :param product_url_prefix: Az URL prefix, amely a termékekre jellemző.
        """
        self.sitemap_url = sitemap_url
        self.product_url_prefix = product_url_prefix

    def read_sitemap(self):
        """
        Beolvassa a sitemap.xml fájlt és visszaadja a termék linkeket.
        """
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
        """
        Adatok mentése a megadott formátumban.
        :param data: A mentendő adatokat tartalmazó lista.
        :param file_path: A célfájl elérési útvonala.
        :param file_format: A fájl formátuma ('tsv' vagy 'xlsx').
        """
        df = pd.DataFrame(data)
        if file_format == "tsv":
            df.to_csv(file_path, sep='\t', index=False, quoting=3, escapechar='\\', doublequote=False)
            print(f"Adatok sikeresen mentve TSV formátumban: {file_path}")
        elif file_format == "xlsx":
            df.to_excel(file_path, index=False)
            print(f"Adatok sikeresen mentve XLSX formátumban: {file_path}")
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
    def scrape_product_data(product_url):
        response = requests.get(product_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            sku = product_url.split("/")[-1]

            name_tag = soup.find('h2', class_='a-ttl_h2')
            product_name = name_tag.find('span', class_='a-ttl_txt').get_text(strip=True) if name_tag else ""

            orderable = "N" if soup.find('span', class_='a-label a-label_new', string="Nem rendelhető") else "Y"

            ean_code = ProductScraper.extract_section(soup, "EAN-kód:", 'p')
            gross_mass = ProductScraper.extract_section(soup, "Bruttó tömeg:", 'p')
            vtsz = ProductScraper.extract_section(soup, "VTSZ:", 'p')

            features = ProductScraper.extract_section(soup, "További jellemzők", 'ul')
            specifications = ProductScraper.extract_section(soup, "Műszaki adatok", 'table')
            included_accessories = ProductScraper.extract_section(soup, "Leszállított tartozékok", 'ul')

            image_url = ProductScraper.get_image(sku, soup)

            # if not product_name or not image_url or orderable == "N":
            #     return None

            return ProductScraper.collect_product_data(
                sku=sku,
                product_name=product_name,
                product_url=product_url,
                ean_code=ean_code,
                gross_mass=gross_mass,
                vtsz=vtsz,
                features=features,
                specifications=specifications,
                included_accessories=included_accessories,
                image_url=image_url,
                orderable=orderable
            )
        else:
            raise Exception(f"Hiba történt az oldal letöltésekor: {response.status_code}")


class ProductProcessor:
    @staticmethod
    def process_links_parallel(links, output_file, output_format="tsv", max_workers=5):
        product_data = []
        total_links = len(links)

        # ThreadPoolExecutor párhuzamos feldolgozásra
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Linkek feldolgozása párhuzamosan
            future_to_url = {executor.submit(ProductScraper.scrape_product_data, link): link for link in links}

            # Eredmények feldolgozása, ahogy elkészülnek
            for i, future in enumerate(future_to_url, 1):
                link = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        product_data.append(result)
                    sys.stdout.write(f"\rFeldolgozott linkek: {i}/{total_links}")
                    sys.stdout.flush()
                except Exception as e:
                    print(f"\nHiba történt a következő link feldolgozásakor: {link} - {e}")

        ProductSaver.save(product_data, output_file, file_format=output_format)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Termékadatok kinyerése.")
    parser.add_argument("--sku", type=str, help="Csak az adott SKU-nak megfelelő terméket dolgozza fel.", required=False)
    parser.add_argument("--format", type=str, choices=["tsv", "xlsx"], default="tsv", help="Mentési formátum: 'tsv' vagy 'xlsx'.")
    parser.add_argument("--supplier", type=str, required=True, help="A szállító neve (pl. 'Hikoki').")
    args = parser.parse_args()

    supplier_settings = {
        "Hikoki": {
            "sitemap_url": "https://www.hikoki-powertools.hu/sitemap.xml",
            "product_url_prefix": "https://www.hikoki-powertools.hu/hu/termekek/"
        }
        # Nem így lesz, külön fájlban lesznek tárolva
    }

    if args.supplier not in supplier_settings:
        print(f"Nem támogatott szállító: {args.supplier}")
        sys.exit(1)

    settings = supplier_settings[args.supplier]
    sitemap_reader = SitemapReader(settings["sitemap_url"], settings["product_url_prefix"])
    output_file = fr"{path.base_dir}/web/scrape/{args.supplier.lower()}_products.{args.format}"

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
        print(e)