import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from config_loader import ConfigLoader
from common_args import ArgumentParser
from file_save import FileSaver  # A fenti osztályt importáljuk
from error_log import ErrorLogger
from scraper_helper import ScraperHelper

class ProductScraper:
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.logger = ErrorLogger()

    def fetch_html(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.logger.add_error(self.url, str(e))
            print(f"Hiba történt a weboldal lekérésekor: {e}")

    def get_image(self):
        if not self.soup:
            return ""
        photos_section = self.soup.find('div', id='photos_nav')
        anchors = (photos_section.find_all('a', class_='photos__link')
                   if photos_section else self.soup.find_all('a', class_='photos__link'))
        return " | ".join(urljoin(self.url, a.get('href')) for a in anchors if a.get('href')) if anchors else ""

    def get_specifications(self):
        if not self.soup:
            return ""
        dictionary_section = self.soup.find('section', id='projector_dictionary')
        if dictionary_section:
            specs = []
            for param in dictionary_section.find_all('div', class_='dictionary__param'):
                name_tag = param.find('span', class_='dictionary__name_txt')
                value_tag = param.find('div', class_='dictionary__values')
                if name_tag and value_tag:
                    value_text = " ".join(v.get_text(" ", strip=True)
                                          for v in value_tag.find_all(['span', 'a']))
                    cleaned_value = ScraperHelper.clean_html_content(value_text)
                    specs.append(f"{name_tag.text.strip()}: {cleaned_value}")
            return " | ".join(specs)
        return ""

    def get_description(self):
        if not self.soup:
            return ""
        description_section = self.soup.find('section', id='projector_longdescription')
        if description_section:
            for img in description_section.find_all('img'):
                img.decompose()
            raw_content = " ".join(description_section.decode_contents().split())
            return ScraperHelper.clean_html_content(raw_content)
        return ""

    def parse_product_data(self):
        if not self.soup:
            return None
        product_section = self.soup.find('section', id='projector_productname')
        if not product_section:
            print(f"Nem található a termékadatokat tartalmazó szekció: {self.url}")
            return None

        product_names = product_section.find_all('h1', class_='product_name__name')
        if len(product_names) < 2:
            print(f"Nem sikerült az adatok megfelelő kinyerése: {self.url}")
            return None

        return {
            'sku': product_names[0].text.strip(),
            'url': self.url,
            'category': "",
            'product_name': product_names[1].text.strip(),
            'image_urls': self.get_image(),
            'specifications': self.get_specifications(),
            'description': self.get_description(),
        }

    @staticmethod
    def read_links(input_file):
        try:
            return pd.read_csv(input_file, delimiter='\t', encoding='utf-8')
        except Exception as e:
            print(f"Hiba történt a TSV fájl beolvasása közben: {e}")
            return pd.DataFrame()

    @staticmethod
    def search_category(products, df_input):
        df_output = pd.DataFrame(products)
        if 'category' in df_output.columns:
            df_output = df_output.drop(columns=['category'])
        if not df_input.empty:
            merged_df = pd.merge(df_output, df_input[["link", "category"]],
                                 left_on="url", right_on="link", how="left")
            merged_df.drop(columns=["link"], inplace=True)
            return merged_df
        return df_output

def process_single_url(url, products, file_saver):
    print(f"Feldolgozás alatt: {url}")
    scraper = ProductScraper(url)
    scraper.fetch_html()
    product_data = scraper.parse_product_data()
    if product_data:
        products.append(product_data)
        file_saver.save_entry(product_data)  # Azonnali mentés soronként
    else:
        print(f"Nem sikerült kinyerni az adatokat a következő URL-ről: {url}")

def process_products(args, settings):
    products = []
    input_file = settings["product_links_template"].format(
        supplier=args.supplier.lower(),
        l=args.l,
        format=args.format
    )
    df_input = ProductScraper.read_links(input_file)
    file_saver = FileSaver(settings["output_file"])  # Egyetlen példány, melyet végig használsz
    if args.link:
        print(f"Csak az alábbi link kerül feldolgozásra: {args.link}")
        process_single_url(args.link, products, file_saver)
    else:
        print(f"Input file: {input_file}")
        for _, row in df_input.iterrows():
            url = row.get("link", "")
            if not url:
                continue
            process_single_url(url, products, file_saver)
    return products, df_input, file_saver

def main():
    args = ArgumentParser().parse()
    config_loader = ConfigLoader("../config.json")
    settings = config_loader.get_supplier_settings(args.supplier, args.format)
    products, df_input, file_saver = process_products(args, settings)
    final_output = ProductScraper.search_category(products, df_input)
    print(f"Output file: {settings['output_file']}")
    # Ha a végleges outputot újra szeretnéd menteni (pl. a kategóriák hozzáadásával), azt itt teheted meg:
    FileSaver.save(final_output.to_dict(orient="records"), settings["output_file"], file_format=args.format)

if __name__ == "__main__":
    main()
