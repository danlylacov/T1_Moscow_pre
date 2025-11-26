#!/bin/bash
# Показать историю генерации пайплайнов

cd "$(dirname "$0")/core-service" || exit 1
python3 cli.py list-pipelines

