import requests
import csv

base_url = "https://admin-api.zakanyszerszamhaz.hu"
endpoint_template = "/v1/product/{id}/specification-template"
token_url = f"{base_url}/oauth/v2/token"
client_id = "155305_69udk0jo1cw088kkc8wgcw4kcgc4ogkgo84oc4okck004cs8c4"
client_secret = "lfnu4u3x5lsgow0c0w48w4socwwg4o4swwwkgc0k8ccsckc0k"

def get_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    try:
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            print("Token sikeresen megszerezve.")
            return response.json().get("access_token")
        else:
            print(f"Token kérés hiba: {response.status_code}")
            print(f"Válasz: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Hiba a token kérés során: {e}")
        return None

def get_specification_template(access_token, product_id):
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {access_token}",
    }
    url = f"{base_url}{endpoint_template.format(id=product_id)}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Sikeres válasz.")
            return response.json()
        else:
            print(f"Hiba az API hívás során: {response.status_code}")
            print(f"Válasz: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Kapcsolódási hiba: {e}")
        return None

def write_to_tsv(data, file_name="output.tsv"):
    try:
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            tsv_writer = csv.writer(file, delimiter="\t")

            # Write headers based on dictionary keys
            if isinstance(data, dict):
                tsv_writer.writerow(data.keys())
                tsv_writer.writerow(data.values())

            # If data is a list of dictionaries, write all rows
            elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
                headers = data[0].keys()
                tsv_writer.writerow(headers)
                for item in data:
                    tsv_writer.writerow(item.values())

            print(f"Adatok sikeresen kiírva a következő fájlba: {file_name}")
    except Exception as e:
        print(f"Hiba az adatok fájlba írása során: {e}")

if __name__ == "__main__":
    token = get_token()
    if token:
        product_id = 103000711  # Példa termék ID
        data = get_specification_template(token, product_id)
        if data:
            write_to_tsv(data)
    else:
        print("Token megszerzése sikertelen, API hívás nem végezhető el.")
