import os
import time
import pandas as pd


class FileSaver:
    def __init__(self, output_file):
        """
        :param output_file: Az output fájl elérési útvonala.
        """
        self.output_file = output_file
        # Nem tárolunk flag-et a fejléchez, hanem ellenőrizzük a fájlt (ha már létezik, nem írjuk a fejlécet)

    def _append_record(self, record):
        """
        Soronként hozzáfűzi a rekordot a fájlhoz.
        Ha PermissionError lép fel, exponenciálisan növeli a várakozási időt, amíg az írás sikeres nem lesz.
        """
        retry_count = 0
        delay = 1  # Kezdő késleltetés másodpercben
        while True:
            try:
                # Gondoskodunk róla, hogy a célkönyvtár létezik
                os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
                mode = 'a'
                write_header = False
                if not os.path.exists(self.output_file) or os.stat(self.output_file).st_size == 0:
                    write_header = True
                with open(self.output_file, mode, encoding='utf-8') as f:
                    if write_header:
                        header = '\t'.join(record.keys())
                        f.write(header + '\n')
                    line = '\t'.join(str(record[key]) for key in record.keys())
                    f.write(line + '\n')
                break
            except PermissionError as e:
                print(f"PermissionError: {e}. Várunk {delay} másodpercet, majd újrapróbálkozunk.")
                time.sleep(delay)
                delay *= 2
                retry_count += 1
            except Exception as e:
                print(f"Nem várt hiba a fájlba íráskor: {e}")
                break

    def save_entry(self, record):
        """
        Ment egyetlen rekordot a fájlba.
        """
        self._append_record(record)

    @staticmethod
    def save(data, file_path, file_format="tsv"):
        """
        Egyszeri mentés a megadott formátumban (például a végleges adatokhoz).
        :param data: A mentendő adatokat tartalmazó lista.
        :param file_path: A célfájl elérési útvonala.
        :param file_format: A fájl formátuma ('tsv' vagy 'xlsx').
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df = pd.DataFrame(data)
        if file_format.lower() == "tsv":
            df.to_csv(file_path, sep='\t', index=False, quoting=3, escapechar='\\', doublequote=False)
        elif file_format.lower() == "xlsx":
            df.to_excel(file_path, index=False)
        else:
            raise ValueError("Támogatott formátumok: 'tsv', 'xlsx'")
        print(f"Adatok mentve: {file_path}")
