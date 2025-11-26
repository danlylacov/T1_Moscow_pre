#!/bin/bash
# Скрипт для тестирования API на разных репозиториях

API_URL="http://localhost:8000/analyze"
REPOS=(
    "https://github.com/tiangolo/fastapi"
    "https://github.com/pallets/flask"
    "https://github.com/expressjs/express"
    "https://github.com/spring-projects/spring-boot"
    "https://github.com/gin-gonic/gin"
)

echo "=== Тестирование API анализатора стека ==="
echo ""

for repo in "${REPOS[@]}"; do
    echo "----------------------------------------"
    echo "Тестирую: $repo"
    echo "----------------------------------------"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"repo_url\": \"$repo\"}" \
        --max-time 300)
    
    if [ $? -eq 0 ]; then
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
        echo ""
    else
        echo "Ошибка при запросе к API"
        echo ""
    fi
    
    sleep 2
done

