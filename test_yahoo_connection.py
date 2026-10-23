
import os
import requests

# ============================================================
# Yahoo Fantasy API Connection Test
# ============================================================

YAHOO_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"

YAHOO_API_BASE = "https://fantasysports.yahooapis.com/fantasy/v2"

REDIRECT_URI = (
    "https://troth19-code.github.io/"
    "fantasy-hockey-ai-advisor/callback.html"
)


def get_required_secret(name):
    """Read a required credential from GitHub Actions Secrets."""
    value = os.getenv(name, "").strip()

    if not value:
        raise SystemExit(
            f"Missing required GitHub Actions secret: {name}"
        )

    return value


def print_safe_error(response, context):
    """
    Display safe Yahoo error information without printing
    access tokens, refresh tokens, or credentials.
    """
    print(f"\n{context}")
    print("HTTP status:", response.status_code)

    try:
        error_data = response.json()

        if isinstance(error_data, dict):
            error = error_data.get("error", "Unknown")
            description = error_data.get(
                "error_description", "Not provided"
            )

            # Print only recognized error codes, never
            # arbitrary server response text.
            known_errors = {
                "invalid_grant",
                "invalid_client",
                "invalid_request",
                "unauthorized_client",
                "unsupported_grant_type",
                "access_denied",
                "invalid_token",
            }

            if error in known_errors:
                print("Yahoo error:", error)
            else:
                print("Yahoo error: Unrecognized error")

            # Avoid printing potentially sensitive details.
            print(
                "Yahoo description:",
                "Available but hidden for credential safety"
                if description != "Not provided"
                else "Not provided"
            )
        else:
            print("Yahoo returned an unexpected error format.")

    except ValueError:
        print("Yahoo returned a non-JSON error response.")


def authenticate():
    """Exchange the refresh token for an access token."""

    print("Step 1: Checking GitHub credentials...")

    client_id = get_required_secret("YAHOO_CLIENT_ID")
    client_secret = get_required_secret("YAHOO_CLIENT_SECRET")
    refresh_token = get_required_secret("YAHOO_REFRESH_TOKEN")

    print("All three credentials are present.")

    print("\nStep 2: Authenticating with Yahoo...")

    try:
        response = requests.post(
            YAHOO_TOKEN_URL,
            auth=(client_id, client_secret),
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "redirect_uri": REDIRECT_URI,
            },
            timeout=30,
        )
    except requests.RequestException as exc:
        print("Network error contacting Yahoo.")
        print("Error type:", type(exc).__name__)
        raise SystemExit(1)

    if not response.ok:
        print_safe_error(
            response,
            "Yahoo authentication failed."
        )

        print("\nPossible causes:")
        print("- Invalid or expired refresh token")
        print("- Client ID and Client Secret do not match")
        print("- Incorrect redirect URI")
        print("- Yahoo application access not yet activated")

        raise SystemExit(1)

    try:
        tokens = response.json()
        access_token = tokens["access_token"]
    except (ValueError, KeyError, TypeError):
        raise SystemExit(
            "Yahoo returned an unexpected token response."
        )

    print("Authentication successful!")
    print("Access token received: True")

    # Yahoo may return a replacement refresh token.
    new_refresh_token = tokens.get("refresh_token")

    if new_refresh_token and new_refresh_token != refresh_token:
        print(
            "\nWARNING: Yahoo returned a replacement "
            "refresh token."
        )
        print(
            "The existing GitHub secret may need updating."
        )
        print(
            "Do not rerun this workflow until token "
            "rotation is handled securely."
        )

        # Never print the replacement token.
        raise SystemExit(1)

    return access_token


def get_fantasy_teams(access_token):
    """Retrieve the authenticated user's Yahoo fantasy teams."""

    print("\nStep 3: Fetching Yahoo Fantasy hockey teams...")

    url = (
        f"{YAHOO_API_BASE}/"
        "users;use_login=1/games;game_keys=nhl/teams"
    )

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            params={"format": "json"},
            timeout=30,
        )
    except requests.RequestException as exc:
        print("Network error contacting Yahoo Fantasy API.")
        print("Error type:", type(exc).__name__)
        raise SystemExit(1)

    if not response.ok:
        print_safe_error(
            response,
            "Yahoo Fantasy API request failed."
        )

        if response.status_code == 403:
            print(
                "Yahoo Fantasy API permissions may "
                "not yet be activated."
            )

        raise SystemExit(1)

    try:
        data = response.json()
    except ValueError:
        raise SystemExit(
            "Yahoo Fantasy API returned invalid JSON."
        )

    print("\nYahoo Fantasy API connection successful!")
    print(
        "Fantasy data received:",
        bool(data.get("fantasy_content"))
    )

    return data


def show_team_keys(value):
    """
    Print only fantasy team and league identifiers.
    Do not print the full Yahoo API response.
    """
    if isinstance(value, dict):
        for key in ("team_key", "league_key"):
            if key in value and isinstance(value[key], str):
                print(f"{key}: {value[key]}")

        for child in value.values():
            show_team_keys(child)

    elif isinstance(value, list):
        for child in value:
            show_team_keys(child)


def main():
    print("=" * 50)
    print("Yahoo Fantasy Hockey API Connection Test")
    print("=" * 50)

    access_token = authenticate()

    data = get_fantasy_teams(access_token)

    print("\nStep 4: Identifying fantasy teams...")
    show_team_keys(data.get("fantasy_content", {}))

    print("\n" + "=" * 50)
    print("Connection test completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
