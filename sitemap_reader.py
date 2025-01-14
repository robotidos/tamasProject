import requests
import xml.etree.ElementTree as ET

class SitemapReader:
    def __init__(self, sitemap_url, url_prefix):
        """
        Általános Sitemap olvasó, amely képes URL-ek szűrésére egy adott prefix alapján.
        """
        self.sitemap_url = sitemap_url
        self.url_prefix = url_prefix

    def read_sitemap(self):
        """
        Letölti és feldolgozza a sitemap-et, visszaadja a prefixnek megfelelő URL-ek listáját.
        SitemapReader(settings["sitemap_url"], settings["product_url_prefix"])
        config.json a sitemap_url-ból olvassa azt a linket ami a sitemap_url-el kezdődik
        """
        response = requests.get(self.sitemap_url)
        if response.status_code == 200:
            xml_content = response.content
            root = ET.fromstring(xml_content)
            links = []
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            for loc in root.findall('.//ns:loc', namespace):
                url = loc.text
                if url.startswith(self.url_prefix):
                    links.append(url)
            return links
        else:
            raise Exception(f"Hiba történt az XML letöltésekor: {response.status_code}")
