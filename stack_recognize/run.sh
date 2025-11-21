#!/bin/bash
# Скрипт для запуска анализатора технологического стека

cd "$(dirname "$0")/.."
PYTHONPATH="$(pwd)" python3 -m stack_recognize.main

