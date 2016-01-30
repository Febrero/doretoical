#!/bin/bash

cd "$(dirname "$0")"

python doretoical.py

if [ $? -ne 0 ]; then
	exit 1
fi

python last.py

if [ $? -ne 0 ]; then
        exit 1
fi

exit 0
