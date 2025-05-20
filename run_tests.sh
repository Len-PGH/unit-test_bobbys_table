#!/bin/bash

# Function to handle script exit
cleanup() {
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Deactivating virtual environment..."
        deactivate
    fi
    exit $1
}

# Set up trap to handle script exit
trap cleanup EXIT

echo "Setting up environment and running tests..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Get the full path to Python in the virtual environment
VENV_PYTHON="$VIRTUAL_ENV/bin/python"

# Upgrade pip first
echo "Upgrading pip..."
"$VENV_PYTHON" -m pip install --upgrade pip

# Install required packages
echo "Installing required packages..."
"$VENV_PYTHON" -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install required packages"
    exit 1
fi

# Verify pytest is installed
echo "Verifying pytest installation..."
"$VENV_PYTHON" -m pytest --version
if [ $? -ne 0 ]; then
    echo "Error: pytest is not properly installed"
    exit 1
fi

# Set required environment variables for testing
echo "Setting up test environment variables..."
export HTTP_USERNAME="admin"
export HTTP_PASSWORD="secret"
export SIGNALWIRE_PROJECT_ID="test_project"
export SIGNALWIRE_TOKEN="test_token"
export SIGNALWIRE_SPACE="test_space"

# Run tests, generate standard html report, and capture output to log file
echo "Running tests..."
"$VENV_PYTHON" -m pytest -v tests/test_reservation_system.py tests/test_swaig_simulation.py --html=test_report.html --self-contained-html > test_run.log 2>&1

# Capture the exit code of the pytest command
TEST_EXIT_CODE=$?

# Run the custom report generator script
echo "Generating custom test report..."
"$VENV_PYTHON" generate_report.py

# Check the exit code and provide feedback
if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo "Tests failed with exit code $TEST_EXIT_CODE."
    echo "Please check test_run.log for details."
else
    echo "Tests passed successfully."
    echo "Custom test report generated: custom_test_report.html"
    echo "Log file generated: test_run.log"
fi

# The cleanup function will handle deactivating the virtual environment
exit $TEST_EXIT_CODE 