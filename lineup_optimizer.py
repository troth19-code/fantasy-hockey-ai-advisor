
from functools import lru_cache


# Temporary settings based on your Yahoo screenshots.
# We'll replace these with your league's actual settings.
ROSTER_SLOTS = {
    "C": 2,
    "W": 4,
    "D": 4,
    "UTIL": 1,
    "G": 2,
}


def optimize_lineup(players, slots=ROSTER_SLOTS):
    """
    Find the highest-projected lineup for one day.

    Each player is a dictionary:
    {
        "name": "Connor McDavid",
        "positions": ["C"],
        "projected_points": 9.31,
        "has_game": True,
        "available": True
    }

    Returns the starting lineup, bench, and projected points.
    """

    slot_names = [
        slot
        for slot, count in slots.items()
        for _ in range(count)
    ]

    def eligible(player, slot):
        positions = set(player["positions"])

        if slot == "UTIL":
            return bool(positions & {"C", "W"})

        return slot in positions

    @lru_cache(maxsize=None)
    def solve(slot_index, used_mask):
        if slot_index == len(slot_names):
            return 0.0, ()

        # Allow an empty starting slot.
        best_score, best_lineup = solve(
            slot_index + 1, used_mask
        )

        slot = slot_names[slot_index]

        for i, player in enumerate(players):
            if used_mask & (1 << i):
                continue

            if not player.get("has_game", False):
                continue

            if not player.get("available", True):
                continue

            if not eligible(player, slot):
                continue

            score, remaining = solve(
                slot_index + 1,
                used_mask | (1 << i)
            )

            score += player["projected_points"]

            if score > best_score:
                best_score = score
                best_lineup = ((slot, i),) + remaining

        return best_score, best_lineup

    total, selected = solve(0, 0)

    starters = [
        {
            "slot": slot,
            "name": players[i]["name"],
            "projected_points": players[i]["projected_points"],
        }
        for slot, i in selected
    ]

    selected_indices = {i for _, i in selected}

    bench = [
        player["name"]
        for i, player in enumerate(players)
        if i not in selected_indices
    ]

    return {
        "projected_points": round(total, 2),
        "starters": starters,
        "bench": bench,
    }


if __name__ == "__main__":
    # Sample data from your Tuesday Yahoo lineup.
    sample_players = [
        {
            "name": "Connor McDavid",
            "positions": ["C"],
            "projected_points": 9.31,
            "has_game": True,
        },
        {
            "name": "Brayden Point",
            "positions": ["C"],
            "projected_points": 5.67,
            "has_game": True,
        },
        {
            "name": "Jake DeBrusk",
            "positions": ["W"],
            "projected_points": 4.08,
            "has_game": True,
        },
        {
            "name": "Jesper Bratt",
            "positions": ["W"],
            "projected_points": 3.92,
            "has_game": True,
        },
        {
            "name": "Mikko Rantanen",
            "positions": ["W"],
            "projected_points": 5.14,
            "has_game": True,
        },
        {
            "name": "Pavel Zacha",
            "positions": ["C", "W"],
            "projected_points": 4.84,
            "has_game": True,
        },
        {
            "name": "Dougie Hamilton",
            "positions": ["D"],
            "projected_points": 4.21,
            "has_game": True,
        },
        {
            "name": "Miro Heiskanen",
            "positions": ["D"],
            "projected_points": 4.46,
            "has_game": True,
        },
        {
            "name": "Zach Hyman",
            "positions": ["W"],
            "projected_points": 4.33,
            "has_game": True,
        },
        {
            "name": "Mackenzie Blackwood",
            "positions": ["G"],
            "projected_points": 0.23,
            "has_game": True,
        },
        {
            "name": "Jesper Wallstedt",
            "positions": ["G"],
            "projected_points": 6.55,
            "has_game": True,
        },
    ]

    result = optimize_lineup(sample_players)

    print("OPTIMAL LINEUP")
    print("-" * 40)

    for player in result["starters"]:
        print(
            f'{player["slot"]:5} '
            f'{player["name"]:22} '
            f'{player["projected_points"]:.2f}'
        )

    print("-" * 40)
    print(f'TOTAL: {result["projected_points"]:.2f} points')
    print("BENCH:", result["bench"])
