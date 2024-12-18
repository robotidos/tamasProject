import csv

name_path = r'C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\ms2\product_names'


def changes(lang):
    generate_path = fr'{name_path}\{lang}\generate.tsv'

    updated_rows = []

    with open(generate_path, 'r', newline='', encoding='utf-8') as generate_file:
        reader = csv.DictReader(generate_file, delimiter='\t')
        fieldnames = reader.fieldnames
        for row in reader:
            product_name = row.get('product_name')

            if lang == 'ro' and ' db' in product_name:
                row['product_name'] = product_name.replace(' db', ' buc')
            if '1 db' in product_name:
                row['product_name'] = product_name.replace(' 1 db', '')
            if lang == 'ro' and '1 buc' in product_name:
                row['product_name'] = product_name.replace(' 1 buc', '')
            if lang == 'ro' and '/perc' in product_name:
                row['product_name'] = product_name.replace('/perc', '/min')
            if lang == 'ro' and 'Güde' in product_name:
                row['product_name'] = product_name.replace('Güde', 'Gude')
            if 'AVR: Igen' in product_name:
                row['product_name'] = product_name.replace('AVR: Igen', 'AVR')
            if 'AVR: Da' in product_name:
                row['product_name'] = product_name.replace('AVR: Da', 'AVR')
            if 'AVR: Nem' in product_name:
                row['product_name'] = product_name.replace('AVR: Nem', '')
            if 'AVR: Nu' in product_name:
                row['product_name'] = product_name.replace('AVR: Nu', '')
            if '| |' in product_name:
                row['product_name'] = product_name.replace('| |', '|')
            if product_name.endswith(' | '):
                row['product_name'] = product_name[:-3]

            updated_rows.append(row)

    with open(generate_path, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(updated_rows)


def ekezetes(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            product_name = row.get('product_name', '')

            if any(char in 'áéíóöőúüűÁÉÍÓÖŐÚÜŰ' for char in product_name):
                print('Ékezetes betűt tartalmaz!:', product_name)


def overwrite(lang):
    generate_file = fr'C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\ms2\product_names\{lang}\generate.tsv'
    nevek_file = fr'C:\Users\karalyos.tamas\Documents\DTWs\nevek_web_{lang}.csv'

    with open(generate_file, 'r', newline='', encoding='utf-8') as generate_csv, open(nevek_file, 'w', newline='', ) as nevek_csv:
        generate_reader = csv.reader(generate_csv, delimiter='\t')
        nevek_writer = csv.writer(nevek_csv, delimiter=';')

        generate_header = next(generate_reader)

        z_soid_index = generate_header.index('z_soid')
        product_name_index = generate_header.index('product_name')

        nevek_writer.writerow(['ItemCode', f'U_TERMEKNEV_{lang.upper()}_WEB'])
        nevek_writer.writerow(['ItemCode', f'U_TERMEKNEV_{lang.upper()}_WEB'])

        for row in generate_reader:
            item_code = row[z_soid_index]
            product_name = row[product_name_index]
            nevek_writer.writerow([item_code, product_name])

def main():
    changes('hu')
    changes('ro')
    ekezetes(fr'{name_path}\ro\generate.tsv')
    overwrite('hu')
    overwrite('ro')


if __name__ == '__main__':
    main()
