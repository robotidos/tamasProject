import os
import pandas as pd
from bs4 import BeautifulSoup
from common_args import ArgumentParser
from config_loader import ConfigLoader
from file_save import FileSaver
from scraper_helper import ScraperHelper
from urllib.parse import urljoin

class CategoryScraper:
    def __init__(self, config, args):
        self.config = config
        self.args = args
        self.input_file = config["product_links_template"].format(
            supplier=args.supplier, l=args.l, format=args.format
        )
        self.output_file = config["category_file_template"].format(
            supplier=args.supplier, l=args.l, format=args.format
        )
        self.session = ScraperHelper.get_session_with_retries()
        # A FileSaver példány a mentési küszöbértékkel (például 20 új bejegyzés után)
        self.file_saver = FileSaver(self.output_file, save_threshold=20)

    def update_input_file(self, link, category_name):
        """
        Frissíti az input fájlt az adott link kategóriájának nevével.
        """
        links_df = pd.read_csv(self.input_file, sep="\t")
        if "category" not in links_df.columns:
            links_df["category"] = ""
        links_df.loc[links_df["link"] == link, "category"] = category_name
        FileSaver.save(links_df, self.input_file, file_format=self.args.format)

    def extract_category_path(self, soup):
        """
        Kinyeri a teljes kategóriaútvonalat és a legmélyebb kategória linkjét.
        """
        breadcrumb_items = soup.select("li[class*='category'] a.category")
        if not breadcrumb_items:
            return None, None  # Ha nincs breadcrumbs, nincs kategória
        breadcrumb_trail = [item.text.strip() for item in breadcrumb_items]
        deepest_category = breadcrumb_items[-1]
        category_link = urljoin(self.config.get("base_url", ""), deepest_category["href"].strip())
        return " > ".join(breadcrumb_trail), category_link

    def add_new_category(self, category_path, category_link, new_entries, existing_categories):
        """
        Ha egy kategória még nem szerepel az adatbázisban, hozzáadja a mentésre váró listához.
        """
        if category_path not in existing_categories:
            new_entries.append({"link": category_link, "category": category_path, "required": "Y"})
            existing_categories.add(category_path)

    def scrape_categories(self):
        """
        Kategóriák kinyerése és egyedi adatok mentése a fájlba.
        """
        links_df = pd.read_csv(self.input_file, sep="\t")
        if "link" not in links_df.columns:
            raise ValueError("Az input fájl nem tartalmaz 'link' oszlopot.")
        if os.path.exists(self.output_file):
            output_df = pd.read_csv(self.output_file, sep="\t")
        else:
            output_df = pd.DataFrame(columns=["link", "category", "required"])
        new_entries = []
        existing_categories = set(output_df["category"])
        for link in links_df["link"].unique():
            try:
                response = self.session.get(link, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                category_path, category_link = self.extract_category_path(soup)
                if category_path and category_link:
                    self.update_input_file(link, category_path)
                    print(f"{category_link} - {category_path}")
                    self.add_new_category(category_path, category_link, new_entries, existing_categories)
                    # Mentés, ha elérte a küszöbértéket
                    output_df = self.file_saver.save_new_entries(new_entries, output_df)
            except Exception as e:
                print(f"Hiba történt a következő link feldolgozásakor: {link} - {e}")
        # Végső mentés, ha maradtak elmentetlen adatok
        self.file_saver.last_save_new_entries(new_entries, output_df)

if __name__ == "__main__":
    args = ArgumentParser().parse()
    config_loader = ConfigLoader("../config.json")
    config = config_loader.get_supplier_settings(args.supplier, args.format)
    scraper = CategoryScraper(config, args)
    scraper.scrape_categories()
