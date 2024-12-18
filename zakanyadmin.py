import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import csv
import datetime
import pyautogui
import pandas as pd
import path

programpatch = r'C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\tomi\python'

def adminlogin(driver):

    driver.get("https://admin.zakanyszerszamhaz.hu/")

    time.sleep(1)

    username_field = driver.find_element(By.ID, 'username')
    username_field.send_keys('karalyos.tamas')

    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys('Makita12.')

    password_field.send_keys(Keys.RETURN)

    time.sleep(1)


def add_property(property_name_path, property_type, driver):

    adminlogin(driver)
    driver.get("https://admin.zakanyszerszamhaz.hu/property/new")

    df = pd.read_csv(property_name_path)

    for property_name in df.iloc[0, 0]:

        # Input
        property_name_field = driver.find_element(By.ID, 'property_name')
        property_name_field.send_keys(property_name)

        time.sleep(1)

        # Legördülő
        property_type_dropdown = driver.find_element(By.NAME, 'property[type]')
        select = Select(property_type_dropdown)
        select.select_by_value(property_type)

        time.sleep(1)

        # Létrehozás gomb
        create_button = driver.find_element(By.XPATH, "//button[@data-vat-name='buttonCreate']")
        create_button.click()

        time.sleep(1)

        alert = driver.switch_to.alert
        alert.accept()

        time.sleep(1)

        driver.get("https://admin.zakanyszerszamhaz.hu/property/new")

        time.sleep(1)


def modify_property_name(csv_path):
    driver = webdriver.Chrome()
    adminlogin(driver)
    menu = 'property'

    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')

        for row in csv_reader:
            kod = row[0]
            new_name = row[1]

            # Nyisd meg a tulajdonság szerkesztő oldalt
            urlopen(driver, menu, kod)

            time.sleep(1)

            # Töröld ki az aktuális nevet és írd be az új nevet
            property_name_field = driver.find_element(By.ID, 'property_name')
            property_name_field.clear()
            property_name_field.send_keys(new_name)

            # Kattints a módosítások mentése gombra
            save_button = driver.find_element(By.XPATH, '//button[@data-vat-name="buttonSave"]')
            save_button.click()

            # Várakozás az alertre és elfogadás
            time.sleep(1)
            alert = driver.switch_to.alert
            alert.accept()

    driver.quit()

def urlopen(driver, menu, sku):
    url = f'https://admin.zakanyszerszamhaz.hu/{menu}/{sku}/edit'
    driver.get(url)


def kitoltottseg(xlsx_path, output_path):
    adminlogin(driver)
    start_time = datetime.datetime.now()
    menu = 'product'

    # XLSX beolvasása
    data = pd.read_excel(xlsx_path, engine='openpyxl')

    output_data = {'sku': [], 'hibak': []}

    for index, row in data.iterrows():
        sku = row['sku']
        urlopen(driver, menu, sku)

        elements = driver.find_elements(By.XPATH,
                                        '//ul[@class="list-group"]/li[@class="list-group-item list-group-item-warning"]')

        if elements:
            for element in elements:
                hiba = element.text
                output_data['sku'].append(sku)
                output_data['hibak'].append(hiba)
                print(sku, hiba)
        else:
            print(sku, 'Hibátlan')

    output_df = pd.DataFrame(output_data)
    output_df.to_excel(output_path, index=False, engine='openpyxl')

    driver.quit()

    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print(elapsed_time)


def tulajdonsagertek(tulajdonsag):
    # adminból, sablonból le szedi az adott tulajdonság értékeit
    adminlogin(driver)
    start_time = datetime.datetime.now()

    data = []

    with open('docs/sku.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        num_rows = sum(1 for row in reader)-1
        csvfile.seek(3)
        counter = 1

        for row in reader:
            sku = row['SKU']
            url = f'https://admin.zakanyszerszamhaz.hu/product/{sku}/specification-template'
            driver.get(url)

            html_source = driver.page_source

            soup = BeautifulSoup(html_source, 'html.parser')
            tulajdonsag_label = soup.find('label', class_='control-label',
                                           string=lambda x: x and x.startswith(tulajdonsag))
            tulajdonsag_text = 'üres'

            counter += 1

            if tulajdonsag_label:
                next_span = tulajdonsag_label.find_next('span', title=True)
                if next_span:
                    tulajdonsag_text = next_span.get_text()
                    print(f'{counter}/{num_rows}: {sku}: {tulajdonsag}: {tulajdonsag_text}')

            data.append({'SKU': sku, tulajdonsag: tulajdonsag_text})

    df = pd.DataFrame(data)

    output_file = f'docs/tulajdonsagertekek_{tulajdonsag}.csv'
    df.to_csv(output_file, sep=';', encoding='utf-8', index=False)

    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time
    print(f'Sikeresen lefutott! {elapsed_time}')


def delbuttonclick():
    buttons = driver.find_elements(By.CLASS_NAME, 'remove-collection-item')

    for button in buttons:
        button.click()
        time.sleep(0.5)
        pyautogui.click(x=730, y=290)
        time.sleep(0.5)

    modositasokmentese(driver)


def modositasokmentese(driver):
    save_button = driver.find_element(By.XPATH, '//button[@data-vat-name="buttonSave"]')
    save_button.click()

    time.sleep(1)
    alert = driver.switch_to.alert
    alert.accept()


def delpropvalues(driver, propidpath):
    adminlogin(driver)
    idpcs = 0

    with open(propidpath, newline='') as csv_file:
        csv_reader = csv.reader(csv_file)

        for row in csv_reader:
            propid = row[0]
            driver.get(f'https://admin.zakanyszerszamhaz.hu/property/{propid}/edit')
            idpcs += 1
            delbuttonclick()
            print(idpcs)


def pagecount(url):
    # megszámolja hogy hányat kell lapozni az adott URL-en
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')
    li_itemCount = soup.find('li', class_='itemCount')
    if li_itemCount:
        page_link = li_itemCount.find('a', class_='page-link')
        if page_link:
            ipp, maxitems = map(int, page_link.text.strip().split(' / '))
            pagenumber = (maxitems // ipp) + 1
            print('Oldalak száma:', pagenumber)
            return pagenumber
    return None


def keresosablonok(driver):
    # leszedi a keresősablonokból az URL-eket és a keresősablonok neveit
    adminlogin(driver)
    url = 'https://admin.zakanyszerszamhaz.hu/specification_search_template'
    pagenumber = pagecount(url)
    data = {'url': [], 'sablonnev': []}

    for page in range(1, pagenumber + 1):
        driver.get(f'{url}/?page={page}')
        content = driver.find_element(By.TAG_NAME, 'html').get_attribute('outerHTML')
        soup = BeautifulSoup(content, 'html.parser')
        tr_elements = soup.find_all('tr', class_='')

        for tr in tr_elements:
            link = tr.find('a', href=lambda href: href and "specification_search_template" in href)
            if link:
                text = link.text.strip()
                href = link['href']
                data['url'].append(href)
                data['sablonnev'].append(text)
                print(href, text)

    df = pd.DataFrame(data)
    df.to_csv('keresosablon_url.tsv', sep='\t', index=False)
    driver.quit()


def keresosablon_tulajdonsagok(driver):
    # ki szedi melyik keresősablonban milyen tulajdonságok találhatóak
    # keresosablonok(driver)
    adminlogin(driver)
    keresosablon_df = pd.read_csv('keresosablon_url.tsv', sep='\t')
    data = {'url': [], 'sablonnev': [], 'tulajdonsag': []}

    for url in keresosablon_df['url']:
        driver.get(url)
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        spans = soup.find_all('span',
                              class_="form-control-static fieldValue displayField atField-box_title textType form-control")
        for span in spans:
            data['url'].append(url)
            data['sablonnev'].append(keresosablon_df.loc[keresosablon_df['url'] == url, 'sablonnev'].iloc[0])
            data['tulajdonsag'].append(span.text.strip())
            print(url, span.text.strip())

    result_df = pd.DataFrame(data)
    result_df.to_excel('keresosablonok.xlsx', index=False)
    driver.quit()


def tulajdonsag_sablon(driver):
    adminlogin(driver)
    url = 'https://admin.zakanyszerszamhaz.hu/property_translation'
    pagenumber = pagecount(url)

    data = {'tulajdonsag': [], 'sablonnev': []}

    for page in range(1, pagenumber + 1):
        page_url = f"{url}?page={page}"
        driver.get(page_url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        tr_elements = soup.find_all('tr', class_='')

        for tr in tr_elements:
            td_elements = tr.find_all('td')
            if len(td_elements) >= 1:
                links = tr.find_all('a', href=lambda href: href and 'property_translation' in href)
                sablonnev_elements = td_elements[2].find_all('a')
                for link in links:
                    text = link.text.strip()
                    for sablonnev_element in sablonnev_elements:
                        sablonnev = sablonnev_element.text.strip()
                        data['tulajdonsag'].append(text)
                        data['sablonnev'].append(sablonnev)
                        print(text, sablonnev)

    # Adatok DataFrame létrehozása
    df = pd.DataFrame(data)

    # DataFrame írása Excel-fájlba
    file_name = 'tulajdonsag_sablon.xlsx'
    df.to_excel(file_name, index=False)
    print(f"Az adatok el lettek mentve a '{file_name}' fájlba.")

    driver.quit()





property_name_path = fr'{path.base_dir}\add_property.csv'
csv_path = f'{path.base_dir}\docs\kitoltottseg.xlsx'
output_path = f'{path.base_dir}\docs\kitoltottseghibak.xlsx'
property_type = "multi_value"
tulajdonsagmodosit_csv_path = rf'{path.base_dir}\tulajdonsagmodosit.csv'
propidpath = f'{path.base_dir}\propid.csv'
driver = webdriver.Chrome()



def main():
    kitoltottseg(csv_path, output_path)
    # tulajdonsagertek('Kiszerelés (db)')
    # delpropvalues(driver, propidpath)
    # keresosablon_tulajdonsagok(driver)


if __name__ == "__main__":
    main()
