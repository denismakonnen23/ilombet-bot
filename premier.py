import requests
from datetime import datetime

API_KEY = "TUA_API_KEY"  # substitui pela tua chave real
HEADERS = {"x-apisports-key": API_KEY}

hoje = datetime.now().strftime("%Y-%m-%d")

url = "https://v3.football.api-sports.io/fixtures"
params = {
    "date": hoje,
    "league": 39  # Premier League
}

res = requests.get(url, headers=HEADERS, params=params)
print("Status:", res.status_code)

dados = res.json()

# Visualizar resposta completa
from pprint import pprint
pprint(dados)
