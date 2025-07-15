#!/bin/bash

curl 'https://game.walruslife.com/send-score?score=999999999' \
  -H 'accept: */*' \
  -H 'accept-language: en-US,en;q=0.9,ru;q=0.8' \
  -H 'dnt: 1' \
  -H 'priority: u=1, i' \
  -H 'referer: https://game.walruslife.com/' \
  -H 'sec-ch-ua: "Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'