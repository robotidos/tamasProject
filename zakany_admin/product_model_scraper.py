import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from login import AdminLogin
from config_loader import ConfigLoader
from scraper_helper import ScraperHelper

class ProductModelScraper:
    """
    https://admin.zakanyszerszamhaz.hu/product_model/
    Ki szedi: Belső megnevezés, Specifikációs template, Variációképző tulajdonságok
    """
    def __init__(self, config_path="config.json"):
        self.config_loader = ConfigLoader(config_path)
        self.base_url = self.config_loader.config.get("base_url").rstrip("/")
        self.driver = webdriver.Chrome()
        self.data = []

    def scrape_product_model(self):
        try:
            admin_login = AdminLogin(self.driver)
            admin_login.login()

            product_model_url = f"{self.base_url}/product_model/"
            self.driver.get(product_model_url)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            max_page = ScraperHelper.find_max_page(soup, "page-link", "page")

            for page_number in range(1, max_page + 1):
                product_model_url = f"{self.base_url}/product_model/?page={page_number}"
                self.driver.get(product_model_url)
                self.process_page()

            df = pd.DataFrame(self.data)
            df.to_csv("product_models.tsv", sep="\t", index=False)
            print("✅ Az adatok elmentve a 'product_models.tsv' fájlba!")

        finally:
            self.driver.quit()

    def process_page(self):
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        rows = soup.find_all("tr", {"data-groupoperations": True})

        for row in rows:
            link_tag = row.find("a", href=True)
            product_link = link_tag['href'] if link_tag else "N/A"
            product_name = link_tag.text.strip() if link_tag else "N/A"

            specification_name = ScraperHelper.get_table_data(row, 2)
            properties = ScraperHelper.get_table_data(row, 5, multiple=True)

            for property_name in properties:
                self.data.append({
                    "link": product_link,
                    "product_name": product_name,
                    "specification": specification_name,
                    "property": property_name
                })
                print(f"{product_link} | {product_name} | {specification_name} | {property_name}")

if __name__ == "__main__":
    navigator = ProductModelScraper()
    navigator.scrape_product_model()
