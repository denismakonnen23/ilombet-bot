import requests

API_KEY = "177074678f6469c26f1b885a5a0fb0a6"  # <- substitui pela tua chave real da API-Football

url = "https://v3.football.api-sports.io/odds/bookmakers"
headers = {"x-apisports-key": API_KEY}

res = requests.get(url, headers=headers)

print("Status:", res.status_code)
print("Resposta JSON:", res.json())  # <- Para debug

bookmakers = res.json()["response"]

for bm in bookmakers:
    print(f"{bm['id']} - {bm['name']}")
