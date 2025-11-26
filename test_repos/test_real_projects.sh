#!/bin/bash
# Скрипт для тестирования реальных проектов (не библиотек)

API_URL="http://localhost:8001/analyze"
RESULTS_DIR="/home/daniil/Рабочий стол/T1/test_repos/results_real_projects"
mkdir -p "$RESULTS_DIR"

# Список реальных проектов
REPOS=(
    # Python проекты
    "https://github.com/mattermost/mattermost-server"
    "https://github.com/outline/outline"
    "https://github.com/supabase/supabase"
    "https://github.com/appwrite/appwrite"
    "https://github.com/amplication/amplication"
    "https://github.com/novuhq/novu"
    "https://github.com/strapi/strapi"
    "https://github.com/medusajs/medusa"
    "https://github.com/calcom/cal.com"
    "https://github.com/n8n-io/n8n"
    
    # TypeScript/JavaScript проекты
    "https://github.com/microsoft/vscode"
    "https://github.com/grafana/grafana"
    "https://github.com/gitpod-io/gitpod"
    "https://github.com/storybookjs/storybook"
    
    # Java проекты
    "https://github.com/elastic/elasticsearch"
    "https://github.com/apache/spark"
    "https://github.com/jenkinsci/jenkins"
    
    # Go проекты
    "https://github.com/prometheus/prometheus"
    
    # Дополнительные реальные проекты
    "https://github.com/calendso/calendso"
    "https://github.com/appsmithorg/appsmith"
    "https://github.com/directus/directus"
    "https://github.com/nocodb/nocodb"
    "https://github.com/hoppscotch/hoppscotch"
    "https://github.com/immich-app/immich"
    "https://github.com/automatisch/automatisch"
    "https://github.com/usememos/memos"
    "https://github.com/answerdev/answer"
)

echo "=== Тестирование реальных проектов ==="
echo "Всего репозиториев: ${#REPOS[@]}"
echo "Результаты сохраняются в: $RESULTS_DIR"
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0
ERRORS=()

for i in "${!REPOS[@]}"; do
    repo="${REPOS[$i]}"
    repo_name=$(basename "$repo" | sed 's/\.git$//')
    result_file="$RESULTS_DIR/${repo_name}.json"
    
    echo "----------------------------------------"
    echo "[$((i+1))/${#REPOS[@]}] Тестирую: $repo"
    echo "----------------------------------------"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"repo_url\": \"$repo\"}" \
        --max-time 300 \
        -w "\n%{http_code}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        if echo "$body" | python3 -m json.tool > /dev/null 2>&1; then
            echo "$body" | python3 -m json.tool > "$result_file"
            
            languages=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(', '.join(d.get('languages', [])))" 2>/dev/null)
            frameworks=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(', '.join(d.get('frameworks', [])))" 2>/dev/null)
            package_manager=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('package_manager', 'None'))" 2>/dev/null)
            docker=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('docker', False))" 2>/dev/null)
            kubernetes=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('kubernetes', False))" 2>/dev/null)
            terraform=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('terraform', False))" 2>/dev/null)
            entry_points=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('entry_points', [])))" 2>/dev/null)
            
            echo "✅ Успешно"
            echo "   Languages: ${languages:-None}"
            echo "   Frameworks: ${frameworks:-None}"
            echo "   Package Manager: ${package_manager:-None}"
            echo "   Docker: ${docker}"
            echo "   Kubernetes: ${kubernetes}"
            echo "   Terraform: ${terraform}"
            echo "   Entry Points: ${entry_points}"
            
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo "❌ Ошибка: Невалидный JSON"
            echo "$body" > "$result_file.error"
            FAIL_COUNT=$((FAIL_COUNT + 1))
            ERRORS+=("$repo: Невалидный JSON")
        fi
    else
        echo "❌ Ошибка HTTP: $http_code"
        echo "$body" > "$result_file.error"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        ERRORS+=("$repo: HTTP $http_code")
    fi
    
    echo ""
    sleep 2
done

echo "========================================"
echo "=== ИТОГИ ТЕСТИРОВАНИЯ ==="
echo "========================================"
echo "Всего репозиториев: ${#REPOS[@]}"
echo "Успешно: $SUCCESS_COUNT"
echo "Ошибок: $FAIL_COUNT"
echo ""

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "Ошибки:"
    for error in "${ERRORS[@]}"; do
        echo "  - $error"
    done
    echo ""
fi

echo "Результаты сохранены в: $RESULTS_DIR"
