#!/bin/bash

sed 's/[\?\., ]/\n/g' < gatheredlyrics.txt | tr '[:upper:]' '[:lower:]' | \
sed '/^$/d' >> lyricdict.txt

\rm gatheredlyrics.txt
touch gatheredlyrics.txt
