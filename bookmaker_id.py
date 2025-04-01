url = "https://v3.football.api-sports.io/odds"
params = {
    "bookmaker": 8,  # ID da Betclic (se disponível)
    "market": "over_under",
    "bet": "Over 2.5",
    "date": "2025-04-01"
}
res = requests.get(url, headers=headers, params=params)
