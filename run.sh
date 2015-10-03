#!/bin/bash

cd "$(dirname "$0")"

python doretoical.py

if [ $? -ne 0 ]; then
	exit 1
fi

wput -q -nc -u dore.ics ftp://back.host22.com/public_html/

