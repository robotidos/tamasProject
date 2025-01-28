import csv
import requests
from read_xml import ProductListXMLReader

class APIClient:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.token_url = f"{base_url}/oauth/v2/token"
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def get_token(self):
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        try:
            response = requests.post(self.token_url, data=data)
            if response.status_code == 200:
                print("Token sikeresen megszerezve.")
                self.access_token = response.json().get("access_token")
                return self.access_token
            else:
                print(f"Token kérés hiba: {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Hiba a token kérés során: {e}")
            return None

    def get_specification_template(self, product_id):
        if not self.access_token:
            print("Nincs érvényes hozzáférési token.")
            return None

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.access_token}",
        }
        endpoint = f"{self.base_url}/v1/product/{product_id}/specification-template"
        try:
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Hiba az API hívás során: {response.status_code}: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Kapcsolódási hiba: {e}")
            return None

class DataWriter:
    def __init__(self, file_name="output.tsv"):
        self.file_name = file_name

    def write_grouped_data_to_tsv(self, product_id, data, append=False):
        try:
            mode = "a" if append else "w"
            with open(self.file_name, mode=mode, newline="", encoding="utf-8") as file:
                tsv_writer = csv.writer(file, delimiter="\t")

                # Fejléc írása csak akkor, ha új fájlt hozunk létre
                if not append:
                    tsv_writer.writerow(["Termék ID", "Tulajdonság neve", "Típus", "Érték", "Egység"])

                # Ellenőrzés, hogy van-e 'items' kulcs
                if "items" in data and data["items"]:
                    for item in data["items"]:
                        for group in item.get("groups", []):
                            for prop in group.get("properties", []):
                                prop_name = prop.get("name", "Ismeretlen tulajdonság")
                                prop_type = prop.get("type", "Ismeretlen típus")
                                unit = prop.get("unit", "")

                                # Értékek eltávolítják az egységeket, ha van egység megadva
                                values = ", ".join([
                                    value.get("value", "").replace(f" {unit}", "") if unit else value.get("value", "")
                                    for value in prop.get("values", [])
                                ])

                                # Sor hozzáadása a táblázathoz
                                tsv_writer.writerow([product_id, prop_name, prop_type, values, unit])

                print(f"Adatok sikeresen kiírva a következő fájlba: {self.file_name}")
        except Exception as e:
            print(f"Hiba az adatok fájlba írása során: {e}")
