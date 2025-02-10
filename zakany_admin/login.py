import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config_loader import ConfigLoader  # Betöltjük a config loadert

# Betöltjük a konfigurációt a config.json-ból
config = ConfigLoader("config.json")

class AdminLogin:
    def __init__(self, driver):
        self.driver = driver
        self.username = os.getenv("VIRGO_ADMIN_USERNAME")
        self.password = os.getenv("VIRGO_ADMIN_PASSWORD")
        self.url = config.config.get("base_url")  # URL betöltése a config.json-ból

    def login(self):
        self.driver.get(self.url)
        time.sleep(1)

        username_field = self.driver.find_element(By.ID, 'username')
        username_field.send_keys(self.username)

        password_field = self.driver.find_element(By.ID, 'password')
        password_field.send_keys(self.password)

        password_field.send_keys(Keys.RETURN)

        time.sleep(1)

