#!/bin/bash
# Сгенерировать CI/CD пайплайн напрямую из репозитория со всеми возможными стадиями
# Использование: ./generate-from-repo.sh --url "https://github.com/user/repo" [--token "token"] [--output .gitlab-ci.yml] [--platform gitlab] [--stack-output stack.json]

cd "$(dirname "$0")/core-service" || exit 1
python3 cli.py generate-from-repo "$@"

