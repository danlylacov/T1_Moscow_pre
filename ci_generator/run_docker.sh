docker build -t ci-generator:latest .
docker run --rm -p 8000:8000 ci-generator:latest