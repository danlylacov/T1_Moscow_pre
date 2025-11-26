#!/bin/bash
# Скрипт для генерации пайплайнов для всех проектов

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/generated-pipelines"
CORE_SERVICE_DIR="$SCRIPT_DIR/core-service"

# Создаем структуру папок
mkdir -p "$OUTPUT_DIR/java"
mkdir -p "$OUTPUT_DIR/go"
mkdir -p "$OUTPUT_DIR/typescript"
mkdir -p "$OUTPUT_DIR/python"

cd "$CORE_SERVICE_DIR" || exit 1

echo "🚀 Начинаем генерацию пайплайнов..."
echo ""

# JAVA проекты
echo "📦 Генерация пайплайнов для JAVA проектов..."
echo ""

echo "  - Keycloak..."
python3 cli.py generate-from-repo \
  --url "https://github.com/keycloak/keycloak" \
  --output "$OUTPUT_DIR/java/keycloak.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Keycloak"

echo "  - Apache Kafka..."
python3 cli.py generate-from-repo \
  --url "https://github.com/apache/kafka" \
  --output "$OUTPUT_DIR/java/kafka.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Kafka"

echo "  - Elasticsearch..."
python3 cli.py generate-from-repo \
  --url "https://github.com/elastic/elasticsearch" \
  --output "$OUTPUT_DIR/java/elasticsearch.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Elasticsearch"

echo "  - Apache Cassandra..."
python3 cli.py generate-from-repo \
  --url "https://github.com/apache/cassandra" \
  --output "$OUTPUT_DIR/java/cassandra.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Cassandra"

echo "  - Jenkins..."
python3 cli.py generate-from-repo \
  --url "https://github.com/jenkinsci/jenkins" \
  --output "$OUTPUT_DIR/java/jenkins.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Jenkins"

echo ""
echo "📦 Генерация пайплайнов для GO проектов..."
echo ""

echo "  - Syncthing..."
python3 cli.py generate-from-repo \
  --url "https://github.com/syncthing/syncthing" \
  --output "$OUTPUT_DIR/go/syncthing.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Syncthing"

echo "  - Gitea..."
python3 cli.py generate-from-repo \
  --url "https://github.com/go-gitea/gitea" \
  --output "$OUTPUT_DIR/go/gitea.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Gitea"

echo "  - Minio..."
python3 cli.py generate-from-repo \
  --url "https://github.com/minio/minio" \
  --output "$OUTPUT_DIR/go/minio.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Minio"

echo "  - Vault..."
python3 cli.py generate-from-repo \
  --url "https://github.com/hashicorp/vault" \
  --output "$OUTPUT_DIR/go/vault.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Vault"

echo "  - Traefik..."
python3 cli.py generate-from-repo \
  --url "https://github.com/traefik/traefik" \
  --output "$OUTPUT_DIR/go/traefik.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Traefik"

echo ""
echo "📦 Генерация пайплайнов для TYPESCRIPT/JAVASCRIPT проектов..."
echo ""

echo "  - Rocket.Chat..."
python3 cli.py generate-from-repo \
  --url "https://github.com/RocketChat/Rocket.Chat" \
  --output "$OUTPUT_DIR/typescript/rocketchat.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Rocket.Chat"

echo "  - Wiki.js..."
python3 cli.py generate-from-repo \
  --url "https://github.com/requarks/wiki" \
  --output "$OUTPUT_DIR/typescript/wikijs.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Wiki.js"

echo "  - Ghost..."
python3 cli.py generate-from-repo \
  --url "https://github.com/TryGhost/Ghost" \
  --output "$OUTPUT_DIR/typescript/ghost.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Ghost"

echo "  - Strapi..."
python3 cli.py generate-from-repo \
  --url "https://github.com/strapi/strapi" \
  --output "$OUTPUT_DIR/typescript/strapi.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Strapi"

echo "  - n8n..."
python3 cli.py generate-from-repo \
  --url "https://github.com/n8n-io/n8n" \
  --output "$OUTPUT_DIR/typescript/n8n.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации n8n"

echo ""
echo "📦 Генерация пайплайнов для PYTHON проектов..."
echo ""

echo "  - Home Assistant..."
python3 cli.py generate-from-repo \
  --url "https://github.com/home-assistant/core" \
  --output "$OUTPUT_DIR/python/homeassistant.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Home Assistant"

echo "  - Mastodon..."
python3 cli.py generate-from-repo \
  --url "https://github.com/mastodon/mastodon" \
  --output "$OUTPUT_DIR/python/mastodon.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Mastodon"

echo "  - Pixelfed..."
python3 cli.py generate-from-repo \
  --url "https://github.com/pixelfed/pixelfed" \
  --output "$OUTPUT_DIR/python/pixelfed.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Pixelfed"

echo "  - Calibre..."
python3 cli.py generate-from-repo \
  --url "https://github.com/kovidgoyal/calibre" \
  --output "$OUTPUT_DIR/python/calibre.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Calibre"

echo "  - Odoo..."
python3 cli.py generate-from-repo \
  --url "https://github.com/odoo/odoo" \
  --output "$OUTPUT_DIR/python/odoo.gitlab-ci.yml" \
  --no-docker-compose || echo "  ⚠️  Ошибка при генерации Odoo"

echo ""
echo "✅ Генерация пайплайнов завершена!"
echo "📁 Пайплайны сохранены в: $OUTPUT_DIR"
echo ""
echo "Структура:"
echo "  - java/ (5 проектов)"
echo "  - go/ (5 проектов)"
echo "  - typescript/ (5 проектов)"
echo "  - python/ (5 проектов)"

