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


def calc_points_diff(row, team):
    if row["team_name_top"] == team:
        return row["points_top"] - row["points_bottom"]
    else:
        return row["points_bottom"] - row["points_top"]


def calc_points_losts(row, team):
    if row["team_name_top"] == team:
        return row["points_top"], row["points_bottom"]
    else:
        return row["points_bottom"], row["points_top"]


def calc_inning_points(row, team):
    tmp_row = row.copy()
    if tmp_row["team_name_top"] == team:
        for i in range(1, 10):
            tmp_row.rename({f"{i}_top": f"{i}_points"}, inplace=True)
    else:
        for i in range(1, 10):
            tmp_row.rename({f"{i}_bottom": f"{i}_points"}, inplace=True)
    return tmp_row[[f"{i}_points" for i in range(1, 10)]]


def calc_inning_losts(row, team):
    tmp_row = row.copy()
    if row["team_name_top"] == team:
        for i in range(1, 10):
            tmp_row.rename({f"{i}_bottom": f"{i}_losts"}, inplace=True)
    else:
        for i in range(1, 10):
            tmp_row.rename({f"{i}_top": f"{i}_losts"}, inplace=True)
    return tmp_row[[f"{i}_losts" for i in range(1, 10)]]
