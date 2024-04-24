## 概要
- [teams](https://teams.one/teams/ryunen_busters)の情報をスクレイピングし，手元のPCに整形されたcsvファイルを作成する．
- 得られたファイルをGitHubレポジトリにPUSHすることで，Streamlit Sharingに反映することが可能．

## 実行方法
### 実行例
```
bash run_scraping.sh 2019 2025 ryunen_busters
```
### 引数
1. 開始年（2019）：スクレイピングを開始する年
2. 終了年（2025）：スクレイピングを終了する年
3. チーム名（ryunen_busters）：teamsに登録しているチームのID．チームホームページのURLの最後に書かれているもの．

## 実行結果
以下のような形で出力される．一番下にある3つのファイル（batting.csv・pitching.csv・score.csv）をGitHubにPUSHすればその情報が反映されるようになる．
```
ryunen_busters/
├── 2019
├── 2020
│   ├── 459441
│   │   ├── batting.csv
│   │   ├── pitching.csv
│   │   └── score.csv
│   ├── 460489
│   │   ├── batting.csv
│   │   ├── pitching.csv
│   │   └── score.csv
├── 2024
│   ├── 781994
│   │   ├── batting.csv
│   │   ├── pitching.csv
│   │   └── score.csv
│   ├── batting.csv
│   ├── pitching.csv
│   └── score.csv
├── 2025
├── batting.csv
├── pitching.csv
└── score.csv
```