import requests
from bs4 import BeautifulSoup

class CategoryScraper:
    @staticmethod
    def generate_category_url(product_url):
        parts = product_url.split("/")
        if len(parts) > 5:
            parts[4] = "termeklista"
            category_url = "/".join(parts[:6])
            return category_url
        return None

    @staticmethod
    def get_category_title(category_url):
        try:
            response = requests.get(category_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            h2_tag = soup.find("h2", class_="a-ttl_h3 a-ttl_border a-ttl_main")
            if h2_tag:
                h2_text = h2_tag.get_text(strip=True)
                if h2_text:
                    return h2_text

            parts = category_url.split("/")
            if len(parts) > 5:
                return parts[5]

            return "Unknown Category"
        except Exception as e:
            print(f"Hiba a kategória betöltésekor: {category_url}: {e}")
            return "Error Loading Category"

    @staticmethod
    def process_product_urls(product_urls):
        result = []
        for url in product_urls:
            category_url = CategoryScraper.generate_category_url(url)
            if category_url:
                category_title = CategoryScraper.get_category_title(category_url)
                result.append({"url": url, "category": category_title})
        return result
