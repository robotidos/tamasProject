import requests
import certifi
import json

class Swagger:
    def __init__(self, api_url, auth_url, client_id, client_secret, api_key):
        self.api_url = api_url
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.bearer_token = self.get_token()

    def get_token(self):
        """Token beszerzése az autentikációs URL-ről client_credentials alapon."""
        token_url = f"{self.auth_url}/connect/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        print(f"Token kérés folyamatban...\nURL: {token_url}\nAdatok: {data}")
        try:
            # Specifikus tanúsítványlánc használata a certifi könyvtárral
            response = requests.post(token_url, data=data, verify=False)
            print(f"Token kérés státuszkód: {response.status_code}")
            print(f"Token kérés válasz: {response.text}")

            if response.status_code == 200:
                access_token = response.json().get("access_token")
                print("Access Token sikeresen megszerezve!")
                return f"Bearer {access_token}"
            else:
                print("Hiba történt a token lekérésekor!")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Hiba a token kérés során: {e}")
            return None

    def req(self, method, endpoint, params=None, body=None):
        """Általános API kérés."""
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "Authorization": self.bearer_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "api-key": self.api_key
        }

        print(f"Kérés indítása: {method} {url}")
        print(f"Header: {headers}")
        print(f"Params: {params}")
        print(f"Body: {body}")

        try:
            response = requests.request(method, url, headers=headers, params=params, json=body, verify=certifi.where())
            print(f"API kérés státuszkód: {response.status_code}")
            print(f"API válasz: {response.text}")

            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code in [204, 404]:
                print(f"Erőforrás nem található vagy nincs tartalom: {response.status_code}")
                return None
            else:
                print(f"Hiba történt az API hívás során: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"API hiba: {e}")
            return None

    def get(self, endpoint, params=None):
        """GET kérés paraméterekkel."""
        return self.req("GET", endpoint, params=params)

    def post(self, endpoint, body):
        """POST kérés."""
        return self.req("POST", endpoint, body=body)

# Példa használat
if __name__ == "__main__":
    api_url = "https://b2b.toya.pl/api/Multimedia/ProductsList"
    auth_url = "https://b2b.toya.pl/auth"
    client_id = "api_swagger"
    client_secret = "secret"
    api_key = "0464eed0a377d3aa089563e93346c2d7b00f7595e10dc07a3a4b10a103b96cbe"

    api = Swagger(api_url, auth_url, client_id, client_secret, api_key)
    if not api.bearer_token:
        print("Token megszerzése sikertelen! Program leáll.")
        exit()

    print("Token megszerzése sikeres. Folytatás...")

    # Paraméterek a GET kéréshez
    params = {
        "dateFrom": "2024-12-20"
    }

    # GET kérés futtatása
    response = api.get("Multimedia/ProductsList", params=params)
    if response:
        print("API válasz:")
        print(json.dumps(response, indent=4))
    else:
        print("Hiba történt az API hívás során, vagy nincs elérhető adat.")
