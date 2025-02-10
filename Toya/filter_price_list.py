import os
import pandas as pd
import datetime
import config_xlsx


class PriceFilter:
    def __init__(self):
        self.config = config_xlsx.config
        self.input_path = os.path.join(self.config["folder"], self.config["input_fn"])
        current_date = datetime.datetime.now().strftime("%Y_%m_%d")
        output_fn_template = self.config.get("output_fn", "YATO_{date}.tsv")
        self.output_fn = output_fn_template.format(date=current_date)
        self.output_path = os.path.join(self.config["folder"], self.output_fn)
        self.df = None

    def compute_skip_and_post_drop_rows(self):
        skip_rows = set()
        post_drop_rows = set()
        for item in self.config["exclude_rows"]:
            if isinstance(item, str) and '-' in item:
                start_str, end_str = item.split('-')
                start = int(start_str)
                end = int(end_str)
                skip_rows.update(range(start, end + 1))
            elif isinstance(item, int):
                post_drop_rows.add(item)
        return sorted(skip_rows), post_drop_rows

    def load_data(self):
        skip_rows, post_drop_rows = self.compute_skip_and_post_drop_rows()
        # Ha az output_header mapping tartalmazza az "ITEM NO." oszlopot,
        # akkor azt szövegként olvassuk be, így megmaradnak a vezető 0-k.
        converters = {}
        if "output_header" in self.config:
            for mapping in self.config["output_header"]:
                for original, new in mapping.items():
                    if original == "ITEM NO.":
                        converters[original] = str

        self.df = pd.read_excel(self.input_path, skiprows=skip_rows, converters=converters)
        self.df.columns = self.df.columns.str.replace("\n", " ").str.strip()
        print("A beolvasott oszlopok:", self.df.columns.tolist())
        if post_drop_rows:
            self.df = self.df.drop(self.df.index[list(post_drop_rows)], errors='ignore')

    def apply_filter(self):
        for condition in self.config["filter"]:
            for col, cond_value in condition.items():
                if col not in self.df.columns:
                    print(f"A '{col}' oszlop nem található a fájlban, ezért a szűrés kimarad.")
                    continue
                is_str = self.df[col].dtype == object
                if isinstance(cond_value, list):
                    if is_str:
                        allowed = [str(x).upper() for x in cond_value]
                        mask = self.df[col].str.upper().isin(allowed)
                    else:
                        mask = self.df[col].isin(cond_value)
                elif isinstance(cond_value, str):
                    if cond_value.startswith('!'):
                        value = cond_value[1:]
                        mask = self.df[col].str.upper() != value.upper() if is_str else self.df[col] != value
                    else:
                        mask = self.df[col].str.upper() == cond_value.upper() if is_str else self.df[col] == cond_value
                else:
                    mask = self.df[col] == cond_value
                self.df = self.df[mask]

    def apply_output_modifications(self):
        # Átnevezés az output_header alapján
        if "output_header" in self.config:
            rename_map = {}
            for mapping in self.config["output_header"]:
                for original, new in mapping.items():
                    rename_map[original] = new
            self.df = self.df.rename(columns=rename_map)

        # Az átalakítás után az "ITEM NO." oszlop már "sku" néven szerepel,
        # így biztosítjuk, hogy szövegként legyen kezelve, és ne történjen numerikus konverzió.
        if "sku" in self.df.columns:
            self.df["sku"] = self.df["sku"].astype(str)

        # Oszlopok kizárása az exclude_coulumn lista alapján
        if "exclude_coulumn" in self.config:
            exclude_list = self.config["exclude_coulumn"]
            self.df = self.df.drop(columns=[col for col in exclude_list if col in self.df.columns], errors='ignore')

    def save_data(self):
        self.df.to_csv(self.output_path, sep='\t', index=False)
        print("A szűrt táblázat elmentve:", self.output_path)

    def process(self):
        self.load_data()
        self.apply_filter()
        self.apply_output_modifications()
        self.save_data()


if __name__ == '__main__':
    pf = PriceFilter()
    pf.process()
