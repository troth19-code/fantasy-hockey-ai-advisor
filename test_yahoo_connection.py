
import os
import requests

client_id = os.environ["YAHOO_CLIENT_ID"]
client_secret = os.environ["YAHOO_CLIENT_SECRET"]
refresh_token = os.environ["YAHOO_REFRESH_TOKEN"]

print("Step 1: Authenticating with Yahoo...")

response = requests.post(
    "https://api.login.yahoo.com/oauth2/get_token",
    auth=(client_id, client_secret),
    data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": (
            "https://troth19-code.github.io/"
            "fantasy-hockey-ai-advisor/callback.html"
        ),
    },
    timeout=30,
)

if not response.ok:
    print("Authentication failed.")
    print("HTTP status:", response.status_code)
    raise SystemExit(1)

tokens = response.json()
access_token = tokens["access_token"]

# Never print token values.
print("Authentication successful!")

if tokens.get("refresh_token") and (
    tokens["refresh_token"] != refresh_token
):
    print(
        "WARNING: Yahoo returned a replacement refresh token. "
        "Do not rerun this test until the stored GitHub "
        "secret has been updated."
    )
    raise SystemExit(1)

print("Step 2: Fetching your fantasy hockey teams...")

url = (
    "https://fantasysports.yahooapis.com/fantasy/v2/"
    "users;use_login=1/games;game_keys=nhl/teams"
)

response = requests.get(
    url,
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    },
    params={"format": "json"},
    timeout=30,
)

if not response.ok:
    print("Fantasy API request failed.")
    print("HTTP status:", response.status_code)
    raise SystemExit(1)

data = response.json()

print("Yahoo Fantasy API connection successful!")
print("Response received:", bool(data.get("fantasy_content")))

# Print only team and league identifiers, not
# tokens or the full Yahoo account response.
def show_keys(value):
    if isinstance(value, dict):
        for key in ("team_key", "league_key"):
            if key in value and isinstance(value[key], str):
                print(f"{key}: {value[key]}")
        for child in value.values():
            show_keys(child)
    elif isinstance(value, list):
        for child in value:
            show_keys(child)

show_keys(data.get("fantasy_content", {}))
