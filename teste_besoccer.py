import requests

API_KEY = "TUA_CHAVE_BESOCCER"  # substitui aqui pela tua chave da API BeSoccer

url = "https://api.besoccerapps.com/scripts/api/api.php"
params = {
    "key": API_KEY,
    "format": "json",
    "req": "matchsday",     # pedidos do tipo "jogos do dia"
    "league": "1",          # exemplo: LaLiga
    "day": "2025-04-01"     # podes trocar pela data de hoje se quiser
}

res = requests.get(url, params=params)
dados = res.json()

# Mostra os jogos no terminal
for jogo in dados.get("matches", []):
    casa = jogo["local"]["name"]
    fora = jogo["visitor"]["name"]
    hora = jogo["hour"]
    print(f"{hora} - {casa} x {fora}")
