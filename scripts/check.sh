#!/bin/bash
# Run all checks before committing

set -e

echo "Running all checks..."
echo "===================="

echo "1. Formatting code..."
make format

echo -e "\n2. Running linting..."
make lint

echo -e "\n3. Running tests..."
make test

echo -e "\nAll checks passed! ✓"