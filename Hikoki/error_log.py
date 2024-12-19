class ErrorLogger:
    def __init__(self):
        self.error_links = {}
        self.retry_count = {}

    def add_error(self, link, error):
        """
        Hibás link hozzáadása a szótárhoz
        """
        self.error_links[link] = error
        if link not in self.retry_count:
            self.retry_count[link] = 0

    def increment_retry(self, link):
        """
        Újrapróbálkozás számának növelése
        """
        if link in self.retry_count:
            self.retry_count[link] += 1

    def can_retry(self, link, max_retries=3):
        """
        Ellenőrzés, hogy a link újrapróbálható-e
        """
        return self.retry_count.get(link, 0) < max_retries

    def get_error_links(self):
        """
        Hibás linkek visszaadása
        """
        return list(self.error_links.keys())

    def clear_errors(self):
        """
        Hibás linkek törlése
        """
        self.error_links.clear()
        self.retry_count.clear()

    def log_errors(self, log_file="data/failed_links.log"):
        """
        Hibás linkek mentése egy log fájlba
        """
        with open(log_file, "w") as file:
            for link, error in self.error_links.items():
                file.write(f"{link} - {error}\n")
