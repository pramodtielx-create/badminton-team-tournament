from collections import defaultdict, deque

def analyze_results(results, fixtures):
    team_stats = defaultdict(lambda: {
        "Played": 0, "Won": 0, "Lost": 0,
        "Points": 0,
        "Sets Won": 0, "Sets Lost": 0,
        "Points Won": 0, "Points Lost": 0
    })

    player_stats = defaultdict(lambda: {
        "Team": "",
        "Played": 0, "Won": 0, "Points": 0,
        "Sets Won": 0, "Sets Lost": 0,
        "Points Won": 0, "Points Lost": 0,
        "Form": deque(maxlen=5)
    })

    for tie in results:
        team_a = tie["team_a"]
        team_b = tie["team_b"]
        fixture = next(f for f in fixtures if f["tie_id"] == tie["tie_id"])

        team_a_matches = team_b_matches = 0

        for i, match in enumerate(tie["matches"]):
            pair_a = fixture["matches"][i][0].split("/")
            pair_b = fixture["matches"][i][1].split("/")

            a_sets = b_sets = 0
            a_points = b_points = 0

            for s in match["sets"]:
                a_points += s[0]
                b_points += s[1]
                if s[0] > s[1]:
                    a_sets += 1
                else:
                    b_sets += 1

            a_wins = a_sets > b_sets
            team_a_matches += int(a_wins)
            team_b_matches += int(not a_wins)

            for p in pair_a:
                p = p.strip()
                player_stats[p]["Team"] = team_a
                player_stats[p]["Played"] += 1
                player_stats[p]["Sets Won"] += a_sets
                player_stats[p]["Sets Lost"] += b_sets
                player_stats[p]["Points Won"] += a_points
                player_stats[p]["Points Lost"] += b_points
                player_stats[p]["Form"].append("✅" if a_wins else "❌")
                if a_wins:
                    player_stats[p]["Won"] += 1
                    player_stats[p]["Points"] += 2

            for p in pair_b:
                p = p.strip()
                player_stats[p]["Team"] = team_b
                player_stats[p]["Played"] += 1
                player_stats[p]["Sets Won"] += b_sets
                player_stats[p]["Sets Lost"] += a_sets
                player_stats[p]["Points Won"] += b_points
                player_stats[p]["Points Lost"] += a_points
                player_stats[p]["Form"].append("✅" if not a_wins else "❌")
                if not a_wins:
                    player_stats[p]["Won"] += 1
                    player_stats[p]["Points"] += 2

        winner = team_a if team_a_matches >= 2 else team_b

        team_stats[team_a]["Played"] += 1
        team_stats[team_b]["Played"] += 1
        team_stats[winner]["Won"] += 1
        team_stats[winner]["Points"] += 2

        loser = team_b if winner == team_a else team_a
        team_stats[loser]["Lost"] += 1

    return team_stats, player_stats
``