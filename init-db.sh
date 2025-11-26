#!/bin/bash
# Инициализация базы данных

cd "$(dirname "$0")/core-service" || exit 1
python3 cli.py init

