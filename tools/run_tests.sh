#!/usr/bin/env bash
set -euo pipefail

# navigate to repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

# run with pytest if available, otherwise fallback to standard library unittest
if command -v pytest >/dev/null 2>&1; then
    echo "Running tests with pytest..."
    pytest "$@"
elif python3 -m pytest --version >/dev/null 2>&1; then
    echo "Running tests with python3 -m pytest..."
    python3 -m pytest "$@"
else
    echo "Running tests with python3 -m unittest..."
    python3 -m unittest discover tests "$@"
fi
