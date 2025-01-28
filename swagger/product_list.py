from read_xml import ProductListXMLReader
from swagger import APIClient, DataWriter


class ProductProcessor:
    def __init__(self, xml_path, base_url, client_id, client_secret, output_file="output.tsv"):
        """
        Inicializálja a termékfeldolgozási osztályt.

        :param xml_path: Az XML fájl elérési útja (URL vagy helyi fájl).
        :param base_url: Az API alap URL-je.
        :param client_id: API kliens azonosító.
        :param client_secret: API kliens titkos kulcs.
        :param output_file: Az eredményfájl elérési útja.
        """
        self.xml_reader = ProductListXMLReader(xml_path)
        self.api_client = APIClient(base_url, client_id, client_secret)
        self.data_writer = DataWriter(output_file)

    def process_products(self):
        """
        Termékek feldolgozása: XML beolvasás, API hívások, adatok fájlba írása.
        """
        # Token megszerzése
        token = self.api_client.get_token()
        if not token:
            print("Nem sikerült a token megszerzése, feldolgozás megszakítva.")
            return

        # XML beolvasása
        product_ids = self.xml_reader.read_column("identifier")
        if not product_ids:
            print("Nem talált termékazonosítókat az XML fájlban.")
            return

        # Adatok lekérése és fájlba írása
        for index, product_id in enumerate(product_ids):
            print(f"Feldolgozás megkezdése: Termék ID {product_id}")
            data = self.api_client.get_specification_template(product_id)
            if data:
                append = index > 0  # Az első iterációnál nem írunk hozzá
                self.data_writer.write_grouped_data_to_tsv(product_id, data, append=append)


if __name__ == "__main__":
    # Konfigurációs adatok
    xml_file_path = "https://zakanyszerszamhaz.hu/product_list.xml"
    base_url = "https://admin-api.zakanyszerszamhaz.hu"
    client_id = "155305_69udk0jo1cw088kkc8wgcw4kcgc4ogkgo84oc4okck004cs8c4"
    client_secret = "lfnu4u3x5lsgow0c0w48w4socwwg4o4swwwkgc0k8ccsckc0k"
    output_file = "output.tsv"

    # Processzor inicializálása és futtatása
    processor = ProductProcessor(xml_file_path, base_url, client_id, client_secret, output_file)
    processor.process_products()
