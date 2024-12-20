import json
import sys


class ConfigLoader:
    """
    Egy osztály a konfigurációs fájl kezelésére.
    """

    def __init__(self, config_path):
        """
        Inicializálja a ConfigLoader példányt.
        :param config_path: A konfigurációs fájl elérési útvonala.
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """
        Privát metódus a konfigurációs fájl beolvasására.
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            print(f"Hiba: A konfigurációs fájl nem található: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Hiba a konfigurációs fájl beolvasásakor: {e}")
            sys.exit(1)

    def get_supplier_settings(self, supplier, args_format):
        """
        A szállítóhoz tartozó beállításokat adja vissza.
        :param supplier: A szállító neve.
        :param args_format: A fájlformátum az output fájlhoz.
        :return: A szállító beállításai.
        """
        if supplier not in self.config:
            print(f"Nem támogatott szállító: {supplier}")
            sys.exit(1)

        settings = self.config[supplier]
        settings["output_file"] = settings["output_file_template"].format(
            supplier=supplier.lower(),
            format=args_format
        )
        return settings
