#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H-%M")

BACKUP="ARUS_backup_$DATE.tar.gz"

echo "================================="
echo " GUARDANDO ARUS"
echo "================================="

tar \
--exclude="__pycache__" \
--exclude=".git" \
--exclude="*.pyc" \
-czf "$BACKUP" .

echo ""
echo "Guardado:"
echo "$BACKUP"

echo ""
echo "Estado:"
find . -maxdepth 2 -type d | sort

echo ""
echo "Python:"
python3 --version

echo ""
echo "FIN"
