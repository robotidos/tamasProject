import base_sets
import os
import pandas as pd
from common_args import ArgumentParser

class TSVCombiner:
    def __init__(self, folder_path, output_folder, output_file):
        self.folder_path = folder_path
        self.output_folder = output_folder
        self.output_file = output_file
        self.header = None

    def combine_files(self):
        # Ellenőrizzük, hogy a mappa létezik-e, ha nem, hozzuk létre
        if not os.path.exists(self.folder_path):
            print(f"A mappa nem létezik, létrehozás: {self.folder_path}")
            os.makedirs(self.folder_path)

        # Ellenőrizzük, hogy az output mappa létezik-e, ha nem, hozzuk létre
        if not os.path.exists(self.output_folder):
            print(f"Az output mappa nem létezik, létrehozás: {self.output_folder}")
            os.makedirs(self.output_folder)

        combined_data = []

        # Mappa bejárása és TSV fájlok feldolgozása
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.tsv'):
                file_path = os.path.join(self.folder_path, filename)
                print(f"Feldolgozás: {file_path}")

                # TSV fájl beolvasása Pandas-szal
                try:
                    df = pd.read_csv(file_path, sep='\t', header=0)

                    # Az első fájl fejlécének beállítása, ha még nincs
                    if self.header is None:
                        self.header = df.columns.tolist()

                    combined_data.append(df)
                except Exception as e:
                    print(f"Hiba a fájl feldolgozása közben: {file_path}\n{e}")

        # Az adatok egyesítése egy DataFrame-be
        if combined_data:
            combined_df = pd.concat(combined_data, ignore_index=True)
            if self.header is not None and len(combined_df.columns) != len(self.header):
                raise ValueError(f"Az oszlopok számának egyeznie kell. Várt: {len(self.header)}, kapott: {len(combined_df.columns)}")

            combined_df.columns = self.header  # Ellenőrizzük, hogy a fejléc egyezzen

            # Az összefűzött adatok mentése TSV fájlba
            combined_df.to_csv(self.output_file, sep='\t', index=False, encoding='utf-8')
            print(f"Az összefűzött fájl sikeresen létrejött: {self.output_file}")
        else:
            print("Nem találhatók feldolgozható TSV fájlok a megadott mappában.")

if __name__ == "__main__":
    # Argumentumok beolvasása
    args = ArgumentParser().parse()
    name = args.name

    # Dinamikus elérési útvonal generálása
    combinate_path = os.path.join(base_sets.MS2_PATH_COMBINATE, f"{name}")
    output_folder = base_sets.MS2_PATH_TMP
    output_file = os.path.join(output_folder, f"{name}.tsv")

    # TSVCombiner példányosítása és futtatása
    combiner = TSVCombiner(combinate_path, output_folder, output_file)
    combiner.combine_files()
