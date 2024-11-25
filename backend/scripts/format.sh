#!/bin/bash

SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd $SCRIPT_DIR
cd ..

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