"""Read-only Yahoo league retrieval. Never log raw responses or persist data here."""
import re
from yahoo_client import YahooFantasyClient

def values(node, key):
    if isinstance(node, dict):
        if key in node:
            yield node[key]
        for value in node.values():
            yield from values(value, key)
    elif isinstance(node, list):
        for value in node:
            yield from values(value, key)

def keys(node, key):
    return sorted({v for v in values(node, key) if isinstance(v, str)})

def get(client, endpoint):
    result = client.get(endpoint)
    if not isinstance(result, dict) or not result.get("fantasy_content"):
        raise ValueError("Missing fantasy_content")
    return result["fantasy_content"]

def discover(client):
    return get(client, "users;use_login=1/games;game_keys=nhl/teams")

def snapshot(client, team_key, max_player_pages=100):
    if not re.fullmatch(r"\d+\.l\.\d+\.t\.\d+", team_key):
        raise ValueError("Invalid team key")
    league = team_key.rsplit(".t.", 1)[0]
    settings = get(client, f"league/{league}/settings")
    standings = get(client, f"league/{league}/standings")
    scoreboard = get(client, f"league/{league}/scoreboard")
    teams = get(client, f"league/{league}/teams")
    team_keys = keys(teams, "team_key")
    if team_key not in team_keys:
        raise ValueError("Selected team missing from league")
    rosters = {t: get(client, f"team/{t}/roster") for t in team_keys}
    players = {}
    complete = {}
    for status in ("FA", "W"):
        pages = []
        seen = set()
        complete[status] = False
        for page in range(max_player_pages):
            data = get(client, f"league/{league}/players;status={status};start={page*25};count=25/stats")
            current = set(keys(data, "player_key"))
            if current & seen:
                raise ValueError("Overlapping player pages")
            pages.append(data)
            seen.update(current)
            if len(current) < 25:
                complete[status] = True
                break
        players[status] = pages
    return {"settings": settings, "standings": standings, "scoreboard": scoreboard,
            "teams": teams, "rosters": rosters, "players": players,
            "complete": complete, "team_key": team_key}
