#!/bin/bash
# Format all Python code

set -e

echo "Formatting Python code..."
echo "========================"

echo "1. Running black..."
black .

echo -e "\n2. Sorting imports with isort..."
isort .

echo -e "\n3. Auto-fixing with ruff..."
ruff check --fix .

echo -e "\nFormatting complete! ✓"