import csv
import requests
import time
import urllib3
import json

# Letiltjuk az InsecureRequestWarning figyelmeztetéseket
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SKUProcessor:
    def __init__(self, tsv_file, headers=None, timeout=10, max_attempts=5, sleep_between=0.1):
        """
        Inicializálja az SKUProcessor példányt.

        :param tsv_file: A TSV fájl elérési útja.
        :param headers: Az API híváshoz használt fejlécek (szótár formátumban).
        :param timeout: Egy kérésre várható maximális idő (másodpercben).
        :param max_attempts: Maximum próbálkozások száma timeout esetén.
        :param sleep_between: Késleltetés két egymást követő kérés között (másodpercben).
        """
        self.tsv_file = tsv_file
        self.headers = headers or {
            "accept": "application/json",
            "Accept-Language": "en",
            "api-key": "0464eed0a377d3aa089563e93346c2d7b00f7595e10dc07a3a4b10a103b96cbe"
        }
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.sleep_between = sleep_between

    def check_sku(self, sku):
        """
        Lekérdezi az SKU termékadatokat az API-ból.
        Timeout hiba esetén exponenciális backoff-ot alkalmaz, és kiírja a próbálkozások számát.

        :param sku: Az ellenőrizendő SKU.
        :return: A termékadatok (JSON vagy szöveg), ha elérhetők, egyébként None.
        """
        url = f"https://b2b.toya.pl/api/Multimedia/ProductData/{sku}"
        attempt = 1
        wait_time = 1

        while attempt <= self.max_attempts:
            try:
                response = requests.get(url, headers=self.headers, verify=False, timeout=self.timeout)

                # 204-es (No Content) vagy üres válasz esetén nincs adat
                if response.status_code == 204 or not response.text.strip():
                    return None

                try:
                    data = response.json()
                except ValueError:
                    # Ha a válasz nem JSON formátumú, akkor a nyers szöveget adjuk vissza.
                    data = response.text
                return data

            except requests.exceptions.ReadTimeout as e:
                print(f"⏰ Timeout hiba a {sku} SKU esetében, {attempt}. próbálkozás. Várunk {wait_time} másodpercet...")
                time.sleep(wait_time)
                wait_time *= 2  # Várakozási idő duplázása
                attempt += 1
            except requests.exceptions.RequestException as e:
                print(f"❗ Kérés hiba a {sku} SKU esetében: {e}")
                return None

        print(f"❌ Maximum próbálkozások ({self.max_attempts}) a {sku} SKU esetében sikertelenek.")
        return None

    def process_all_skus(self):
        """
        Beolvassa az összes SKU-t a TSV fájlból, majd ellenőrzi őket az API-val.
        Ha az SKU-hoz van adat, kiírja a nameSAP angol nyelvű értékét (ha elérhető), különben a teljes adatot.
        """
        found_skus = []
        total_checked = 0

        with open(self.tsv_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter="\t")

            for row in reader:
                sku = row.get("sku", "").strip()  # Csak az "sku" oszlopot használjuk
                if sku:
                    total_checked += 1
                    data = self.check_sku(sku)

                    if data:
                        print(f"✅ SKU {sku} - VAN adat.")
                        # Ha JSON formátumú adatot kaptunk, próbáljuk meg kiírni a nameSAP["en"] értéket.
                        if (isinstance(data, dict) and "nameSAP" in data and
                                isinstance(data["nameSAP"], dict) and "en" in data["nameSAP"]):
                            print("NameSAP (en):", data["nameSAP"]["en"])
                        else:
                            # Ha nincs nameSAP vagy nem a várt formátumban, akkor a teljes adatot írjuk ki.
                            print(json.dumps(data, indent=2, ensure_ascii=False))
                        found_skus.append(sku)
                    else:
                        print(f"❌ SKU {sku} - NINCS adat.")

                    # Kis késleltetés a két kérés között
                    time.sleep(self.sleep_between)

        print("\n📊 Összesen ellenőrzött SKU:", total_checked)
        if found_skus:
            print("✅ Adattal rendelkező SKU-k:", found_skus)
        else:
            print("NINCS OLYAN SKU, AMIHEZ VAN ADAT!")


if __name__ == "__main__":
    TSV_FILE = r"C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\Árlisták\Listaáras árlisták\2025\Toya\YATO_2025_02_05.tsv"

    processor = SKUProcessor(tsv_file=TSV_FILE)
    processor.process_all_skus()
