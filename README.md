# Test Environment

This is an isolated test environment for the SignalWire Reservation System.

## Setup

1. Navigate to this directory
2. Create a virtual environment:
   ```ash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: .\venv\Scripts\activate
   - Linux/macOS: source venv/bin/activate
4. Install requirements:
   ```ash
   pip install -r requirements.txt
   ```

## Running Tests

### Windows
`powershell
.\run_tests.bat
`

### Linux/macOS

```
chmod +x run_tests.sh
./run_tests.sh
```

## Test Output

- Test results: custom_test_report.html
- Log file: 	est_run.log

## Project Structure

- app_new.py - Main application file
- swaig.py - SWAIG integration
- swaig_handler.py - SWAIG request handler
- 
reservation_system.py - Core reservation system
- 	tests/ - Test files
- 	templates/ - HTML templates
