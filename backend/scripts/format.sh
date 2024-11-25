#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd "$SCRIPT_DIR" || exit 1
cd .. || exit 1

format_files() {
    git ls-files "*.py" | xargs black "$@"
    git ls-files "*.py" | xargs isort --profile black "$@"
}

check_format() {
    format_files --check
}

reformat() {
    format_files
}

if [ "$1" == "--check" ]; then
    check_format
else
    reformat
fi