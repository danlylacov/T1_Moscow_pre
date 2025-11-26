#!/bin/bash
# Определить стек проекта и вывести его в консоль
# Использование: ./analyze-repo.sh --url "https://github.com/user/repo" [--token "token"] [--output stack.json]

cd "$(dirname "$0")/core-service" || exit 1
python3 cli.py analyze-repo "$@"

