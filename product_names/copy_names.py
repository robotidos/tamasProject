import pandas as pd
# nem így lesz, átalakítandó!

name_path = r'C:\Users\karalyos.tamas\OneDrive - Zákány Szerszámház Kft\Dokumentumok - Zákány Szerszámház Kft_\ms2\product_names'

def changes(lang):
    generate_path = fr'{name_path}\{lang}\generate.tsv'

    df = pd.read_csv(generate_path, sep='\t', encoding='utf-8', skip_blank_lines=True)

    # Alkalmazzuk a helyettesítéseket
    df['product_name'] = df['product_name'].str.replace(' db', ' buc' if lang == 'ro' else ' db', regex=False)
    df['product_name'] = df['product_name'].str.replace(' 1 db', '', regex=False)
    df['product_name'] = df['product_name'].str.replace(' 1 buc', '' if lang == 'ro' else ' 1 buc', regex=False)
    df['product_name'] = df['product_name'].str.replace('/perc', '/min' if lang == 'ro' else '/perc', regex=False)
    df['product_name'] = df['product_name'].str.replace('Güde', 'Gude' if lang == 'ro' else 'Güde', regex=False)
    df['product_name'] = df['product_name'].str.replace('AVR: Igen', 'AVR', regex=False)
    df['product_name'] = df['product_name'].str.replace('AVR: Da', 'AVR', regex=False)
    df['product_name'] = df['product_name'].str.replace('AVR: Nem', '', regex=False)
    df['product_name'] = df['product_name'].str.replace('AVR: Nu', '', regex=False)
    df['product_name'] = df['product_name'].str.replace('| |', '|', regex=False)
    df['product_name'] = df['product_name'].str.replace('  ', ' ', regex=False)
    df['product_name'] = df['product_name'].str.rstrip(' | ')
    df['product_name'] = df['product_name'].str.replace('<sup>3</sup>', '³', regex=False)
    df['product_name'] = df['product_name'].str.replace('<sup>2</sup>', '²', regex=False)

    df.to_csv(generate_path, sep='\t', index=False, encoding='utf-8')

def ekezetes(filename):
    df = pd.read_csv(filename, sep='\t', encoding='utf-8')

    mask = df['product_name'].str.contains('[áéíóöőúüűÁÉÍÓÖŐÚÜŰ]', regex=True, na=False)
    accented_rows = df[mask]

    if not accented_rows.empty:
        print('Ékezetes betűt tartalmazó sorok:')
        print(accented_rows['product_name'])

def overwrite(lang):
    generate_file = fr'C:\\Users\\karalyos.tamas\\OneDrive - Zákány Szerszámház Kft\\Dokumentumok - Zákány Szerszámház Kft_\\ms2\\product_names\\{lang}\\generate.tsv'
    nevek_file = fr'C:\\Users\\karalyos.tamas\\Documents\\DTWs\\nevek_web_{lang}.csv'

    df = pd.read_csv(generate_file, sep='\\t', encoding='utf-8', engine='python')

    # Kiválasztjuk a szükséges oszlopokat
    nevek_df = df[['z_soid', 'product_name']].rename(columns={
        'z_soid': 'ItemCode',
        'product_name': f'U_TERMEKNEV_{lang.upper()}_WEB'
    })

    # Megnyitjuk a fájlt írásra és kétszer írjuk ki a fejlécet
    with open(nevek_file, 'w', encoding='utf-8-sig', newline='') as f:
        # Első fejléc
        f.write(';'.join(nevek_df.columns) + '\n')
        # Második fejléc és az adatok
        f.write(';'.join(nevek_df.columns) + '\n')
        nevek_df.to_csv(f, sep=';', index=False, header=False, encoding='utf-8-sig')


def main():
    changes('hu')
    changes('ro')
    ekezetes(fr'{name_path}\ro\generate.tsv')
    overwrite('hu')
    overwrite('ro')

if __name__ == '__main__':
    main()
