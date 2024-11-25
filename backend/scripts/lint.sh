SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd $SCRIPT_DIR
cd ..

run_mypy_check() {
    echo "Running mypy check..."
    git ls-files "*.py" | xargs mypy
}

run_pylint_check() {
    echo "Running pylint check..."
    git ls-files "*.py" | xargs pylint
}

run_mypy_check
run_pylint_check