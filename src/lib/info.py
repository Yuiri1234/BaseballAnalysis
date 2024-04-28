teams_url = "https://teams.one/teams/"

team_dict = {
    "ryunen_busters": "留年バスターズ",
}

column_name = {
    "game": "ID",
    "game_url": "詳細",
    "game_type": "試合種別",
    "game_date": "試合日",
    "game_day": "曜日",
    "game_time": "時間",
    "game_place": "球場",
    "team_name_top": "先攻",
    "team_name_bottom": "後攻",
    "oppo_team": "対戦相手",
    "1_top": "1回表",
    "2_top": "2回表",
    "3_top": "3回表",
    "4_top": "4回表",
    "5_top": "5回表",
    "6_top": "6回表",
    "7_top": "7回表",
    "8_top": "8回表",
    "9_top": "9回表",
    "1_bottom": "1回裏",
    "2_bottom": "2回裏",
    "3_bottom": "3回裏",
    "4_bottom": "4回裏",
    "5_bottom": "5回裏",
    "6_bottom": "6回裏",
    "7_bottom": "7回裏",
    "8_bottom": "8回裏",
    "9_bottom": "9回裏",
    "points_top": "得点(先攻)",
    "points_bottom": "得点(後攻)",
    "points": "得点",
    "losts": "失点",
    "points_diff": "得失点差",
    "result": "結果",
    "1_points": "得点(1回)",
    "2_points": "得点(2回)",
    "3_points": "得点(3回)",
    "4_points": "得点(4回)",
    "5_points": "得点(5回)",
    "6_points": "得点(6回)",
    "7_points": "得点(7回)",
    "8_points": "得点(8回)",
    "9_points": "得点(9回)",
    "1_losts": "失点(1回)",
    "2_losts": "失点(2回)",
    "3_losts": "失点(3回)",
    "4_losts": "失点(4回)",
    "5_losts": "失点(5回)",
    "6_losts": "失点(6回)",
    "7_losts": "失点(7回)",
    "8_losts": "失点(8回)",
    "9_losts": "失点(9回",
}

score_format = {
    "勝率": "{:.3f}",
    "1試合平均得点": "{:.2f}",
    "1試合平均失点": "{:.2f}",
    "1試合平均得失点差": "{:.2f}",
}

batting_format = {
    "勝率": "{:.3f}",
    "打率": "{:.3f}",
    "出塁率": "{:.3f}",
    "長打率": "{:.3f}",
    "OPS": "{:.3f}",
    "IsoP": "{:.3f}",
    "IsoD": "{:.3f}",
    "BABIP": "{:.3f}",
    "wOBA": "{:.3f}",
    "SecA": "{:.3f}",
    "K%": "{:.3f}",
    "BB%": "{:.3f}",
    "BB/K": "{:.3f}",
    "Spd": "{:.3f}",
    "失策率": "{:.3f}",
}

pitching_format = {
    "勝率": "{:.3f}",
    "防御率": "{:.3f}",
    "K/9": "{:.3f}",
    "BB/9": "{:.3f}",
    "K/BB": "{:.3f}",
    "WHIP": "{:.3f}",
    "LOB%": "{:.3f}",
}

display_score_columns = [
    "詳細",
    "試合種別",
    "試合日",
    "曜日",
    "対戦相手",
    "球場",
    "先攻",
    "後攻",
    "得点",
    "失点",
    "得失点差",
    "結果",
]

display_batting_columns = [
    "詳細",
    "選手名",
    "試合種別",
    "試合日",
    "対戦相手",
    "球場",
    "結果",
    "出場",
    "打順",
    "守備",
    "打席",
    "打数",
    "安打",
    "本",
    "打点",
    "得点",
    "盗塁",
    "二塁打",
    "三塁打",
    "三振",
    "四死球",
    "犠打",
    "犠飛",
    "併殺打",
    "敵失",
    "失策",
]

display_pitching_columns = [
    "詳細",
    "選手名",
    "試合種別",
    "試合日",
    "対戦相手",
    "球場",
    "結果",
    "勝敗",
    "投球回",
    "失点",
    "自責点",
    "完投",
    "完封",
    "被安打",
    "被本塁打",
    "奪三振",
    "与四死球",
    "ボーク",
    "暴投",
    "登板順",
]

low_better_score = [
    "負け",
    "合計失点",
    "1試合平均失点",
]

low_better_batting = [
    "三振",
    "K%",
    "併殺打",
    "失策",
    "失策率",
]

low_better_pitching = [
    "負",
    "防御率",
    "失点",
    "自責点",
    "被安打",
    "被本塁打",
    "与四死球",
    "ボーク",
    "暴投",
    "BB/9",
    "WHIP",
]

position_list = [
    "投",
    "捕",
    "一",
    "二",
    "三",
    "遊",
    "左",
    "中",
    "右",
    "DH",
]

batting_metrics = {
    "打率": {
        "説明": None,
        "数式": [
            r"""
        \text{打率} = \frac{\text{安打数}}{\text{打数}}
        """
        ],
    },
    "出塁率": {
        "説明": None,
        "数式": [
            r"""
        \text{出塁率} = \frac{\text{安打数} + \text{四死球数}}{\text{打数} + \text{四死球数} + \text{犠飛数}}
        """
        ],
    },
    "長打率": {
        "説明": None,
        "数式": [
            r"""
        \text{長打率} = \frac{\text{塁打数}}{\text{打数}}
        """
        ],
    },
    "OPS": {
        "説明": None,
        "数式": [
            r"""
        \text{OPS} = \text{出塁率} + \text{長打率}
        """
        ],
    },
    "IsoP": {
        "説明": "純長打率",
        "数式": [
            r"""
        \text{IsoP} = \text{長打率} - \text{打率}
        """
        ],
    },
    "IsoD": {
        "説明": "Isolated Disciplineの略．選球眼（四死球によってどれだけ出塁したか）を表す．",
        "数式": [
            r"""
        \text{IsoD} = \text{出塁率} - \text{打率}
        """
        ],
    },
    "BABIP": {
        "説明": "本塁打を除くインプレー打球のうち安打となった割合を表す．",
        "数式": [
            r"""
        \text{BABIP} = \frac{\text{安打数} - \text{本塁打数}}
                        {\text{打数} - \text{三振数} - \text{本塁打数} + \text{犠飛数}}
        """
        ],
    },
    "wOBA": {
        "説明": "Weighted On-Base Averageの略．１打席当たりの打撃による得点貢献を表す．",
        "数式": [
            r"""
        \text{wOBA} = \frac{0.7 \times \text{四死球数} + 0.9 \times (\text{単打数} + \text{敵失})
        + 1.3 \times (\text{二塁打数} + \text{三塁打数}) + 2.0 \times \text{本塁打数}}
        {\text{打席} + \text{犠打数}}
        """
        ],
    },
    "SecA": {
        "説明": "Secondary Averageの略．長打力と出塁率の高さを表す．",
        "数式": [
            r"""
        \text{SecA} = \frac{\text{総塁打数} - \text{安打数} + \text{四死球数} + \text{盗塁数}}{\text{打数}}
        """
        ],
    },
    "K%": {
        "説明": "三振率",
        "数式": [
            r"""
        \text{K\%} = \frac{\text{三振数}}{\text{打席数}}
        """
        ],
    },
    "BB%": {
        "説明": "四死球率",
        "数式": [
            r"""
        \text{BB\%} = \frac{\text{四死球数}}{\text{打席数}}
        """
        ],
    },
    "BB/K": {
        "説明": "四死球数に対する三振数の割合",
        "数式": [
            r"""
        \text{BB/K} = \frac{\text{四死球数}}{\text{三振数}}
        """
        ],
    },
    "Spd": {
        "説明": "総合走力指標",
        "数式": [
            r"""
        \text{Spd} = \frac{(A + B + C + D)}{4}
        """,
            r"""
        A = 20 \times (\frac{\text{盗塁数} + 3}{\text{盗塁数} + 7} - 0.4)
        """,
            r"""
        B = \frac{1}{0.07} \times \sqrt{\frac{\text{盗塁数}}{\text{単打数} + \text{四死球数}}}
        """,
            r"""
        C = 500 \times \frac{\text{三塁打数}}{\text{打数} - \text{本数} - \text{三振数}}
        """,
            r"""
        D = 25 \times (\frac{\text{得点} - \text{本数}}{\text{安打数} + \text{四死球数} - \text{本数}} - 0.1)
        """,
        ],
    },
    "失策率": {
        "説明": "先発出場した試合あたりにする失策する確率．（本来は守備機会数あたりであるがデータがないため以下の計算で表す．）",
        "数式": [
            r"""
        \text{失策率} = \frac{\text{失策数}}{\text{先発出場試合数}}
        """
        ],
    },
}

pitching_metrics = {
    "防御率": {
        "説明": None,
        "数式": [
            r"""
        \text{防御率} = \frac{7 \times \text{自責点}}{\text{投球回}}
        """
        ],
    },
    "K/9": {
        "説明": "奪三振率",
        "数式": [
            r"""
        \text{K/9} = \frac{9 \times \text{奪三振数}}{\text{投球回}}
        """
        ],
    },
    "BB/9": {
        "説明": "与四死球率",
        "数式": [
            r"""
        \text{BB/9} = \frac{9 \times \text{四死球数}}{\text{投球回}}
        """
        ],
    },
    "K/BB": {
        "説明": "与四死球数に対する奪三振数の割合",
        "数式": [
            r"""
        \text{K/BB} = \frac{\text{奪三振数}}{\text{四死球数}}
        """
        ],
    },
    "WHIP": {
        "説明": "Walks plus Hits per Innings Pitchedの略．1イニングあたりに何人の出塁を許したかを表す．",
        "数式": [
            r"""
        \text{WHIP} = \frac{\text{与四死球数} + \text{被安打数}}{\text{投球回}}
        """
        ],
    },
    "LOB%": {
        "説明": "Left On Base Percentageの略．出塁させた走者の非帰還率．",
        "数式": [
            r"""
        \text{LOB\%} = \frac{\text{被安打数} + \text{与四死球数} - \text{失点数}}
        {\text{被安打数} + \text{与四死球数} - 1.4 \times \text{被本塁打数}}
        """
        ],
    },
}
