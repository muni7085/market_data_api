SCRIPT_DIR=$(dirname "$(realpath "$0")")
cd $SCRIPT_DIR
cd ..
echo "Current script parent path: $(pwd)"


echo "Running mypy check..."
mypy $(git ls-files "*.py")

echo $(pwd)
echo "Running pylint check..."
pylint $(git ls-files "*.py")