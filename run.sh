#!/bin/bash

FECHA=$(date "+%d/%m/%Y %H:%M")

cd "$(dirname "$0")"

python doretoical.py

if [ $? -ne 0 ]; then
	exit 1
fi

python last.py

if [ $? -ne 0 ]; then
        exit 1
fi

git add ics/* yaml/*
git commit -m "Ejecución $FECHA"
git push origin master

exit 0
