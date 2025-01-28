import argparse

class ArgumentParser:
    """
    Egy osztály a közös parancssori argumentumok kezelésére.
    """

    def __init__(self):
        """
        Inicializálja az ArgumentParser példányt és definiálja az argumentumokat.
        """
        self.parser = argparse.ArgumentParser(description="Termékadatok kinyerése.")
        self._add_arguments()

    def _add_arguments(self):
        """
        Privát metódus az argumentumok hozzáadásához.
        """
        self.parser.add_argument("--sku", type=str, help="Csak az adott SKU-nak megfelelő terméket dolgozza fel.", required=False)
        self.parser.add_argument("--format", type=str, choices=["tsv", "xlsx"], default="tsv", help="Mentési formátum: 'tsv' vagy 'xlsx'.")
        self.parser.add_argument("--supplier", type=str, help="A szállító neve (pl. 'Hikoki').")
        self.parser.add_argument("--name", type=str)

    def parse(self):
        """
        Az argumentumok értelmezése és visszaadása.
        :return: Az argumentumok értékei.
        """
        return self.parser.parse_args()
