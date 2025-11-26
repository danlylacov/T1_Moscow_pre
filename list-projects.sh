#!/bin/bash
# Показать список всех проектов

cd "$(dirname "$0")/core-service" || exit 1
python3 cli.py list-projects

