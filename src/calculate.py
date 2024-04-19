def win_or_lose(row, team):
    if row["team_name_top"] == team:
        if row["points_top"] > row["points_bottom"]:
            return "○"
        elif row["points_top"] < row["points_bottom"]:
            return "☓"
        else:
            return "△"
    else:
        if row["points_top"] < row["points_bottom"]:
            return "○"
        elif row["points_top"] > row["points_bottom"]:
            return "☓"
        else:
            return "△"


def calc_goal_diff(row, team):
    if row["team_name_top"] == team:
        return row["points_top"] - row["points_bottom"]
    else:
        return row["points_bottom"] - row["points_top"]


def calc_points_losts(row, team):
    if row["team_name_top"] == team:
        return row["points_top"], row["points_bottom"]
    else:
        return row["points_bottom"], row["points_top"]