import xml.etree.ElementTree as ET
from io import StringIO
import requests

class ProductListXMLReader:
    def __init__(self, file_path):
        """
        A ProductListXMLReader osztály inicializálása egy fájl elérési úttal vagy URL-lel.

        :param file_path: Az XML fájl elérési útja (lehet URL vagy helyi fájl).
        """
        self.file_path = file_path

    def _load_xml(self):
        """
        XML fájl vagy URL beolvasása és elemfává alakítása.

        :return: Az XML fához tartozó ElementTree objektum, vagy None hiba esetén.
        """
        try:
            if self.file_path.startswith("http://") or self.file_path.startswith("https://"):
                response = requests.get(self.file_path)
                response.raise_for_status()  # Hiba kiváltása nem sikeres HTTP státuszkód esetén
                return ET.ElementTree(ET.fromstring(response.text))
            else:
                return ET.parse(self.file_path)  # Helyi fájl feldolgozása
        except requests.exceptions.RequestException as e:
            print(f"Hiba az XML letöltése során: {e}")
            return None
        except ET.ParseError as e:
            print(f"Hiba az XML feldolgozása során: {e}")
            return None

    def read_column(self, element_name):
        """
        Az XML fájlból egy adott elem értékeit olvassa ki.

        :param element_name: Az elem neve, amelynek értékeit keresni kell.
        :return: Az adott elem értékeinek listája, vagy üres lista hiba esetén.
        """
        tree = self._load_xml()
        if not tree:
            print("Nem sikerült betölteni az XML fájlt.")
            return []

        try:
            root = tree.getroot()
            values = [elem.text for product in root.findall("product") for elem in product.iter(element_name)]
            if not values:
                print(f"Nincs '{element_name}' elem az XML fájlban.")
            return values
        except Exception as e:
            print(f"Hiba az oszlop beolvasása során: {e}")
            return []
