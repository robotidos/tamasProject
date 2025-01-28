import os
import pandas as pd


class FileSaver:
    @staticmethod
    def save(data, file_path, file_format="tsv"):
        """
        Adatok mentése a megadott formátumban.
        :param data: A mentendő adatokat tartalmazó lista.
        :param file_path: A célfájl elérési útvonala.
        :param file_format: A fájl formátuma ('tsv' vagy 'xlsx').
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        df = pd.DataFrame(data)
        if file_format == "tsv":
            df.to_csv(file_path, sep='\t', index=False, quoting=3, escapechar='\\', doublequote=False)
        elif file_format == "xlsx":
            df.to_excel(file_path, index=False)
        else:
            raise ValueError("Támogatott formátumok: 'tsv', 'xlsx'")

    @staticmethod
    def save_line(data, saved_count, save_threshold, file_path, file_format):
        """
        Ha egyszerre sok adatot aakrunk menteni a fájlba
        Általánosított mentési metódus, amely bármilyen adatot ment, ha elértük a küszöbértéket.
        :param data: Az adat, amit menteni kell. Lehet lista, szótár, stb.
        :param saved_count: Az eddig mentett adatok száma.
        :param save_threshold: Az a küszöb, amikor az adatokat menteni kell.
        :param file_path: A célfájl elérési útvonala.
        :param file_format: A fájl formátuma ('tsv' vagy 'xlsx').
        """
        if len(data) - saved_count >= save_threshold:
            FileSaver.save(data, file_path, file_format)
            saved_count = len(data)
            print(f"{saved_count} adat mentve")
        return saved_count
