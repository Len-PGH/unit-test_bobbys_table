@echo off
echo Setting up environment and running tests...

:: Set environment variables
set HTTP_USERNAME=admin
set HTTP_PASSWORD=secret

:: Install requirements if not already installed
pip install -r requirements.txt

:: Create a log file
echo Test Run Log > test_run.log
echo Timestamp: %date% %time% >> test_run.log
echo. >> test_run.log

:: Run the tests with HTML report and capture output
python -m pytest tests/ -v --html=test_report.html --self-contained-html --log-cli-level=DEBUG --capture=tee-sys >> test_run.log 2>&1

:: Generate custom report
python generate_report.py

:: Keep the window open if there are any errors
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Tests failed with error code %ERRORLEVEL%
    echo See test_run.log for details
    pause
) else (
    echo.
    echo Test report generated: custom_test_report.html
    echo Log file generated: test_run.log
    start custom_test_report.html
    start test_run.log
) 