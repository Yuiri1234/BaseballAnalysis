# BaseballAnalysis
## 概要
- Teamsからスクレイピングしたデータを利用したBIツールの作成
- Teams以上に細かいフィルタリングや分析結果を掲載
- スコアをもとに分析している情報も将来的には取り込む予定

## 環境
### 実行環境
```
Python 3.10.12
```

### requirements.txt
```
beautifulsoup4==4.12.3
requests==2.31.0
streamlit==1.33.0
pandas==2.1.0
numpy==1.25.2
seaborn==0.12.2
streamlit-aggrid==1.0.3.post2
```

## インストール
### レポジトリのクローン
```
git clone https://github.com/Yuiri1234/BaseballAnalysis.git
```
### ライブラリのインストール
```
cd BaseballAnalysis/
pip install -r requirements.txt
```

## 実行方法
### データの取得
```
cd data/
bash run_scraping.sh 2019 2025 ryunen_busters
cd ..
```

### WEBサーバの立ち上げ
```
streamlit run src/app.py
```