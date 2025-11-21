#!/usr/bin/env bash

# Простой скрипт для тестового запуска генератора CI.
# Запускает генератор с input.json и платформой gitlab,
# результат кладёт в .gitlab-ci.yml в корне проекта.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running CI generator..."
python3 -m generator.main_generator input.json gitlab > .gitlab-ci.yml
echo "Done. Generated .gitlab-ci.yml"


