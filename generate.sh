#!/bin/bash
# Сгенерировать CI/CD пайплайн для проекта
# Использование: ./generate.sh --project-id 1 [--output .gitlab-ci.yml] [--platform gitlab] [--stages "lint,test,build"]

cd "$(dirname "$0")/core-service" || exit 1
python3 cli.py generate "$@"

