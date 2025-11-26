#!/bin/bash
# Добавить новый проект и проанализировать его стек
# Использование: ./add-project.sh --name "Project Name" --url "https://github.com/user/repo" [--token "token"]

cd "$(dirname "$0")/core-service" || exit 1
python3 cli.py add-project "$@"

