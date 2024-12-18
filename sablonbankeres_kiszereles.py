from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
from selenium.webdriver.common.by import By

# Fájl beolvasása
df = pd.read_excel(r'C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\web\docs\kiszereles_sku.xlsx')

# Webdriver inicializálása (ChromeDriver)
service = Service()
driver = webdriver.Chrome(service=service)

driver.get("https://admin.zakanyszerszamhaz.hu/")

time.sleep(3)

username_field = driver.find_element(By.ID, 'username')
username_field.send_keys('karalyos.tamas')

password_field = driver.find_element(By.ID, 'password')
password_field.send_keys('Makita12.')

password_field.send_keys(Keys.RETURN)

time.sleep(1)

for i in range(len(df)):
    sku = df.loc[i, 'SKU']
    url = f"https://admin.zakanyszerszamhaz.hu/product/{sku}/specification-template"
    driver.get(url)

    time.sleep(0.3)

    # Az oldal forráskódjának lekérése
    html_source = driver.page_source

    # A Kiszerelés (db) értékének keresése a HTML forráskódban
    kiszereles = 0
    kiszereles_label_index = html_source.find("Kiszerelés (db)")
    if kiszereles_label_index != -1:
        value_start_index = html_source.find('value="', kiszereles_label_index) + len('value="')
        value_end_index = html_source.find('"', value_start_index)
        kiszereles = html_source[value_start_index:value_end_index]
        print(f"{sku}: Kiszerelés (db) = {kiszereles}")

    # A kiszerelés értékének hozzárendelése a "Kiszerelés (db)" oszlopban
    df.loc[i, 'Kiszerelés (db)'] = kiszereles
    # time.sleep(3)
    # df.to_excel('docs/kiszereles.xlsx', index=False)


# Fájl mentése
df.to_excel(r'C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\web\docs\kiszereles.xlsx', index=False)

print('Sikeresen lefutott!')
