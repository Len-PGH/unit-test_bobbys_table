import os
import datetime
import json
import html
from jinja2 import Template
from bs4 import BeautifulSoup

def generate_custom_report(html_report_path, log_file_path):
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure the templates directory exists
    templates_dir = os.path.join(script_dir, 'templates')
    if not os.path.exists(templates_dir):
        raise FileNotFoundError(f"Templates directory not found at {templates_dir}")
    
    # Read the log file
    try:
        with open(log_file_path, 'r') as f:
            log_content = f.read()
    except FileNotFoundError:
        print(f"Warning: Log file not found at {log_file_path}")
        log_content = "Log file not found"
    
    # Read the HTML report to extract test results and summary
    try:
        with open(html_report_path, 'r') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Warning: HTML report not found at {html_report_path}")
        html_content = "<html><body>Test report not found</body></html>"
    
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract summary data
    passed = 0
    failed = 0
    total = 0
    duration = "N/A"
    
    summary_div = soup.find('div', class_='summary')
    if summary_div:
        passed_span = summary_div.find('span', class_='passed')
        if passed_span:
            try:
                passed = int(passed_span.text.split()[0])
            except ValueError:
                passed = 0
            
        failed_span = summary_div.find('span', class_='failed')
        if failed_span:
            try:
                failed = int(failed_span.text.split()[0])
            except ValueError:
                failed = 0
            
        # Calculate total
        total = passed + failed
            
        # Extract duration from the run count paragraph
        run_count_p = summary_div.find('p', class_='run-count')
        if run_count_p:
            parts = run_count_p.text.split('took')
            if len(parts) > 1:
                duration = parts[1].strip().split(' ')[0]
                
    # Extract JSON data from the script tag
    json_data_script = soup.find('div', id='data-container')
    test_results_data = [] # Store detailed test results here
    if json_data_script and 'data-jsonblob' in json_data_script.attrs:
        try:
            # The data is HTML-escaped, so we need to unescape it first
            json_string = html.unescape(json_data_script['data-jsonblob'])
            test_data = json.loads(json_string)
            if 'tests' in test_data:
                for test_id, results in test_data['tests'].items():
                    for result_entry in results:
                        test_results_data.append({
                            'testId': result_entry.get('testId', 'N/A'),
                            'result': result_entry.get('result', 'Unknown').lower(),
                            'duration': result_entry.get('duration', 'N/A'),
                            'log': result_entry.get('log', ''),
                            'extras': result_entry.get('extras', []) # Keep extras as they might contain messages
                        })
        except (KeyError, json.JSONDecodeError, AttributeError) as e:
            print(f"Warning: Error parsing test data: {str(e)}")
            test_results_data = []
            
    # Read the template
    template_path = os.path.join(templates_dir, 'report_template.html')
    try:
        with open(template_path, 'r') as f:
            template = Template(f.read())
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found at {template_path}")
    
    # Generate the custom report
    custom_html = template.render(
        timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        passed=passed,
        failed=failed,
        total=total,
        duration=duration,
        test_results=test_results_data, # Pass the list of detailed test results
        log_content=log_content
    )
    
    # Write the custom report
    output_path = os.path.join(script_dir, 'custom_test_report.html')
    with open(output_path, 'w') as f:
        f.write(custom_html)
    
    print(f"Custom test report generated: {output_path}")

if __name__ == "__main__":
    try:
        generate_custom_report('test_report.html', 'test_run.log')
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        exit(1) 