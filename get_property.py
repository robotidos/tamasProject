import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

"""
Leszedi az összes létező tulajdonság értéket.
"""


# Admin bejelentkezés
def adminlogin(driver):
    driver.get("https://admin.zakanyszerszamhaz.hu/")
    time.sleep(1)

    username_field = driver.find_element(By.ID, 'username')
    username_field.send_keys('karalyos.tamas')

    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys('Makita12.')

    password_field.send_keys(Keys.RETURN)
    time.sleep(2)


# Összes oldal meghatározása. Hány oldalt kell lapozni.
def get_total_pages(driver):
    driver.get("https://admin.zakanyszerszamhaz.hu/property/?page=1")
    time.sleep(0.5)
    last_page_link = driver.find_element(By.CSS_SELECTOR, '.pagination .last.page-item a')
    last_page_number = int(last_page_link.get_attribute('href').split('=')[-1])
    return last_page_number


# Adatok kigyűjtése egy oldalról
def scrape_page(driver):
    data = []
    rows = driver.find_elements(By.CSS_SELECTOR, "tr")

    for row in rows:
        try:
            identifier = row.find_element(By.CSS_SELECTOR, 'td:nth-child(2)').text
            property_name = row.find_element(By.CSS_SELECTOR, 'td:nth-child(3)').text
            data_type = row.find_element(By.CSS_SELECTOR, 'td:nth-child(4)').text
            unit = row.find_element(By.CSS_SELECTOR, 'td:nth-child(5)').text.strip()
            data.append((identifier, property_name, data_type, unit))
        except:
            continue  # Ha egy sorban hibát találunk, egyszerűen átlépjük
    return data


# Lapozás és adatok mentése
def scrape_all_pages(driver, total_pages, output_file):
    all_data = []

    for page in range(1, total_pages + 1):
        driver.get(f"https://admin.zakanyszerszamhaz.hu/property/?page={page}")
        print(f"Scraping page: {page}")
        all_data.extend(scrape_page(driver))

    # Mentés TSV fájlba
    with open(output_file, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(["Azonosító", "Tulajdonság neve", "Típus", "Mértékegység"])
        writer.writerows(all_data)


if __name__ == "__main__":
    output_file = r"C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\tomi\python\property\propery.tsv"

    driver = webdriver.Chrome()
    try:
        adminlogin(driver)
        total_pages = get_total_pages(driver)
        print(f"Total pages: {total_pages}")
        scrape_all_pages(driver, total_pages, output_file)
        print(f"Data saved to {output_file}")
    finally:
        driver.quit()
