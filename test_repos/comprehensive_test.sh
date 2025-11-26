#!/bin/bash
# Комплексный скрипт для тестирования 30+ репозиториев

API_URL="http://localhost:8001/analyze"
RESULTS_DIR="/home/daniil/Рабочий стол/T1/test_repos/results"
mkdir -p "$RESULTS_DIR"

# Список репозиториев для тестирования (30+ репозиториев)
REPOS=(
    # Python проекты
    "https://github.com/pallets/flask"
    "https://github.com/tiangolo/fastapi"
    "https://github.com/django/django"
    "https://github.com/pytest-dev/pytest"
    "https://github.com/psf/requests"
    "https://github.com/pandas-dev/pandas"
    
    # TypeScript/JavaScript проекты
    "https://github.com/expressjs/express"
    "https://github.com/nestjs/nest"
    "https://github.com/facebook/react"
    "https://github.com/vuejs/vue"
    "https://github.com/angular/angular"
    "https://github.com/vercel/next.js"
    "https://github.com/nodejs/node"
    "https://github.com/microsoft/TypeScript"
    
    # Java проекты
    "https://github.com/spring-projects/spring-boot"
    "https://github.com/quarkusio/quarkus"
    "https://github.com/micronaut-projects/micronaut-core"
    "https://github.com/apache/kafka"
    
    # Go проекты
    "https://github.com/gin-gonic/gin"
    "https://github.com/golang/go"
    "https://github.com/kubernetes/kubernetes"
    "https://github.com/docker/docker"
    "https://github.com/etcd-io/etcd"
    
    # Монорепозитории (frontend + backend)
    "https://github.com/microsoft/vscode"
    "https://github.com/facebook/react-native"
    "https://github.com/microsoft/playwright"
    "https://github.com/vercel/turbo"
    "https://github.com/nrwl/nx"
    "https://github.com/lerna/lerna"
    "https://github.com/facebook/jest"
    "https://github.com/microsoft/TypeScript"
    "https://github.com/vercel/next.js"
    "https://github.com/remix-run/remix"
    "https://github.com/sveltejs/svelte"
    "https://github.com/preactjs/preact"
    
    # Дополнительные проекты
    "https://github.com/microsoft/vscode-python"
    "https://github.com/microsoft/TypeScript-React-Starter"
    "https://github.com/angular/angular-cli"
    "https://github.com/facebook/create-react-app"
    "https://github.com/vuejs/vue-cli"
    "https://github.com/nestjs/nest-cli"
    
    # Дополнительные монорепозитории с frontend+backend
    "https://github.com/grafana/grafana"
    "https://github.com/gitpod-io/gitpod"
    "https://github.com/mattermost/mattermost-server"
    "https://github.com/outline/outline"
    "https://github.com/strapi/strapi"
    "https://github.com/medusajs/medusa"
    "https://github.com/appwrite/appwrite"
    "https://github.com/amplication/amplication"
    "https://github.com/novuhq/novu"
    "https://github.com/supabase/supabase"
)

echo "=== Комплексное тестирование API анализатора стека ==="
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
        # Проверяем, что ответ валидный JSON
        if echo "$body" | python3 -m json.tool > /dev/null 2>&1; then
            echo "$body" | python3 -m json.tool > "$result_file"
            
            # Извлекаем ключевую информацию
            languages=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(', '.join(d.get('languages', [])))" 2>/dev/null)
            frameworks=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(', '.join(d.get('frameworks', [])))" 2>/dev/null)
            package_manager=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('package_manager', 'None'))" 2>/dev/null)
            docker=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('docker', False))" 2>/dev/null)
            entry_points=$(echo "$body" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('entry_points', [])))" 2>/dev/null)
            
            echo "✅ Успешно"
            echo "   Languages: ${languages:-None}"
            echo "   Frameworks: ${frameworks:-None}"
            echo "   Package Manager: ${package_manager:-None}"
            echo "   Docker: ${docker}"
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
    sleep 2  # Небольшая задержка между запросами
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

