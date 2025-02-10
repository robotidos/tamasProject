config = {
    "filter": [
        {"BRAND": ['YATO', 'VOREL']},
        # {"SELL-OUT": '!SELL-OUT'},
    ],
    "exclude_rows": ["0-7"],
    "exclude_coulumn": ["Unnamed: 0",
                        "CURRENT PRICE",
                        "CURRENT GROUP",
                        "NEW GROUP",
                        "NEW PRICE",
                        "DIFF. IN FINAL PR.",
                        "COO",
                        "FINAL PRICE",
                        "VALID FROM"],
    "output_header": [{"ITEM NO.": "sku"},
                      {"DESCRIPTION EN": "name"}],
    "folder": r"C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\Árlisták\Listaáras árlisták\2025\Toya",
    "input_fn": 'TOYA SA FCA MLOCHOW EU EUR price list 01.01.2025.xlsx',
    "output_fn": 'YATO_{date}.tsv'
}