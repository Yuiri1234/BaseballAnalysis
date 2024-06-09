#!/bin/bash

# リポジトリのディレクトリに移動
cd /home/user/Documents/myproject/BaseballAnalysis

# Git pullを実行
git pull origin main

# dataディレクトリに移動
cd data

# スクレイピングスクリプトを実行
bash run_scraping.sh 2019 2025 ryunen_busters

# リポジトリのルートディレクトリに戻る
cd ..

# Git add、commit、pushを実行
git add .
git commit -m "[ADD] $(date '+%Y-%m-%d') 追加分"
git push origin main
