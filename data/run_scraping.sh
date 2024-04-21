#!/bin/bash

first_year="${1:-2019}"
last_year="${2:-2025}"
team="${3:-ryunen_busters}"

for year in $(seq $first_year $last_year); do
    echo "Scraping data for year $year"
    python scraping.py --team $team --year $year
done
echo "Scraping completed"

python concat_data.py --team $team --first-year $first_year --last-year $last_year
echo "Data concatenated"