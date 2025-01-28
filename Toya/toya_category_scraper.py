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
        self.input_file = config["pruduct_links_template"].format(supplier=args.supplier, format=args.format)
        self.output_file = config["category_file_template"].format(supplier=args.supplier, format=args.format)
        self.session = ScraperHelper.get_session_with_retries()

    def update_input_file(self, link, category_name):
        """
        Frissíti az input fájlt az adott link kategóriájának nevével.
        :param link: Az URL, amelyhez a kategória tartozik.
        :param category_name: A kategória neve.
        """
        links_df = pd.read_csv(self.input_file, sep="\t")
        if "category" not in links_df.columns:
            links_df["category"] = ""

        links_df.loc[links_df["link"] == link, "category"] = category_name

        # Mentés ProductSaver segítségével
        FileSaver.save(links_df, self.input_file, file_format=self.args.format)

    def scrape_categories(self):
        """
        Kategóriák kinyerése és mentése a megadott fájlba.
        """
        links_df = pd.read_csv(self.input_file, sep="\t")
        if "link" not in links_df.columns:
            raise ValueError("Az input fájl nem tartalmaz 'link' oszlopot.")

        if os.path.exists(self.output_file):
            output_df = pd.read_csv(self.output_file, sep="\t")
        else:
            output_df = pd.DataFrame(columns=["link", "category", "required"])

        base_url = self.config.get("base_url", "")
        save_threshold = 100  # Mentési küszöb
        saved_count = len(output_df)  # Már mentett adatok száma
        new_entries = []

        for link in links_df["link"].unique():
            try:
                response = self.session.get(link, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                max_category_tag = soup.find("li", class_=lambda x: x and "bc-active" in x)
                if max_category_tag:
                    category_name = max_category_tag.find("a", class_="category").text.strip()
                    category_link = max_category_tag.find("a", class_="category")["href"].strip()

                    # A kategória linket mindig egészítsük ki a base_url-lel
                    category_link = urljoin(base_url, category_link)

                    # Input fájl frissítése
                    self.update_input_file(link, category_name)
                    print(link, category_name)

                    # Új adat hozzáadása
                    new_entries.append({
                        "link": category_link,
                        "category": category_name,
                        "required": "Y"
                    })

                    # Adatok mentése mentési küszöb alapján
                    saved_count = FileSaver.save_line(
                        new_entries,  # Új adatok
                        saved_count,  # Eddig mentett adatok száma
                        save_threshold,  # Mentési küszöb
                        self.output_file,  # Fájl elérési útvonal
                        self.args.format  # Fájlformátum
                    )

            except Exception as e:
                print(f"Hiba történt a következő link feldolgozásakor: {link} - {e}")

        # Az utolsó mentés, ha maradtak nem mentett adatok
        if new_entries:
            # Az új adatokat hozzáadjuk az output_df-hez és eltávolítjuk a duplikátumokat
            new_df = pd.DataFrame(new_entries)
            output_df = pd.concat([output_df, new_df], ignore_index=True).drop_duplicates(subset=["link", "category"])
            FileSaver.save(output_df, self.output_file, file_format=self.args.format)
            print(f"Az összes új adat mentve a következő fájlba: {self.output_file}")

if __name__ == "__main__":
    args = ArgumentParser().parse()
    config_loader = ConfigLoader("../config.json")
    config = config_loader.get_supplier_settings(args.supplier, args.format)

    scraper = CategoryScraper(config, args)
    scraper.scrape_categories()
