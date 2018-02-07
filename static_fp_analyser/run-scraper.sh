#!/usr/bin/env bash
if [ -z "$1" ]
  then
    echo "Please provide argument: file with URLs to scrape."
    exit 1
    echo "not exited"
fi
while read p; do
  nodejs website-scraper.js $p
done <$1
