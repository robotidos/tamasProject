from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from login import AdminLogin
from scraper_helper import ScraperHelper
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ModifyProductModel:
    def __init__(self, driver):
        self.driver = driver

    def del_variation_properties(self):
        try:
            # Megkeressük az összes select2-selection elemet
            select_elements = self.driver.find_elements(By.CLASS_NAME, "select2-selection")
            for select in select_elements:
                # Ha az elem szövege tartalmazza a "Csőátmérő [mm] maximum" kifejezést
                if "Csőátmérő [mm] maximum" in select.text:
                    # Keressük meg a hozzá tartozó törlés gombot
                    remove_button = select.find_element(
                        By.XPATH,
                        ".//following::button[contains(@class, 'remove-collection-item')]"
                    )
                    remove_button.click()
                    print("Csőátmérő [mm] maximum törlése megtörtént.")
                    # Rövid várakozás, hogy a törlés végbemenjen
                    time.sleep(10)
                    break  # Csak az első megtalált elemmel dolgozunk
        except Exception as e:
            print("Nem sikerült törölni a Csőátmérő [mm] maximum elemet:", e)

    def add_variation_properties(self):
        """ Bejelentkezik, töröl (ha szükséges) egy meglévő Csőátmérő [mm] maximum tulajdonságot, majd hozzáad egy új variációs tulajdonságot """
        admin_login = AdminLogin(self.driver)
        admin_login.login()

        url = "https://admin.zakanyszerszamhaz.hu/product_model/7725295/edit"
        self.driver.get(url)

        # Először töröljük a meglévő Csőátmérő [mm] maximum tulajdonságot
        self.del_variation_properties()

        # Kattintás az "Hozzáadás" gombra
        ScraperHelper.click_button(self.driver, By.CLASS_NAME, "add-to-collection")
        time.sleep(0.5)

        # Megvárjuk, hogy az új Select2 mező megjelenjen a wrapperen belül
        wait = WebDriverWait(self.driver, 10)
        wrapper = wait.until(EC.presence_of_element_located((By.ID, "productmodel_model_properties_wrapper")))

        # Megkeressük az összes Select2 mezőt a wrapperen belül
        all_selects = wrapper.find_elements(By.CLASS_NAME, "select2-selection")

        # Az új, üres Select2 mező keresése (amelyik tartalmazza a placeholder osztályt)
        new_select = None
        for select in all_selects:
            try:
                select.find_element(By.CLASS_NAME, "select2-selection__placeholder")
                new_select = select
                break
            except Exception:
                continue

        if new_select:
            new_select.click()
            search_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select2-search__field")))
            search_input.send_keys("843721")
            time.sleep(0.5)
            search_input.send_keys(Keys.ENTER)
        else:
            print("Hiba: Nem találtunk új, üres Select2 mezőt!")

        ScraperHelper.click_button(self.driver, By.CSS_SELECTOR, '[data-vat-name="buttonSave"]')
        time.sleep(10)

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        modify_product = ModifyProductModel(driver)
        modify_product.add_variation_properties()
    finally:
        driver.quit()
