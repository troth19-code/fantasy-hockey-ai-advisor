"""Export public DEMO lineup results; never export private Yahoo data here."""
import json
from datetime import datetime, timezone
from pathlib import Path
from lineup_optimizer import optimize_lineup

players = [
    ("Connor McDavid", ["C"], 9.31),
    ("Brayden Point", ["C"], 5.67),
    ("Jake DeBrusk", ["W"], 4.08),
    ("Jesper Bratt", ["W"], 3.92),
    ("Mikko Rantanen", ["W"], 5.14),
    ("Pavel Zacha", ["C", "W"], 4.84),
    ("Dougie Hamilton", ["D"], 4.21),
    ("Miro Heiskanen", ["D"], 4.46),
    ("Zach Hyman", ["W"], 4.33),
    ("Mackenzie Blackwood", ["G"], 0.23),
    ("Jesper Wallstedt", ["G"], 6.55),
]

sample_players = [
    {"name": name, "positions": positions, "projected_points": points,
     "has_game": True, "available": True}
    for name, positions, points in players
]
result = optimize_lineup(sample_players)

# Only Tuesday is populated: other days are intentionally unknown, not zero.
days = [{"day": day, "players": None, "projected_points": None}
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]]
days[1] = {
    "day": "Tue",
    "players": [[p["slot"], p["name"], p["projected_points"]]
                for p in result["starters"]],
    "projected_points": result["projected_points"],
}
payload = {
    "mode": "demo",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "weekly_projected_points": None,
    "acquisitions_remaining": None,
    "days": days,
}
Path("results.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print(f"Wrote results.json; Tuesday sample: {result['projected_points']:.2f} pts")
