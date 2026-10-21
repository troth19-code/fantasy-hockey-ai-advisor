
import os
import requests

YAHOO_API_BASE = "https://fantasysports.yahooapis.com/fantasy/v2"


class YahooFantasyClient:
    """Read-only client for the Yahoo Fantasy Sports API."""

    def __init__(self, access_token=None):
        self.access_token = access_token or os.getenv("YAHOO_ACCESS_TOKEN")

    def get(self, endpoint):
        if not self.access_token:
            raise ValueError(
                "Yahoo access token is missing. "
                "API approval and OAuth authentication are required."
            )

        url = f"{YAHOO_API_BASE}/{endpoint.lstrip('/')}"

        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
            },
            params={"format": "json"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_my_teams(self, game_key="nhl"):
        """Retrieve teams belonging to the authenticated Yahoo user."""
        return self.get(f"users;use_login=1/games;game_keys={game_key}/teams")

    def get_league_settings(self, league_key):
        return self.get(f"league/{league_key}/settings")

    def get_roster(self, team_key, date=None):
        endpoint = f"team/{team_key}/roster"
        if date:
            endpoint += f";date={date}"
        return self.get(endpoint)

    def get_matchup(self, team_key, week):
        return self.get(f"team/{team_key}/matchups;weeks={week}")

    def get_free_agents(self, league_key, start=0, count=25):
        endpoint = (
            f"league/{league_key}/players"
            f";status=FA;start={start};count={count}"
        )
        return self.get(endpoint)


if __name__ == "__main__":
    client = YahooFantasyClient()

    if not client.access_token:
        print("Connector created successfully.")
        print("Waiting for Yahoo API credentials.")
    else:
        print(client.get_my_teams())
