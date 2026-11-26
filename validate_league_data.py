"""Manual validation only. Public CI logs contain fixed status labels, never league data."""
import os
from test_yahoo_connection import authenticate
from yahoo_client import YahooFantasyClient
from league_data import discover, snapshot, keys

def main():
    # Existing authentication helper stops on refresh-token rotation.
    client = YahooFantasyClient(authenticate())
    data = discover(client)
    teams = keys(data, "team_key")
    if not teams:
        raise ValueError("No NHL fantasy teams found")
    selected = os.getenv("YAHOO_TEAM_KEY", "").strip()
    if not selected:
        if len(teams) != 1:
            raise ValueError("Multiple teams found; configure YAHOO_TEAM_KEY as a secret")
        selected = teams[0]
    if selected not in teams:
        raise ValueError("Configured team not found among authenticated teams")
    result = snapshot(client, selected)
    print("League settings: retrieved")
    print("League standings and scoreboard: retrieved")
    print("League teams and rosters: retrieved")
    print("Free agent and waiver statistics: retrieved")
    if not all(result["complete"].values()):
        print("Player pagination incomplete: page cap reached")
        return 1
    print("Player pagination: complete")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # Do not print exceptions: HTTP URLs or response data may contain league IDs.
        print("League data validation failed; inspect privately.")
        raise SystemExit(1) from None
