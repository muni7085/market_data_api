SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd $SCRIPT_DIR
cd ..
echo "Current script parent path: $(pwd)"

black $(git ls-files "*.py")
isort --profile black $(git ls-files "*.py")